/*
Note: the functions in this file were adapted from this wonderful repository:

https://github.com/cirosantilli/linux-kernel-module-cheat/blob/873737bd1fc6e5ee0378f21e9df1c52e3f61e3fb/userland/virt_to_phys_user.c
*/

// #include <cmath>
#define _GNU_SOURCE

#include <fcntl.h> /* open */
#include <math.h>  /* fabs */
#include <stdbool.h>
#include <stdint.h> /* uint64_t  */
#include <stdio.h>  /* snprintf */
#include <stdlib.h> /* size_t */
#include <sys/types.h>
#include <unistd.h> /* pread, sysconf */

#ifndef ADDRESS_TRANSLATION_H
#define ADDRESS_TRANSLATION_H
#define HUGE_PAGE_SIZE 2 * 1024 * 1024
#define PAGE_SIZE 4096

/* Format documented at:
 * https://github.com/torvalds/linux/blob/v4.9/Documentation/vm/pagemap.txt
 */
typedef struct {
  uint64_t pfn : 54;
  unsigned int soft_dirty : 1;
  unsigned int file_page : 1;
  unsigned int swapped : 1;
  unsigned int present : 1;
} PagemapEntry;

/* Parse the pagemap entry for the given virtual address.
 *
 * @param[out] entry      the parsed entry
 * @param[in]  pagemap_fd file descriptor to an open /proc/pid/pagemap file
 * @param[in]  vaddr      virtual address to get entry for
 * @return                0 for success, 1 for failure
 */
int pagemap_get_entry(PagemapEntry *entry, int pagemap_fd, uintptr_t vaddr) {
  size_t nread;
  ssize_t ret;
  uint64_t data;
  uintptr_t vpn;

  vpn = vaddr / sysconf(_SC_PAGE_SIZE);
  nread = 0;
  while (nread < sizeof(data)) {
    ret = pread(pagemap_fd, &data, sizeof(data) - nread,
                vpn * sizeof(data) + nread);
    nread += ret;
    if (ret <= 0) {
      return 1;
    }
  }
  entry->pfn = data & (((uint64_t)1 << 54) - 1);
  entry->soft_dirty = (data >> 54) & 1;
  entry->file_page = (data >> 61) & 1;
  entry->swapped = (data >> 62) & 1;
  entry->present = (data >> 63) & 1;
  return 0;
}

/* Convert the given virtual address to physical using /proc/PID/pagemap.
 *
 * @param[out] paddr physical address
 * @param[in]  pid   process to convert for
 * @param[in]  vaddr virtual address to get entry for
 * @return           0 for success, 1 for failure
 */
int virt_to_phys_user(uintptr_t *paddr, pid_t pid, uintptr_t vaddr) {
  char pagemap_file[BUFSIZ];
  int pagemap_fd;

  snprintf(pagemap_file, sizeof(pagemap_file), "/proc/%ju/pagemap",
           (uintmax_t)pid);
  pagemap_fd = open(pagemap_file, O_RDONLY);
  if (pagemap_fd < 0) {
    return 1;
  }
  PagemapEntry entry;
  if (pagemap_get_entry(&entry, pagemap_fd, vaddr)) {
    return 1;
  }
  close(pagemap_fd);
  *paddr =
      (entry.pfn * sysconf(_SC_PAGE_SIZE)) + (vaddr % sysconf(_SC_PAGE_SIZE));
  return 0;
}

int virt_to_phys_huge_page(uintptr_t *paddr, uintptr_t vaddr) {
  // Open /proc/self/pagemap for the current process
  int pagemap_fd = open("/proc/self/pagemap", O_RDONLY);
  if (pagemap_fd < 0) {
    perror("Failed to open /proc/self/pagemap");
    return -1;
  }

  // Get the pagemap entry
  PagemapEntry entry;
  if (pagemap_get_entry(&entry, pagemap_fd, vaddr)) {
    fprintf(stderr, "Failed to retrieve pagemap entry\n");
    close(pagemap_fd);
    return -1;
  }
  close(pagemap_fd);

  // Check if the page is present in physical memory
  if (!entry.present) {
    fprintf(stderr, "Page not present in memory\n");
    return -1;
  }

  // Compute the physical address
  *paddr = (entry.pfn * HUGE_PAGE_SIZE) + (vaddr & (HUGE_PAGE_SIZE - 1));
  return 0;
}
#endif
