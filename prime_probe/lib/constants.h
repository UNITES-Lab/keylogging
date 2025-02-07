/*********************************************************************
 * General Constants
 *********************************************************************/
#define PAGE_OFFSET_BITS 12
#define LINE_OFFSET_BITS 6
#define PAGE_BYTES (1 << PAGE_OFFSET_BITS)
#define CACHE_LINE_BYTES (1 << LINE_OFFSET_BITS)
#define HUGE_PAGE_OFFSET_BITS 21
#define HUGE_PAGE_BYTES (1 << HUGE_PAGE_OFFSET_BITS)
#define KBD_KEYCODE_ADDR 0x656920106b20
/*********************************************************************
 * Machine Constants
 *********************************************************************/
#define ACADIA 0
#define EVERGLADES 1
/*********************************************************************
 * Acadia (Coffee Lake i7-9750H) Constants
 *********************************************************************/

#define ACADIA_CACHE_SET_BITS 10
#define ACADIA_ASSOCIATIVITY 12
#define ACADIA_NUM_SLICES 6
#define ACADIA_SETS_PER_SLICE (1 << ACADIA_CACHE_SET_BITS) / ACADIA_NUM_SLICES
#define ACADIA_LLC_SIZE 8 * 1024 * 1024

/*********************************************************************
 * Everglades (Sandy Bridge i7-2600) Constants
 *********************************************************************/
#define EVERGLADES_CACHE_SET_BITS 11 // 8192 / 4 = 2048
#define EVERGLADES_ASSOCIATIVITY 16
#define EVERGLADES_NUM_SLICES 4
#define EVERGLADES_SETS_PER_SLICE 2048
#define EVERGLADES_LLC_SIZE 8 * 1024 * 1024

/*********************************************************************
 * Prime+Probe
 *********************************************************************/
#define WAIT_INTERVAL 10000
#define BITS_PER_BYTE 8
