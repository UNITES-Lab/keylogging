#define _DEFAULT_SOURCE
#include <assert.h>
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
    cl_set[i] = hugepage_inflate(mapping_start, 64, i);
  }

  uint64_t start_time = 0;
  int target_set = 249;
  int target_slice = 3;
  uintptr_t paddr;
  void *target_addrs[4];
  for (int i = 0; i < 4; i++) {
    target_addrs[i] = NULL;
  }
  for (int i = 0; i < 64; i++) {
    volatile char tmp = *(char *)(cl_set[target_set]->cache_lines[i]);
    virt_to_phys_huge_page(&paddr,
                           (uintptr_t)cl_set[target_set]->cache_lines[i]);
    printf("paddr: %lx\n", paddr);
    int set = pa_to_set(paddr, EVERGLADES);
    int slice = get_i7_2600_slice(paddr);
    printf("set: %d, slice: %d\n", set, slice);
    assert(set == target_set);
    target_addrs[slice] = cl_set[target_set]->cache_lines[i];
    int all_assigned = 1;
    for (int j = 0; j < 4; j++) {
      if (target_addrs[j] == NULL) {
        all_assigned = 0;
        break;
      }
    }
    if (all_assigned)
      break;
  }
  for (int i = 0; i < 4; i++) {
    printf("addr: %p, set: %d, slice: %d\n", target_addrs[i], target_set, i);
  }

  while (1) {
    // for (int i = 0; i < 4; i++) {
    //   volatile char tmp = *(char *)target_addrs[i];
    // }
    volatile char tmp = *(char *)target_addrs[3];
  }
}
