/*
 * Wrapper for AMD SysFS on linux, using adapted code from amdcovc by matszpk
 *
 * By Philipp Andreas - github@smurfy.de
   Reworked and simplified by Andrea Lanfranchi (github @AndreaLanfranchi)
 */

#pragma once

#if defined(__cplusplus)
extern "C" {
#endif

typedef struct
{
    int sysfs_gpucount;
    unsigned int* sysfs_device_id;
    unsigned int* sysfs_hwmon_id;
    unsigned int* sysfs_pci_domain_id;
    unsigned int* sysfs_pci_bus_id;
    unsigned int* sysfs_pci_device_id;
    unsigned int* sysfs_pci_function_id;
    unsigned int* sysfs_pci_vid;
    unsigned int* sysfs_pci_pid;
    unsigned int* sysfs_pci_subsysid;
} wrap_amdsysfs_handle;

typedef struct
{
    int HwMonId = -1;
    int DeviceId = -1;
    int PciDomain = -1;
    int PciBus = -1;
    int PciDevice = -1;
    int PciFunction = -1;
    int vid = -1;
    int pid = -1;
    int subsysid = -1;

} pciInfo;

wrap_amdsysfs_handle* wrap_amdsysfs_create();
int wrap_amdsysfs_destroy(wrap_amdsysfs_handle* sysfsh);

int wrap_amdsysfs_get_gpucount(wrap_amdsysfs_handle* sysfsh, int* gpucount);

int wrap_amdsysfs_get_tempC(wrap_amdsysfs_handle* sysfsh, int index, unsigned int* tempC);

int wrap_amdsysfs_get_fanpcnt(wrap_amdsysfs_handle* sysfsh, int index, unsigned int* fanpcnt);

int wrap_amdsysfs_get_power_usage(wrap_amdsysfs_handle* sysfsh, int index, unsigned int* milliwatts);

int wrap_amdsysfs_get_gpu_pci(wrap_amdsysfs_handle* sysfsh, int index, char* pcibuf, int bufsize);

int wrap_amdsysfs_get_vid_pid_subsysid(wrap_amdsysfs_handle* sysfsh, int index, char* buf, int bufsize);

int wrap_amdsysfs_get_clock(wrap_amdsysfs_handle* sysfsh, int index, unsigned int *baseCoreClock, unsigned int *baseMemoryClock, unsigned int *coreClock, unsigned int *memoryClock);

#if defined(__cplusplus)
}
#endif