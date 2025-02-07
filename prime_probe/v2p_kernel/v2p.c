#include <linux/highmem.h>
#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/mm.h>
#include <linux/module.h>

static unsigned long virt_to_phys(unsigned long virt_addr) {
  struct page *page;
  unsigned long phys_addr = 0;

  // Convert virtual address to struct page
  page = virt_to_page(virt_addr);
  if (!page) {
    pr_err("Invalid virtual address: 0x%lx\n", virt_addr);
    return 0;
  }

  // Get the physical address from the page and add the offset within the page
  phys_addr = (page_to_pfn(page) << 12) + (virt_addr & ~PAGE_MASK);
  return phys_addr;
}

static int __init kv2p_init(void) {
  unsigned long func_addr = 0x8e306b20;
  unsigned long phys_addr;

  pr_info("Kernel virtual address: 0x%lx\n", func_addr);

  phys_addr = virt_to_phys(func_addr);
  if (phys_addr) {
    pr_info("Physical address: 0x%lx\n", phys_addr);
  }

  return 0;
}

static void __exit kv2p_exit(void) { pr_info("Module unloaded.\n"); }

module_init(kv2p_init);
module_exit(kv2p_exit);

MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Kernel virtual to physical address translation demo");
MODULE_AUTHOR("James Chuang ");
