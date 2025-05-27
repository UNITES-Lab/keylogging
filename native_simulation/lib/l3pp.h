#include "eviction.h"
uint8_t probe(EvictionSet *es, int threshold);
/** Prime+Probe until the buffer hit_times is completely filled
 * @param es: eviction set to probe
 * @param associativity: the associativity of the cache
 * @param numBytes: the number of bytes in array hit_times
 * @return hit_times: a list of output, detected hits of target denoted as 1,
 * misses denoted as 0
 * @return detect_timestamps: a list of rdtscp timestamps from prime+probe
 * @return size: the size of timestamps array
 * detections
 */
uint64_t prime_probe(EvictionSet *es, uint8_t associativity, uint8_t *hit_times,
                     uint64_t numBytes, uint64_t *detect_timestamps,
                     int threshold);

uint64_t *prime_probe_many_sets(
    EvictionSet **eslist, uint8_t num_sets, uint8_t associativity,
    uint64_t numProbes, uint8_t probe_results[num_sets][numProbes],
    uint64_t hit_storage_size,
    uint64_t detect_timestamps[num_sets][hit_storage_size], int threshold);

/**
 * Return the hit count for the given trace at the last width * height addresses
 * in results
 * @param results: the traces of prime+probe
 * @param numBytes: the number of bytes of results
 * @param width: the width of the printed output
 * @param height: the height of the printed output
 * @return the hit count for the given trace
 */
uint16_t get_slice_hit_count(uint8_t *results, uint64_t numBytes,
                             uint64_t width, uint64_t height);

void filter_pp_results(uint8_t *results, uint64_t numBytes);

/**
 * Print the last width * height outputs from results
 * @param results: the traces of prime+probe
 * @param numBytes: the number of bytes of results
 * @param width: the width of the printed output
 * @param height: the height of the printed output
 */
void print_probe_result(uint8_t *results, uint64_t numBytes, uint64_t width,
                        uint64_t height);

void flush_timestamps(uint64_t *timestamps, int size, char *filePath);

/*********************************************************************
 * Slicing Function and Slicing Helper Functions
 *********************************************************************/

/* slicing function from Clementine Maurice 2015 Reverse Engineering Intel
Last-Level Cache Complex Addressing
Using Performance Counters */
int get_i7_2600_slice(uintptr_t pa);
CacheLineSet *hugepage_inflate(void *mmap_start, int size, int set);
EvictionSet **get_all_slices_eviction_sets(void *mmap_start, int set);

void free_es_list(EvictionSet **es_list);
