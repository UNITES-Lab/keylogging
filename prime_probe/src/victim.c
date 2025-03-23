#define _DEFAULT_SOURCE
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <unistd.h>
#include <x86intrin.h>

#include "../lib/constants.h"
#include "../lib/eviction.h"
#include "../lib/l3pp.h"

#define TRANSMIT_INTERVAL 6000

uint8_t *target;

unsigned int core_id = 0;

void handle_sigint(int sig) { free(target); }

void send(int bit) {
  uint64_t start_time = __rdtscp(&core_id);
  if (bit) {
    while (__rdtscp(&core_id) - start_time < 10000) {
      *(volatile uint8_t *)target;
    }
  } else {
    while (__rdtscp(&core_id) - start_time < 10000)
      ;
  }
}

void send_byte(uint8_t byte) {
  for (int i = 0; i < 8; i++) {
    send(byte & 0x1);
    byte >>= 1;
  }
}

int main() {
  void *mapping_start = mmap(NULL, EVERGLADES_LLC_SIZE, PROT_READ,
                             MAP_PRIVATE | MAP_ANONYMOUS | MAP_HUGETLB, -1, 0);
  printf("%p\n", (void *)mapping_start);

  CacheLineSet *cl_set[1024];
  EvictionSet *es_set[1024];

  for (int i = 0; i < 1024; i++) {
    cl_set[i] = hugepage_inflate(mapping_start, 32, i);
  }

  uint64_t start_time = 0;
  int i = 127;
  while (1) {
    /* profiling set and slice */
    uint64_t start = __rdtscp(&core_id);
    while (__rdtscp(&core_id) - start < 10000) {
      for (int j = 0; j < 8; j++) {
        volatile char tmp = *(volatile char *)(cl_set[i]->cache_lines[j]);
      }
    }

    start = __rdtscp(&core_id);
    while (__rdtscp(&core_id) - start < 50000)
      ;
  }
}
