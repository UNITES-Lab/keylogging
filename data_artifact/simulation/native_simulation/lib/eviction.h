#include <stdbool.h>
#include <stdint.h>
#include <time.h>

#include "utils.h"

#ifndef EVICTION_H
#define EVICTION_H

/*********************************************************************
 * Eviction Parameters
 *********************************************************************/

// Initial size of generated eviction sets, before reducing
#define INITIAL_SIZE 8192

//  Number of samples to perform each attack
#define SAMPLES 100

// Initial timing threshold to use (measured with RDTSCP) before measurement
#define INITIAL_THRESHOLD 270

// Number of bins used when reducing with reduce2
#define BINS 64

// Slicing of the last-level cache on 6-core Coffee Lake
#define HIGH_MARK 9 / 10
#define LOW_MARK 1 / 10

// How many bits [6,10] to match between the victim cache set and the cache set
// of new cache lines
#define MATCHING_BITS 6

/*********************************************************************
 * Address Translation
 *********************************************************************/

uintptr_t pointer_to_pa(void *va);
int pa_to_set(uintptr_t pa, int machine);

/*********************************************************************
 * Timing
 *********************************************************************/

uint64_t time_load(volatile uint8_t *victim);
uint64_t threshold_from_flush(uint8_t *victim);

/*********************************************************************
 * Allocation
 *********************************************************************/

// A CacheLine is a contiguous region of memory with pointers to other
// CacheLines
typedef struct CacheLine CacheLine;
struct CacheLine {
  CacheLine *next;
  CacheLine *previous;
};

typedef struct {
  CacheLine **cache_lines;
  int size;
} CacheLineSet;

void print_cache_line(CacheLine *cl);
CacheLine *allocate_cache_line(uint8_t *victim);
CacheLineSet *new_cl_set(void);
void print_cl_set(CacheLineSet *cl_set);
void push_cache_line(CacheLineSet *cl_set, CacheLine *cl);
void free_cl_set(CacheLineSet *cl_set);
void deep_free_cl_set(CacheLineSet *cl_set);
CacheLine *pop_cache_line(CacheLineSet *cl_set);
CacheLine *remove_cache_line(CacheLineSet *cl_set, int index);
void shuffle_lines(CacheLineSet *cl_set);
CacheLineSet *inflate(uint8_t *victim, int max_size, int samples,
                      uint64_t threshold);

/*********************************************************************
 * Eviction
 *********************************************************************/

// An EvictionSet is just an intrusive linked list of CacheLines
typedef struct {
  CacheLineSet *cache_lines;
  CacheLine *head;
  CacheLine *tail;
  int size;
} EvictionSet;

extern bool attack_finished;

void print_eviction_set(CacheLineSet *cl_set);
EvictionSet *new_eviction_set(CacheLineSet *cl_set);
void deep_free_es(EvictionSet *es);
void access_set(EvictionSet *es);
void *access_loop(void *in);
uint64_t evict_and_time_once(EvictionSet *es, uint8_t *victim);
uint64_t evict_and_time(CacheLineSet *cl_set, uint8_t *victim, NumList *timings,
                        bool use_siblings);
bool reduce2(CacheLineSet *cl_set, CacheLineSet *reserve, uint8_t *victim,
             int samples, uint64_t threshold, int bins);
EvictionSet *generate_set(uint8_t *victim);
uint64_t threshold_from_evict(CacheLineSet *cl_set, uint8_t *victim);

/*********************************************************************
 * Prime+Probe
 *********************************************************************/

bool get_minimal_set(uint8_t *victim, CacheLineSet **cl_set,
                     uint64_t threshold);
int same_cache_set(uint8_t *cl1, uint8_t *cl2, CacheLineSet *cl_set,
                   uint64_t threshold);
int evict_time_multi(CacheLineSet *cl_set, uint8_t *victim, uint64_t threshold,
                     bool use_siblings);

CacheLineSet **generate_sets(int num_sets, uint8_t *victim_page_offset);
NumList *do_probe(CacheLineSet *cl_set, uint64_t probe_time);
int which_set(NumList **results, NumList *known_trace);

#endif
