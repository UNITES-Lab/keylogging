#define _GNU_SOURCE
#include <math.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>

#include "../lib/utils.h"

/*********************************************************************
 * Ranges and Number Lists
 *********************************************************************/

void print_range(Range *r) { printf("[%u, %u)\n", r->low, r->high); }

void print_range_list(RangeList *rl) {
  for (int i = 0; i < rl->length; i++) {
    printf("[%u, %u) ", rl->ranges[i]->low, rl->ranges[i]->high);
  }
  printf("\n");
}

Range *new_range(int low, int high) {
  Range *nr = malloc(sizeof(Range));
  nr->low = low;
  nr->high = high;

  return nr;
}

bool range_contains(Range *r, int val) {
  return (val >= r->low) && (val < r->high);
}

RangeList *new_range_list(void) {
  RangeList *rl = malloc(sizeof(RangeList));
  rl->length = 0;
  rl->ranges = NULL;

  return rl;
}

void push_range(RangeList *rl, Range *r) {
  rl->length++;
  rl->ranges = reallocarray(rl->ranges, rl->length, sizeof(Range *));
  rl->ranges[rl->length - 1] = r;
}

void free_range_list(RangeList *rl) {
  for (int i = 0; i < rl->length; i++) {
    free(rl->ranges[i]);
  }

  free(rl->ranges);
  free(rl);
}

void print_num_list(NumList *nl) {
  for (int i = 0; i < nl->length; i++) {
    printf("%lu ", nl->nums[i]);
  }
  printf("\n");
}

NumList *new_num_list(int capacity) {
  NumList *nl = malloc(sizeof(NumList));
  nl->capacity = capacity;
  nl->length = 0;
  nl->nums = calloc(nl->capacity, sizeof(uint64_t));

  return nl;
}

void push_num(NumList *nl, uint64_t num) {
  nl->length++;
  if (nl->length > nl->capacity) {
    nl->capacity *= 2;
    nl->nums = reallocarray(nl->nums, nl->capacity, sizeof(uint64_t));
  }
  nl->nums[nl->length - 1] = num;
}

void clear_num_list(NumList *nl) {
  for (int i = 0; i < nl->capacity; i++) {
    nl->nums[i] = 0;
  }

  nl->length = 0;
}

void free_num_list(NumList *nl) {
  free(nl->nums);
  free(nl);
}

uint64_t pop_num(NumList *nl) {
  uint64_t num = nl->nums[nl->length - 1];
  nl->length--;
  return num;
}

// Used for median_and_sort
int compare_nums(const void *a, const void *b) {
  if (*(uint64_t *)a < *(uint64_t *)b) {
    return -1;
  }

  if (*(uint64_t *)a > *(uint64_t *)b) {
    return 1;
  }

  return 0;
}

// Sort a list of numbers and return the median
uint64_t median_and_sort(NumList *nl) {
  qsort(nl->nums, nl->length, sizeof(uint64_t), compare_nums);
  return nl->nums[(nl->length) / 2];
}

uint64_t min(NumList *nl) {
  int min_index = 0;

  for (int i = 0; i < nl->length; i++) {
    if (nl->nums[i] < nl->nums[min_index]) {
      min_index = i;
    }
  }

  return nl->nums[min_index];
}

uint64_t max(NumList *nl) {
  int max_index = 0;

  for (int i = 0; i < nl->length; i++) {
    if (nl->nums[i] > nl->nums[max_index]) {
      max_index = i;
    }
  }

  return nl->nums[max_index];
}

uint64_t mean(NumList *nl) {
  uint64_t sum = 0;
  for (int i = 0; i < nl->length; i++) {
    sum += nl->nums[i];
  }

  return sum /= nl->length;
}

uint64_t has_greater_than(NumList *nl, int threshold) {
  for (int i = 0; i < nl->length; i++) {
    if (nl->nums[i] > threshold)
      return 1;
  }
  return 0;
}

uint64_t print_stats(NumList *nl) {
  uint64_t median = median_and_sort(nl);
  double mean = 0;

  for (int i = 0; i < nl->length; i++) {
    mean += nl->nums[i];
  }

  mean /= nl->length;

  double sd = 0;
  uint64_t minimum = nl->nums[0];
  uint64_t maximum = nl->nums[0];

  for (int i = 0; i < nl->length; i++) {
    sd += pow(nl->nums[i] - mean, 2);
    if (nl->nums[i] < minimum) {
      minimum = nl->nums[i];
    }

    if (nl->nums[i] > maximum) {
      maximum = nl->nums[i];
    }
  }

  sd /= (nl->length - 1);

  sd = sqrt(sd);

  printf("Median: %lu Mean: %.2f Standard deviation: %.2f Minimum: %lu "
         "Maximum: %lu\n",
         median, mean, sd, minimum, maximum);
}

int get_bit(uint64_t value, int n) { return (value >> n) & 0x1; }
void safe_print(char *msg) { write(STDOUT_FILENO, msg, sizeof(msg) - 1); }

void read_binary(const char *filename, uint64_t *array, size_t size) {
  FILE *f = fopen(filename, "rb");
  if (!f) {
    perror("fopen failed");
    exit(1);
  }

  fread(array, sizeof(uint64_t), size, f);
  fclose(f);
}
