#include <stdio.h>
#include <x86intrin.h>

int main() {
  unsigned int core_id = 0;
  unsigned long time = __rdtscp(&core_id);
  printf("{\"time\": %lu}\n", time);
}
