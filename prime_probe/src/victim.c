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

  CacheLineSet *cl_set = hugepage_inflate(mapping_start, 16, 428);
  printf("%p\n", cl_set->cache_lines[0]);

  volatile uint8_t tmp = *(volatile uint8_t *)mapping_start;

  printf("%d\n", get_i7_2600_slice(KBD_KEYCODE_ADDR));

  uint64_t start_time = 0;
  while (1) {
    tmp = *(volatile uint8_t *)cl_set->cache_lines[0];
    start_time = __rdtscp(&core_id);
    while (__rdtscp(&core_id) - start_time < 20000)
      ;

    tmp = *(volatile uint8_t *)cl_set->cache_lines[0];
    start_time = __rdtscp(&core_id);
    while (__rdtscp(&core_id) - start_time < 40000)
      ;
  }
}
