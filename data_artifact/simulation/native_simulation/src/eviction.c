#define _GNU_SOURCE
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <x86intrin.h>

#include "../lib/address_translation.h"
#include "../lib/constants.h"
#include "../lib/eviction.h"
#include "../lib/utils.h"

/*********************************************************************
 * Global Variables
 *********************************************************************/

// Setting this to true tells access_loop to stop (when running in a separate
// thread)
bool attack_finished = false;

/*********************************************************************
 * Address Translation
 *
 * These functions are only used to print physical addresses and cache
 * sets. They are not used to generate eviction sets.
 *
 *********************************************************************/

// Translate virtual address to physical addresses by reading the page map
uintptr_t pointer_to_pa(void *va) {
  uintptr_t pa = 0;

  if (virt_to_phys_user(&pa, getpid(), (uintptr_t)va)) {
    fprintf(stderr, "error: virt_to_phys_user\n");
    return -1;
  };

  return pa;
}

// Determine the cache set of a physical address by reading bits [6, 16)
int pa_to_set(uintptr_t pa, int machine) {
  if (machine == EVERGLADES)
    return (pa >> LINE_OFFSET_BITS) & ((1 << EVERGLADES_CACHE_SET_BITS) - 1);
  else
    return (pa >> LINE_OFFSET_BITS) & ((1 << ACADIA_CACHE_SET_BITS) - 1);
}

int get_i7_2600_slice(uintptr_t pa) {

  /* Practical Timing Side Channel Attacks Against Kernel Space ASLR */
  // int h2 = get_bit(pa, 31) ^ get_bit(pa, 29) ^ get_bit(pa, 28) ^
  //          get_bit(pa, 26) ^ get_bit(pa, 24) ^ get_bit(pa, 23) ^
  //          get_bit(pa, 22) ^ get_bit(pa, 21) ^ get_bit(pa, 20) ^
  //          get_bit(pa, 19) ^ get_bit(pa, 17);
  // int h1 = get_bit(pa, 31) ^ get_bit(pa, 30) ^ get_bit(pa, 29) ^
  //          get_bit(pa, 27) ^ get_bit(pa, 25) ^ get_bit(pa, 23) ^
  //          get_bit(pa, 21) ^ get_bit(pa, 19) ^ get_bit(pa, 18);

  /* Reverse Engineering Intel Last-Level Cache Complex Addressing Using
   * Performance Counters */

  int h1 = get_bit(pa, 33) ^ get_bit(pa, 32) ^ get_bit(pa, 30) ^
           get_bit(pa, 28) ^ get_bit(pa, 27) ^ get_bit(pa, 26) ^
           get_bit(pa, 25) ^ get_bit(pa, 24) ^ get_bit(pa, 22) ^
           get_bit(pa, 20) ^ get_bit(pa, 18) ^ get_bit(pa, 17) ^
           get_bit(pa, 16) ^ get_bit(pa, 14) ^ get_bit(pa, 12) ^
           get_bit(pa, 10) ^ get_bit(pa, 6);
  int h2 = get_bit(pa, 34) ^ get_bit(pa, 33) ^ get_bit(pa, 31) ^
           get_bit(pa, 29) ^ get_bit(pa, 28) ^ get_bit(pa, 26) ^
           get_bit(pa, 24) ^ get_bit(pa, 23) ^ get_bit(pa, 22) ^
           get_bit(pa, 21) ^ get_bit(pa, 20) ^ get_bit(pa, 19) ^
           get_bit(pa, 17) ^ get_bit(pa, 15) ^ get_bit(pa, 13) ^
           get_bit(pa, 11) ^ get_bit(pa, 7);

  return (h1 << 1) + h2;
}

CacheLine *align_to_page(CacheLine *va) {

  uintptr_t addr = (uintptr_t)va >> PAGE_OFFSET_BITS;
  addr <<= PAGE_OFFSET_BITS;

  // if ((uintptr_t)va != addr)
  // {
  // printf("Tried to free unaligned address!\n");
  // print_cache_line(va);
  // }

  return (CacheLine *)addr;
}

CacheLine *align_to_victim(CacheLine *va, uint8_t *victim) {
  uintptr_t cache_set_bits = HALF_CACHE_SET((uintptr_t)victim);
  uintptr_t aligned = (uintptr_t)va | cache_set_bits;

  return (CacheLine *)aligned;
}

/*********************************************************************
 * Timing
 *********************************************************************/

// Times a memory access to the given byte pointer
uint64_t time_load(volatile uint8_t *victim) {
  int core_id = 0;
  _mm_mfence();
  uint64_t t0 = __rdtscp(&core_id);
  _mm_lfence();
  volatile uint8_t x = *victim;
  uint64_t t1 = __rdtscp(&core_id);
  _mm_lfence();

  return t1 - t0;
}

// Calculates the cache hit threshold by timing a memory access both with and
// without evicting it. If cl_set isn't an eviction set for victim, this won't
// work.
uint64_t threshold_from_evict(CacheLineSet *cl_set, uint8_t *victim) {
  CacheLineSet *empty_set = new_cl_set();
  NumList *timings = new_num_list(SAMPLES);
  // Accessing an empty eviction set should leave victim cached
  uint64_t t_cached = evict_and_time(empty_set, victim, timings, false);
  free_cl_set(empty_set);
  free_num_list(timings);
  // Accessing a real eviction set should force victim out of the cache
  NumList *timings2 = new_num_list(SAMPLES);
  uint64_t t_evicted = evict_and_time(cl_set, victim, timings2, true);
  free_num_list(timings2);
  uint64_t threshold = (t_cached + t_evicted) / 2;

  if (threshold < 90 || threshold > 150) {
    return threshold_from_evict(cl_set, victim);
  }

#ifndef __MEASURE__
  printf("Calculated threshold of %lu with Evict+Reload.\n", threshold);
#endif

  return threshold;
}

// Calculates the cache hit threshold by timing a memory access both with and
// without flushing it.
uint64_t threshold_from_flush(uint8_t *victim) {
  NumList *timings = new_num_list(SAMPLES);

  for (int i = 0; i < SAMPLES; i++) {
    volatile uint8_t x = *victim;
    push_num(timings, time_load(victim));
  }

  uint64_t t_cached = median_and_sort(timings);
  clear_num_list(timings);

  for (int i = 0; i < SAMPLES; i++) {
    _mm_clflush(victim);
    push_num(timings, time_load(victim));
  }

  uint64_t t_flushed = median_and_sort(timings);

  uint64_t threshold = (t_cached + t_flushed) / 2;

#ifndef __MEASURE__
  printf("Calculated threshold of %lu with Flush+Reload.\n", threshold);
#endif

  // assert(threshold > 90 && threshold < 150);

  return threshold;
}

/*********************************************************************
 * Allocation
 *********************************************************************/

void print_cache_line(CacheLine *cl) {
  printf("%12p => ", cl);
  printf("0x%013lx ", pointer_to_pa(cl));
  printf("{ %u }\n", pa_to_set(pointer_to_pa(cl), EVERGLADES));
}

// Allocate an aligned page and initialize it
CacheLine *allocate_cache_line(uint8_t *victim) {
  void *new_page = aligned_alloc(PAGE_BYTES, PAGE_BYTES);
  memset(new_page, 0xFF, PAGE_BYTES);

  return align_to_victim((CacheLine *)new_page, victim);
}

CacheLineSet *new_cl_set(void) {
  CacheLineSet *cl_set = malloc(sizeof(CacheLineSet));
  cl_set->cache_lines = NULL;
  cl_set->size = 0;

  return cl_set;
}

void push_cache_line(CacheLineSet *cl_set, CacheLine *cl) {
  cl_set->size++;
  cl_set->cache_lines =
      reallocarray(cl_set->cache_lines, cl_set->size, sizeof(CacheLine));
  cl_set->cache_lines[cl_set->size - 1] = cl;
}

// Free a cache line set without freeing the individual cache lines
void free_cl_set(CacheLineSet *cl_set) {
  if (cl_set->size > 0) {
    free(cl_set->cache_lines);
  }

  free(cl_set);
}

// Free a cache line set and the individual cache lines
void deep_free_cl_set(CacheLineSet *cl_set) {
  if (cl_set->size > 0) {
    for (int i = 0; i < cl_set->size; i++) {
      CacheLine *page_aligned = align_to_page(cl_set->cache_lines[i]);
      free(page_aligned);
    }
    free(cl_set->cache_lines);
  }
  free(cl_set);
}

void print_cl_set(CacheLineSet *cl_set) {
  for (int i = 0; i < cl_set->size; i++) {
    printf("%p\n", (void *)cl_set->cache_lines[i]);
  }
}

// Remove the last cache line from the set of cache lines and return it
CacheLine *pop_cache_line(CacheLineSet *cl_set) {
  // Get last CacheLine from CacheLineSet and resize list
  CacheLine *cl = cl_set->cache_lines[cl_set->size - 1];
  cl_set->size--;
  cl_set->cache_lines =
      reallocarray(cl_set->cache_lines, cl_set->size, sizeof(CacheLine));
  return cl;
}

// Remove the cache line at the given index and return it
CacheLine *remove_cache_line(CacheLineSet *cl_set, int index) {
  if (index < 0 || index >= cl_set->size) {
    printf("Invalid index into CacheLineSet: %u for size %u\n", index,
           cl_set->size);
    return NULL;
  }
  CacheLine *removed = cl_set->cache_lines[index];

  // Copy cache lines over to new location
  CacheLine **new_cache_lines = calloc(cl_set->size - 1, sizeof(CacheLine *));

  for (int i = 0; i < index; i++) {
    new_cache_lines[i] = cl_set->cache_lines[i];
  }

  for (int i = index + 1; i < cl_set->size; i++) {
    new_cache_lines[i - 1] = cl_set->cache_lines[i];
  }

  cl_set->size--;
  free(cl_set->cache_lines);
  cl_set->cache_lines = new_cache_lines;

  return removed;
}

// Randomly shuffle a set of cache lines in place
void shuffle_lines(CacheLineSet *cl_set) {
  for (int i = 0; i < cl_set->size - 1; i++) {
    int j = (rand() % (cl_set->size - i)) + i;
    CacheLine **temp = malloc(sizeof(CacheLine *));
    memcpy(temp, &(cl_set->cache_lines[i]), sizeof(CacheLine *));
    memcpy(&(cl_set->cache_lines[i]), &(cl_set->cache_lines[j]),
           sizeof(CacheLine *));
    memcpy(&(cl_set->cache_lines[j]), temp, sizeof(CacheLine *));
    free(temp);
  }
}

// Generate an eviction set (CacheLineSet) for the victim, of at most max_size
CacheLineSet *inflate(uint8_t *victim, int max_size, int samples,
                      uint64_t threshold) {
  CacheLineSet *cl_set = new_cl_set();

  while (cl_set->size < max_size) {
    // Double the size of the cache line set, starting at 16
    int current_size = cl_set->size;
    for (int i = current_size; i < MAX(2 * current_size, 16); i++) {
      push_cache_line(cl_set, allocate_cache_line(victim));
    }

    int strikes = 0;

    // Check if it's an eviction set
    for (int i = 0; i < 5; i++) {
      NumList *timings = new_num_list(samples);
      uint64_t timing = evict_and_time(cl_set, victim, timings, false);

      if (timing >= threshold) {
        strikes++;
      }
      free_num_list(timings);
    }

    // If it is, break and return the set
    if (strikes >= 5) {
      break;
    }
  }

#ifndef __MEASURE__
  printf("Generated initial eviction set of size %u.\n", cl_set->size);
#endif

  return cl_set;
}

/*********************************************************************
 * Eviction
 *********************************************************************/

void print_eviction_set(CacheLineSet *cl_set) {
  for (int i = 0; i < cl_set->size; i++) {
    print_cache_line(cl_set->cache_lines[i]);
  }
}

// Construct an intrusive linked list from each cache line in the set
EvictionSet *new_eviction_set(CacheLineSet *cl_set) {
  CacheLine *head = NULL;
  CacheLine *tail = NULL;

  for (int i = 0; i < cl_set->size; i++) {
    if (cl_set->size == 1) {
      head = tail = cl_set->cache_lines[i];
      head->next = NULL;
      tail->previous = NULL;
    } else if (i == 0) {
      head = cl_set->cache_lines[i];
      head->next = cl_set->cache_lines[i + 1];
      head->previous = NULL;
    } else if (i == cl_set->size - 1) {
      tail = cl_set->cache_lines[i];
      tail->next = NULL;
      tail->previous = cl_set->cache_lines[i - 1];
    } else {
      cl_set->cache_lines[i]->next = cl_set->cache_lines[i + 1];
      cl_set->cache_lines[i]->previous = cl_set->cache_lines[i - 1];
    }
  }

  EvictionSet *es = malloc(sizeof(EvictionSet));
  es->cache_lines = cl_set;
  es->head = head;
  es->tail = tail;
  es->size = cl_set->size;

  return es;
}

// Free an eviction set, freeing each of its cache lines
void deep_free_es(EvictionSet *es) {
  deep_free_cl_set(es->cache_lines);
  free(es);
}

// Access each of the cache lines in an eviction set
void access_set(EvictionSet *es) {

  if (es->size < 8) {
    return;
  }

  // Perform access pattern twice
  for (int i = 0; i < 2; i++) {
    CacheLine *iter = es->head;
    CacheLine *lagging_iter = es->head;

    // Forwards dual-chasing over the linked list of cache lines
    // lagging_iter lags 8 cache lines behind iter
    for (int j = 0; j < 8; j++) {
      iter = iter->next;
    }

    for (int j = 0; j < es->size; j++) {
      if (j < es->size - 8) {
        iter = iter->next;
      }
      lagging_iter = lagging_iter->next;
    }

    // Repeat the same pattern but in reverse
    iter = es->tail;
    lagging_iter = es->tail;

    for (int j = 0; j < 8; j++) {
      iter = iter->previous;
    }

    for (int j = 0; j < es->size; j++) {
      if (j < es->size - 8) {
        iter = iter->previous;
      }
      lagging_iter = lagging_iter->previous;
    }
  }
}

// Access an eviction set repeatedly until attack_finished is set
void *access_loop(void *in) {

  EvictionSet *es = (EvictionSet *)in;

#ifndef __MEASURE__
  printf("Evicting victim...\n");
  printf("Eviction set is of size %u.\n", es->size);
#endif

  while (!attack_finished) {
    access_set(es);
  }

  return NULL;
}

// Evict the victim and time the access
uint64_t evict_and_time_once(EvictionSet *es, uint8_t *victim) {
  volatile uint8_t x = *victim;
  access_set(es);
  return time_load(victim);
}

// Repeatedly evict the victim and time the access, returning the median timing
uint64_t evict_and_time(CacheLineSet *cl_set, uint8_t *victim, NumList *timings,
                        bool use_siblings) {
  // Construct new set of cache lines
  CacheLineSet *second = new_cl_set();

  for (int i = 0; i < cl_set->size; i++) {
    CacheLine *cl = cl_set->cache_lines[i];
    push_cache_line(second, cl);

    // It includes all old cache lines, as well as the immediately
    // preceding/subsequent (sibling) lines
    if (use_siblings) {
      CacheLine *sibling = (CacheLine *)(((uintptr_t)cl) ^ 0x40);
      push_cache_line(second, sibling);
    }
  }

  // Randomly shuffle cache lines, generate eviction set, and time the victim
  for (int i = 0; i < timings->capacity; i++) {
    shuffle_lines(second);
    EvictionSet *es = new_eviction_set(second);
    push_num(timings, evict_and_time_once(es, victim));
    free(es);
  }

  free_cl_set(second);

  return median_and_sort(timings);
}

// Reduce an eviction set to its minimal subset
bool reduce2(CacheLineSet *cl_set, CacheLineSet *reserve, uint8_t *victim,
             int samples, uint64_t threshold, int bins) {
  // Stores removed cache lines in case they need to be added back
  // CacheLineSet *reserve = new_cl_set();
  int strikes = 0;

  int failures = 0;

  // Continue until we fail to reduce 5 times in a row, while the working set is
  // an eviction set
  while (strikes < 5) {
    // Split the eviction set into many bins of equal (except for potentially
    // the last one) size. Leave each of these bins out, considering the
    // remainder as an eviction set and measuring its performance.
    int step_size = MAX(cl_set->size / bins, 1);
    NumList *starts = new_num_list((step_size == 1) ? cl_set->size : bins);
    for (int i = 0; i < cl_set->size; i += step_size) {
      push_num(starts, i);
    }
    NumList *ends = new_num_list(starts->length);
    for (int i = 0; i < ends->capacity - 1; i++) {
      push_num(ends, starts->nums[i + 1]);
    }
    push_num(ends, cl_set->size);

    RangeList *best_ranges = new_range_list();

    // Iterate through all bins to see which ones are fine to leave out
    for (int i = 0; i < starts->length; i++) {
      if (cl_set->size == INITIAL_SIZE && i % (starts->length / 8) == 0) {
#ifndef __MEASURE__
        // printf("%u/%u\n", i, starts->length);
#endif
      }
      int start = starts->nums[i];
      int end = ends->nums[i];

      Range *r = new_range(start, end);
      CacheLineSet *set = new_cl_set();

      for (int j = 0; j < cl_set->size; j++) {
        CacheLine *cl = cl_set->cache_lines[j];
        // Skip past all cache lines in the range
        if (range_contains(r, j)) {
          continue;
        }

        // Skip cache lines which were previously left out without degrading
        // performance
        bool found = false;
        for (int k = 0; k < best_ranges->length; k++) {
          if (range_contains(best_ranges->ranges[k], j)) {
            found = true;
          }
        }

        if (found) {
          continue;
        }

        push_cache_line(set, cl);
      }

      int strikes2 = 0;

      for (int j = 0; j < 3; j++) {
        NumList *timings = new_num_list(samples);
        uint64_t timing = evict_and_time(set, victim, timings, false);

        if (timing >= threshold) {
          strikes2++;
        }
        free_num_list(timings);
      }

      // If the smaller set doesn't evict 3/3 times, move on
      if (strikes2 < 3) {
        free(r);
        continue;
      }

      // If the smaller set evicts 3/3 times, save the range
      push_range(best_ranges, r);
    }

    free_num_list(starts);
    free_num_list(ends);

    // If no range could be left out, add a strike
    if (best_ranges->length == 0) {
      strikes++;
    }
    // If some ranges could be left out, remove all cache lines in those ranges,
    // saving them in reserve
    else {
      strikes = 0;
      for (int i = best_ranges->length - 1; i >= 0; i--) {
        Range *best_range = best_ranges->ranges[i];

        for (int j = best_range->high - 1; j >= best_range->low; j--) {
          push_cache_line(reserve, remove_cache_line(cl_set, j));
        }
      }
#ifndef __MEASURE__
      // printf("Attempting to reduce to size %u...\n", cl_set->size);
#endif
    }

    int strikes2 = 0;

    // Test if current working set is an eviction set
    for (int i = 0; i < 5; i++) {
      NumList *timings = new_num_list(samples);
      uint64_t timing = evict_and_time(cl_set, victim, timings, false);

      if (timing >= threshold) {
        strikes2++;
      }
      free_num_list(timings);
    }

    if (strikes2 >= 5) {
#ifndef __MEASURE__
      // printf("Success! Reduced eviction set to size %u.\n", cl_set->size);
#endif
      continue;
    }

#ifndef __MEASURE__
    failures++;
    if (failures >= 10) {
      printf("Failed to reduce. Generating new initial set.\n");
      return false;
    }
#endif

    // If it wasn't, add back cache lines from reserve
    while (true) {
      // Add back all cache lines which were removed
      shuffle_lines(reserve);

      while (reserve->size > 0) {
        push_cache_line(cl_set, pop_cache_line(reserve));
      }

      int strikes2 = 0;

      // Test if the working set is an eviction set
      for (int i = 0; i < 5; i++) {
        NumList *timings = new_num_list(samples);
        uint64_t timing = evict_and_time(cl_set, victim, timings, false);

        if (timing >= threshold) {
          strikes2++;
        }
        free_num_list(timings);
      }

      if (strikes2 >= 5) {
        break;
      }
    }

#ifndef __MEASURE__
    // printf("Added back lines. Set now has size %u.\n", cl_set->size);
#endif
  }
  // Successfully reduced
  return true;
}

// Generate a minimal eviction set for a victim
EvictionSet *generate_set(uint8_t *victim) {
// Generate initial large eviction set
#ifndef __MEASURE__
  printf("Generating initial eviction set...\n");
#endif
  CacheLineSet *cl_set =
      inflate(victim, INITIAL_SIZE, SAMPLES, INITIAL_THRESHOLD);
#ifndef __MEASURE__
  printf("\n");
#endif

  // Calculate cache hit threshold from cached and evicted times
  uint64_t threshold = threshold_from_evict(cl_set, victim);
#ifndef __MEASURE__
  printf("\n");
#endif

// Reduce to minimal eviction set
#ifndef __MEASURE__
  printf("Beginning reduction...\n");
#endif

  CacheLineSet *reserve = new_cl_set();
  bool result = reduce2(cl_set, reserve, victim, SAMPLES, threshold, BINS);
  deep_free_cl_set(reserve);

  // Measure how often the minimal set evicts the victim
  int count = 0;
  for (int i = 0; i < SAMPLES; i++) {
    NumList *timings = new_num_list(SAMPLES);
    uint64_t t = evict_and_time(cl_set, victim, timings, false);
    if (t >= threshold) {
      count++;
    }
    free_num_list(timings);
  }

#ifndef __MEASURE__
  printf("Final eviction rate: %u/%u\n", count, SAMPLES);
  printf("\n");

  printf("Minimal eviction set: (VA => PA { Cache Set })\n");
  print_eviction_set(cl_set);
#endif

  return new_eviction_set(cl_set);
}

/*********************************************************************
 * Prime+Probe
 *********************************************************************/

// Returns a minimal eviction set for the victim, using a pre-computed eviction
// threshold
bool get_minimal_set(uint8_t *victim, CacheLineSet **cl_set,
                     uint64_t threshold) {
  *cl_set = inflate(victim, INITIAL_SIZE, SAMPLES, INITIAL_THRESHOLD);
  CacheLineSet *reserve = new_cl_set();

  int tries = 0;

  while (!reduce2(*cl_set, reserve, victim, SAMPLES, threshold, BINS)) {
    if (tries > 2) {
      return false;
    }

    deep_free_cl_set(*cl_set);
    *cl_set = inflate(victim, INITIAL_SIZE, SAMPLES, INITIAL_THRESHOLD);
    deep_free_cl_set(reserve);
    reserve = new_cl_set();
    tries++;
  }
  printf("Successfully reduced to size %u.\n", (*cl_set)->size);
  deep_free_cl_set(reserve);

  return true;
}

int evict_time_multi(CacheLineSet *cl_set, uint8_t *victim, uint64_t threshold,
                     bool use_siblings) {
  int count = 0;
  for (int i = 0; i < SAMPLES; i++) {
    NumList *timings = new_num_list(SAMPLES);
    uint64_t t = evict_and_time(cl_set, victim, timings, use_siblings);
    if (t >= threshold) {
      count++;
    }
    free_num_list(timings);
  }

  return count;
}

int same_cache_set(uint8_t *cl1, uint8_t *cl2, CacheLineSet *cl_set,
                   uint64_t threshold) {
  int count1 = evict_time_multi(cl_set, cl1, threshold, true);
  int count2 = evict_time_multi(cl_set, cl2, threshold, true);

  // printf("Control eviction rate: %u/%u for ", count1, SAMPLES);
  // print_cache_line((CacheLine *)cl1);
  // printf("New line eviction rate: %u/%u for ", count2, SAMPLES);
  // print_cache_line((CacheLine *)cl2);

  if (count1 > SAMPLES * HIGH_MARK && count2 < SAMPLES * LOW_MARK) {
    // printf("Different cache set, slice, or sub-slice.\n");
    return 0;
  } else if (count1 > SAMPLES * HIGH_MARK && count2 > SAMPLES * HIGH_MARK) {
    // printf("Same cache set, slice, and sub-slice!\n");
    return 1;
  } else if (count1 < SAMPLES * HIGH_MARK) {
    // printf("Isn't actually an eviction set.\n");
    return 2;
  } else {
    // printf("Inconclusive...\n");
    return 3;
  }
}

bool match_cache_set(uint8_t *cl1, uint8_t *cl2, int num_bits) {
  int set1 = pa_to_set(pointer_to_pa(cl1), EVERGLADES);
  int set2 = pa_to_set(pointer_to_pa(cl2), EVERGLADES);

  for (int i = 0; i < num_bits; i++) {
    if ((set1 & 1) == (set2 & 1)) {
      set1 >>= 1;
      set2 >>= 1;
    } else {
      return false;
    }
  }

  return true;
}

bool all_same_cache_set(CacheLineSet *cl_set) {
  int set = pa_to_set(pointer_to_pa(cl_set->cache_lines[0]), EVERGLADES);
  for (int i = 1; i < cl_set->size; i++) {
    if (pa_to_set(pointer_to_pa(cl_set->cache_lines[i]), EVERGLADES) != set) {
      return false;
    }
  }

  return true;
}

CacheLine *allocate_matching(uint8_t *victim, int matching_bits) {
  void *new_page = aligned_alloc(PAGE_BYTES, PAGE_BYTES);
  CacheLine *aligned_page = align_to_victim((CacheLine *)new_page, victim);

  CacheLineSet *reserve = new_cl_set();

  while (!match_cache_set((uint8_t *)aligned_page, (uint8_t *)victim,
                          matching_bits)) {
    push_cache_line(reserve, new_page);
    new_page = aligned_alloc(PAGE_BYTES, PAGE_BYTES);
    aligned_page = align_to_victim((CacheLine *)new_page, victim);
  }

  memset(new_page, 0xFF, PAGE_BYTES);

  deep_free_cl_set(reserve);

  return aligned_page;
}

CacheLineSet **generate_sets(int num_sets, uint8_t *victim_page_offset) {
  // Compute eviction threshold
  uint8_t dummy;
  CacheLineSet *initial_set =
      inflate(&dummy, INITIAL_SIZE, SAMPLES, INITIAL_THRESHOLD);
  uint64_t threshold = threshold_from_evict(initial_set, &dummy);

  // Allocate the first cache line
  CacheLineSet *unique_lines = new_cl_set();
  push_cache_line(unique_lines,
                  allocate_matching(victim_page_offset, MATCHING_BITS));

  // Stores a minimal eviction set for each unique cache line we generate
  CacheLineSet **probe_sets = calloc(num_sets, sizeof(CacheLineSet *));
  get_minimal_set((uint8_t *)(unique_lines->cache_lines[0]), &probe_sets[0],
                  threshold);

  // How well each eviction set evicts the victim
  NumList *eviction_rates = new_num_list(num_sets);
  push_num(eviction_rates, evict_time_multi(probe_sets[0], victim_page_offset,
                                            threshold, false));

  // Save physical addresses to makes sure they don't change
  NumList *pas[num_sets];
  for (int i = 0; i < num_sets; i++) {
    pas[i] = new_num_list(ACADIA_ASSOCIATIVITY);
  }

  for (int i = 0; i < probe_sets[0]->size; i++) {
    uintptr_t pa = pointer_to_pa(probe_sets[0]->cache_lines[i]);
    push_num(pas[0], pa);
  }

  uintptr_t victim_pa = pointer_to_pa(victim_page_offset);

  // Keep track of problematic lines
  CacheLineSet *problem_lines = new_cl_set();

  // Continue generating unique cache lines until we have one for every possible
  // cache set
  while (unique_lines->size < num_sets) {

    printf("[ Set %u ]\n", unique_lines->size);

    CacheLine *cl_new = allocate_matching(victim_page_offset, MATCHING_BITS);

    bool unique = true;

    for (int i = 0; i < unique_lines->size; i++) {
      // If the new cache line was in the same cache set as an existing one,
      // move on
      int match = 2;

      while (true) {
        // printf("Testing set %u on new line...\n", i);
        match = same_cache_set((uint8_t *)(unique_lines->cache_lines[i]),
                               (uint8_t *)cl_new, probe_sets[i], threshold);
        if (match != 2 && match != 3) {
          break;
        }
        // If the saved eviction set no longer works, generate another one to
        // stop it from getting stuck
        printf("Critical error: original set stopped evicting.\n");
        return NULL;
      }

      if (match == 1) {
        printf("New cache line %p wasn't unique.\n", cl_new);
        unique = false;
        break;
      }
    }

    // If the new cache line was unique, add it to the list, along with its
    // minimal eviction set
    if (unique) {
      push_cache_line(unique_lines, cl_new);
      printf("Found unique line %u: \n", unique_lines->size - 1);

      print_cache_line(cl_new);
      CacheLineSet **new_cl_set;
      if (!get_minimal_set((uint8_t *)cl_new, new_cl_set, threshold)) {
        printf("Reduction failed repeatedly. Choosing new cache line\n");
        CacheLine *last_cl = pop_cache_line(unique_lines);
        push_cache_line(problem_lines, last_cl);
        deep_free_cl_set(*new_cl_set);
        continue;
      }
      probe_sets[unique_lines->size - 1] = *new_cl_set;

      push_num(eviction_rates, evict_time_multi(*new_cl_set, victim_page_offset,
                                                threshold, false));
      printf("Victim eviction rates for each generated set:\n");
      for (int i = 0; i < eviction_rates->length; i++) {
        printf("Victim eviction rate %u: %lu/%u for set from cache line ", i,
               eviction_rates->nums[i], SAMPLES);
        print_cache_line(unique_lines->cache_lines[i]);
      }

      // Save physical addresses from new eviction set
      for (int i = 0; i < (*new_cl_set)->size; i++) {
        uintptr_t pa = pointer_to_pa((*new_cl_set)->cache_lines[i]);
        push_num(pas[unique_lines->size - 1], (uint64_t)pa);
      }

      // Check that physical addresses didn't change
      for (int i = 0; i < unique_lines->size; i++) {
        // printf("Checking on eviction set %u\n", i);
        for (int j = 0; j < pas[i]->length; j++) {
          uint64_t old_pa = pas[i]->nums[j];
          uint64_t new_pa = pointer_to_pa(probe_sets[i]->cache_lines[j]);
          if (old_pa != new_pa) {
            printf("Set %u element %u old PA: %lx new PA: %lx\n", i, j, old_pa,
                   new_pa);
            printf("pas[%u]->nums[%u]: %lx\n", i, j, pas[i]->nums[j]);

            printf("Error! Physical address changed in set %u from original "
                   "value %lx to %lx.\n",
                   i, old_pa, new_pa);
            printf("Address changed for this cache line: ");
            print_cache_line(probe_sets[i]->cache_lines[j]);
            printf("For set generated from cache line: ");
            print_cache_line(unique_lines->cache_lines[i]);
            return NULL;
          }
        }
      }

      printf("Physical addresses of eviction sets didn't change.\n");

      if (pointer_to_pa(victim_page_offset) != victim_pa) {
        printf("Critical error: victim changed physical address.\n");
        return NULL;
      }
      printf("Victim physical address stayed the same.\n");

      printf("Victim: ");
      print_cache_line((CacheLine *)victim_page_offset);
      printf("\n");
    }
  }

  deep_free_cl_set(problem_lines);

  return probe_sets;
}
