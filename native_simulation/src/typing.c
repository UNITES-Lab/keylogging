#include <emmintrin.h>
#include <fcntl.h>
#include <linux/input-event-codes.h>
#include <linux/input.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>
#include <x86intrin.h>

int shift_active = 0;
int capslock_active = 0;

const char *keymap[256] = {[KEY_A] = "a",
                           [KEY_B] = "b",
                           [KEY_C] = "c",
                           [KEY_D] = "d",
                           [KEY_E] = "e",
                           [KEY_F] = "f",
                           [KEY_G] = "g",
                           [KEY_H] = "h",
                           [KEY_I] = "i",
                           [KEY_J] = "j",
                           [KEY_K] = "k",
                           [KEY_L] = "l",
                           [KEY_M] = "m",
                           [KEY_N] = "n",
                           [KEY_O] = "o",
                           [KEY_P] = "p",
                           [KEY_Q] = "q",
                           [KEY_R] = "r",
                           [KEY_S] = "s",
                           [KEY_T] = "t",
                           [KEY_U] = "u",
                           [KEY_V] = "v",
                           [KEY_W] = "w",
                           [KEY_X] = "x",
                           [KEY_Y] = "y",
                           [KEY_Z] = "z",
                           [KEY_1] = "1",
                           [KEY_2] = "2",
                           [KEY_3] = "3",
                           [KEY_4] = "4",
                           [KEY_5] = "5",
                           [KEY_6] = "6",
                           [KEY_7] = "7",
                           [KEY_8] = "8",
                           [KEY_9] = "9",
                           [KEY_0] = "0",
                           [KEY_SPACE] = " ",
                           [KEY_ENTER] = "\n",
                           [KEY_LEFTSHIFT] = "SHIFT",
                           [KEY_RIGHTSHIFT] = "SHIFT",
                           [KEY_LEFTCTRL] = "CTRL",
                           [KEY_RIGHTCTRL] = "CTRL",
                           [KEY_CAPSLOCK] = "CAPSLOCK",
                           [KEY_TAB] = "TAB",
                           [KEY_LEFTALT] = "ALT",
                           [KEY_RIGHTALT] = "ALT",
                           [KEY_PAUSE] = "PAUSE"};

const char *shiftmap[256] = {[KEY_A] = "A",
                             [KEY_B] = "B",
                             [KEY_C] = "C",
                             [KEY_D] = "D",
                             [KEY_E] = "E",
                             [KEY_F] = "F",
                             [KEY_G] = "G",
                             [KEY_H] = "H",
                             [KEY_I] = "I",
                             [KEY_J] = "J",
                             [KEY_K] = "K",
                             [KEY_L] = "L",
                             [KEY_M] = "M",
                             [KEY_N] = "N",
                             [KEY_O] = "O",
                             [KEY_P] = "P",
                             [KEY_Q] = "Q",
                             [KEY_R] = "R",
                             [KEY_S] = "S",
                             [KEY_T] = "T",
                             [KEY_U] = "U",
                             [KEY_V] = "V",
                             [KEY_W] = "W",
                             [KEY_X] = "X",
                             [KEY_Y] = "Y",
                             [KEY_Z] = "Z",
                             [KEY_1] = "!",
                             [KEY_2] = "@",
                             [KEY_3] = "#",
                             [KEY_4] = "$",
                             [KEY_5] = "%",
                             [KEY_6] = "^",
                             [KEY_7] = "&",
                             [KEY_8] = "*",
                             [KEY_9] = "(",
                             [KEY_0] = ")",
                             [KEY_SPACE] = " ",
                             [KEY_ENTER] = "\n",
                             [KEY_LEFTSHIFT] = "SHIFT",
                             [KEY_RIGHTSHIFT] = "SHIFT",
                             [KEY_LEFTCTRL] = "CTRL",
                             [KEY_RIGHTCTRL] = "CTRL",
                             [KEY_CAPSLOCK] = "CAPSLOCK",
                             [KEY_TAB] = "TAB",
                             [KEY_LEFTALT] = "ALT",
                             [KEY_RIGHTALT] = "ALT",
                             [KEY_PAUSE] = "PAUSE"};

#define SAMPLE_MAX_LENGTH 1000
int simulate(int fd, uint64_t *keycodes, uint64_t *stroke_timestamps,
             int *numchars, uint64_t max_strokes) {
  struct input_event ev;
  int num_strokes = 0;
  unsigned int core_id = 0;
  printf("simulation starts, please start typing: ");
  fflush(stdout);

  while (1) {
    ssize_t n = read(fd, &ev, sizeof(struct input_event));
    if (n == (ssize_t)sizeof(struct input_event) && ev.type == EV_KEY) {
      if (ev.code == KEY_RIGHTCTRL) {
        *numchars = num_strokes;
        break;
      }
      if (ev.code == KEY_LEFTSHIFT || ev.code == KEY_RIGHTSHIFT) {
        if (ev.value == 1)
          shift_active = 1; // pressed
        if (ev.value == 0)
          shift_active = 0; // released
      }

      if (ev.value == 1) { // key press only
        if (ev.code != 0) {
          stroke_timestamps[num_strokes] = __rdtscp(&core_id);
          keycodes[num_strokes] = ev.code;
          num_strokes++;
        }
      }
    }
  }
  printf("\nsuccessfully exited, typed %d characters\n", *numchars);
  return *numchars > 0;
}

void *shm_ptr;
int shm_fd, fd;

void handle_sigint(int sig) {
  *(volatile char *)(shm_ptr) = 2;
  munmap(shm_ptr, 4096);
  close(fd);
}

char *strarr_to_string(char **strarr, int length) {
  char *outstr = malloc(length * sizeof(char));
  sprintf(outstr, "[");
  for (int i = 0; i < length; i++) {
    sprintf(outstr, "\"%s\", ", strarr[i]);
  }
  sprintf(outstr, "]");
  return outstr;
}

char *intarr_to_string(uint64_t *intarr, int length) {
  size_t bufsize =
      length * 21 + 3; // generous: 20 digits + comma/space + brackets
  char *outstr = malloc(bufsize);
  if (!outstr)
    return NULL;

  size_t used = 0;
  used += snprintf(outstr + used, bufsize - used, "[");

  for (int i = 0; i < length; i++) {
    if (i < length - 1)
      used += snprintf(outstr + used, bufsize - used, "%lu, ", intarr[i]);
    else
      used += snprintf(outstr + used, bufsize - used, "%lu", intarr[i]);
  }

  snprintf(outstr + used, bufsize - used, "]");
  return outstr;
}

void output_sample(int participant_id, int test_section_id, int sentence_id,
                   uint64_t *keycodes, uint64_t *timestamps, int num_chars) {
  FILE *file = fopen("test.json", "a");
  if (file == NULL) {
    perror("fopen");
    exit(1);
  }

  char *keycodes_str = intarr_to_string(keycodes, num_chars);
  char *timestamps_str = intarr_to_string(timestamps, num_chars);
  fprintf(file,
          "{\"participant_id\": %d, \"test_section_id\": %d, "
          "\"keystrokes\": %s, \"intervals\": %s, \"sentence_id\": %d}\n",
          participant_id, test_section_id, keycodes_str, timestamps_str,
          sentence_id);
  free(keycodes_str);
  free(timestamps_str);
}

int main(int argc, char **argv) {
  signal(SIGINT, handle_sigint);
  if (argc < 2) {
    fprintf(stderr, "Usage: %s /dev/input/eventX\n", argv[0]);
    return 1;
  }

  fd = open(argv[1], O_RDONLY);
  if (fd < 0) {
    perror("open");
    return 1;
  }

  shm_fd = shm_open("ipc_signals", O_RDWR, 0666);
  if (shm_fd < 0) {
    perror("shm_open");
    return 1;
  }

  shm_ptr = mmap(0, 4096, PROT_READ | PROT_WRITE, MAP_SHARED, shm_fd, 0);
  if (shm_ptr == MAP_FAILED) {
    perror("mmap");
    return 1;
  }

  uint64_t *timestamps = malloc(SAMPLE_MAX_LENGTH * sizeof(uint64_t));
  uint64_t *keycodes = malloc(SAMPLE_MAX_LENGTH * sizeof(uint64_t));

  int sample_id = 0;
  *(volatile char *)(shm_ptr + 3) = '0' + sample_id;
  *(volatile char *)(shm_ptr + 4) = '.';
  *(volatile char *)(shm_ptr + 5) = 'b';
  *(volatile char *)(shm_ptr + 6) = 'i';
  *(volatile char *)(shm_ptr + 7) = 'n';
  *(volatile char *)(shm_ptr + 8) = '\0';

  printf("waiting for prime+probe to be ready\n");
  while (!*(volatile char *)shm_ptr)
    ;
  *(volatile char *)(shm_ptr + 2) = 1;
  *(volatile char *)(shm_ptr + 1) = 0;

  printf("\n");

  // run simulation
  int num_chars = 0;
  simulate(fd, keycodes, timestamps, &num_chars, SAMPLE_MAX_LENGTH);

  *(volatile char *)(shm_ptr + 1) = 2;

  output_sample(0, 0, 0, keycodes, timestamps, num_chars);
  sample_id++;
  free(timestamps);
  free(keycodes);

  return 0;
}
