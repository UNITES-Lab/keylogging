#include "../lib/l3pp.h"
#include "../lib/constants.h"
#include "../lib/eviction.h"
#include <stdio.h>

uint8_t probe(EvictionSet *es, int threshold) {
  CacheLine *iter = es->head;
  for (int i = 0; i < es->size; i++) {
    uint64_t time = time_load((uint8_t *)iter);
    if (time > threshold) {
      return 1;
    }
    iter = iter->next;
  }
  return 0;
}

uint64_t prime_probe(EvictionSet *es, uint8_t associativity, uint8_t *hit_times,
                     uint64_t numBytes, uint64_t *detect_timestamps,
                     int threshold) {
  // TODO: numBytes * 8 to store data efficiently
  unsigned int core_id = 0;

  int times[associativity];
  for (int i = 0; i < numBytes; i++)
    hit_times[i] = 0;

  for (int i = 0; i < associativity; i++) {
    times[i] = 0;
  }

  access_set(es);

  int prev = 0;
  uint64_t hit_count = 0;
  for (int i = 0; i < numBytes; i++) {
    hit_times[i] = probe(es, threshold);
    if (hit_times[i] == 1 && prev == 1) {
      hit_times[i] = 0; // filtering out duplicate detections
      prev = 1;
    } else if (hit_times[i] == 1) {
      detect_timestamps[hit_count] =
          __rdtscp(&core_id); // get timestamp for the detection
      hit_count++;
      prev = 1;
    } else {
      prev = 0;
    }
  }
  return hit_count;
}

uint64_t *prime_probe_many_sets(
    EvictionSet **eslist, uint8_t num_sets, uint8_t associativity,
    uint64_t numProbes, uint8_t probe_results[num_sets][numProbes],
    uint64_t hit_storage_size,
    uint64_t detect_timestamps[num_sets][hit_storage_size], int threshold) {
  unsigned int core_id = 0;
  int times[associativity];
  for (int i = 0; i < associativity; i++) {
    times[i] = 0;
  }

  int prev[num_sets];
  uint64_t *hit_count = malloc(num_sets * sizeof(uint64_t));
  for (int i = 0; i < num_sets; i++) {
    prev[i] = 0;
    hit_count[i] = 0;
  }

  for (int i = 0; i < num_sets; i++) {
    access_set(eslist[i]);
  }

  for (int i = 0; i < numProbes; i++) {
    for (int j = 0; j < 4; j++) {
      probe_results[j][i] = probe(eslist[j], threshold);
      if (probe_results[j][i] == 1 && prev[j] == 1) {
        probe_results[j][i] = 0;
        prev[j] = 1;
      } else if (probe_results[j][i] == 1) {
        detect_timestamps[j][hit_count[j]] = __rdtscp(&core_id);
        hit_count[j]++;
        prev[j] = 1;
      } else {
        prev[j] = 0;
      }
    }
  }
  return hit_count;
}

void filter_pp_results(uint8_t *results, uint64_t numBytes) {
  int prev = 0;
  for (int i = 0; i < numBytes; i++) {
    if (prev == 1 && results[i] == 1) {
      prev = 1;
      results[i] = 0;
    } else {
      prev = results[i];
    }
  }
}

void print_probe_result(uint8_t *results, uint64_t numBytes, uint64_t width,
                        uint64_t height) {
  for (int i = 0; i < height; i++) {
    for (int j = 0; j < width; j++) {
      printf("%d", results[numBytes - width * height + i * width + j]);
    }
    printf("\n");
  }
}

void flush_timestamps(uint64_t *timestamps, int size, char *filePath) {
  FILE *file = fopen(filePath, "ab");
  fwrite(timestamps, sizeof(uint64_t), size, file);
  fflush(file);
  fclose(file);
}

uint16_t get_slice_hit_count(uint8_t *results, uint64_t numBytes,
                             uint64_t width, uint64_t height) {
  uint16_t count = 0;
  for (int i = 0; i < height; i++) {
    for (int j = 0; j < width; j++) {
      count += results[numBytes - width * height + i * width + j];
    }
  }
  return count;
}

CacheLineSet *hugepage_inflate(void *mmap_start, int size, int set) {
  CacheLineSet *cl_set = new_cl_set();
  for (int i = 0; i < size; i++) {
    CacheLine *line =
        (CacheLine *)(mmap_start + (set << LINE_OFFSET_BITS) +
                      ((1 << EVERGLADES_CACHE_SET_BITS) << LINE_OFFSET_BITS) *
                          i);
    push_cache_line(cl_set, line);
  }
  return cl_set;
}

EvictionSet **get_all_slices_eviction_sets(void *mmap_start, int set) {
  CacheLineSet *cl_set =
      hugepage_inflate(mmap_start, EVERGLADES_ASSOCIATIVITY, set);

  int threshold = threshold_from_flush((uint8_t *)cl_set->cache_lines[0]);

  int i = 0;
  EvictionSet **es_list = malloc(4 * sizeof(EvictionSet *));
  for (int i = 0; i < 4; i++) {
    es_list[i] = malloc(sizeof(EvictionSet));
  }
  while (i < cl_set->size) {
    if (i >= EVERGLADES_NUM_SLICES) {
      printf("finding sets for all slices failed, please retry\n");
      break;
    }

    printf("cl_set size: %d\n", cl_set->size);
    print_cl_set(cl_set);
    CacheLineSet *cl_evset;
    if (!get_minimal_set((uint8_t *)cl_set->cache_lines[i], &cl_evset,
                         threshold)) {
      printf("cannot find eviction set for %p\n",
             (void *)cl_set->cache_lines[i]);
      exit(1);
    }
    EvictionSet *es = new_eviction_set(cl_evset);
    NumList *nl = new_num_list(EVERGLADES_ASSOCIATIVITY);
    int size = 0;
    for (int j = i + 1; j < cl_set->size; j++) {
      int count = 0;
      for (int k = 0; k < 10; k++) {
        int time = evict_and_time_once(es, (uint8_t *)cl_set->cache_lines[j]);
        if (time < threshold)
          count++;
      }
      if (count > 6) {
        push_num(nl, j);
        size++;
      }
    }
    print_num_list(nl);

    CacheLine *new_cache_lines[i + 1 + nl->length];

    for (int j = 0; j < i + 1; j++) {
      new_cache_lines[j] = cl_set->cache_lines[j];
    }

    for (int j = 0; j < nl->length; j++) {
      new_cache_lines[i + j + 1] = cl_set->cache_lines[nl->nums[j]];
    }

    for (int j = 0; j < i + 1 + nl->length; j++) {
      cl_set->cache_lines[j] = new_cache_lines[j];
    }

    cl_set->size = i + 1 + nl->length;
    es_list[i] = es;
    i++;

    free_num_list(nl);
  }

  print_cl_set(cl_set);
  return es_list;
}

void free_es_list(EvictionSet **es_list) {
  for (int i = 0; i < 4; i++) {
    deep_free_es(es_list[i]);
  }
  free(es_list);
}
