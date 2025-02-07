#include "constants.h"
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <unistd.h>
#include <x86intrin.h>

#ifndef UTILS_H
#define UTILS_H

/*********************************************************************
 * Macros
 *********************************************************************/

#define HALF_CACHE_SET(va)                                                     \
  ((((va) >> LINE_OFFSET_BITS) &                                               \
    ((1 << (PAGE_OFFSET_BITS - LINE_OFFSET_BITS)) - 1))                        \
   << LINE_OFFSET_BITS)
#define LINE_OFFSET(va) ((va) & ((1 << LINE_OFFSET_BITS) - 1))

#define MAX(x, y) ((x) >= (y) ? (x) : (y))
#define MIN(x, y) ((x) <= (y) ? (x) : (y))

/*********************************************************************
 * Ranges and Number Lists
 *********************************************************************/

// Simple abstraction for a range of numbers, including low but not high, i.e.
// [low, high)
typedef struct {
  int low;
  int high;
} Range;

typedef struct {
  Range **ranges;
  int length;
} RangeList;

void print_range(Range *r);
void print_range_list(RangeList *rl);
Range *new_range(int low, int high);
bool range_contains(Range *r, int val);
RangeList *new_range_list(void);
void push_range(RangeList *rl, Range *r);
void free_range_list(RangeList *rl);

typedef struct {
  uint64_t *nums;
  int length;
  int capacity;
} NumList;

void print_num_list(NumList *nl);
NumList *new_num_list(int capacity);
void push_num(NumList *nl, uint64_t num);
void clear_num_list(NumList *nl);
void free_num_list(NumList *nl);
uint64_t pop_num(NumList *nl);
int compare_nums(const void *a, const void *b);
uint64_t min(NumList *nl);
uint64_t max(NumList *nl);
uint64_t mean(NumList *nl);
uint64_t has_greater_than(NumList *nl, int threshold);
uint64_t median_and_sort(NumList *nl);
uint64_t print_stats(NumList *nl);

/*********************************************************************
 * Indexed Values
 *********************************************************************/

typedef struct {
  int value;
  int index;
} IndexedValue;

void printTwoLargest(IndexedValue *largest1, IndexedValue *largest2);
/* Helper function for finding two largest values in an array */
void findTwoLargest(const int hits[], int size, IndexedValue *largest1,
                    IndexedValue *largest2);

/*********************************************************************
 * Cache Utilities
 *********************************************************************/

/* Helper function for flushing the memory referenced by ptr */
void flush(volatile void *ptr, size_t length);

/* Helper function for measuring the access time of ptr[index] */
uint64_t time_access(volatile uint8_t *ptr, size_t index);

/* Helper function for getting the n'th bit of value, 0-indexed */
int get_bit(uint64_t value, int n);

/*********************************************************************
 * Signal Safe Functions
 *********************************************************************/
void safe_print(char *msg);

/*********************************************************************
 * File IO
 *********************************************************************/
void read_binary(const char *filename, uint64_t *arr, size_t size);

#endif
