#include "/lib/eviction.h"

CacheLineSet cset = get_addr_all_slices(TARGET_SET, NUM_ADDRS);
EvictionSet evsets[NUM_SLICES];
while (cset.length > 0) {
  CacheLine victim = cset[0];
  EvictionSet evset = find_evset(victim);
  for (int i = cset_index + 1; i < cset.length; i++) {
    CacheLine eviction_target = cset[i];
    if (can_evict(evset, eviction_target)) {
      cset.remove(eviction_target);
    }
  }
  evsets.push(evset);
  cset.remove(victim);
  cset.resize();
}
