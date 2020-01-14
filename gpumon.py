import os
import platform
import subprocess
from cffi import FFI

ffi = FFI()

ffi.cdef('''
    typedef void wrap_nvml_handle;
    wrap_nvml_handle* wrap_nvml_create();
    int wrap_nvml_destroy(wrap_nvml_handle* nvmlh);
    int wrap_nvml_get_gpucount(wrap_nvml_handle* nvmlh, int* gpucount);
    int wrap_nvml_get_gpu_name(wrap_nvml_handle* nvmlh, int gpuindex, char* namebuf, int bufsize);
    int wrap_nvml_get_tempC(wrap_nvml_handle* nvmlh, int gpuindex, unsigned int* tempC);
    int wrap_nvml_get_fanpcnt(wrap_nvml_handle* nvmlh, int gpuindex, unsigned int* fanpcnt);
    int wrap_nvml_get_power_usage(wrap_nvml_handle* nvmlh, int gpuindex, unsigned int* milliwatts);

    typedef void wrap_adl_handle;
    wrap_adl_handle* wrap_adl_create();
    int wrap_adl_destroy(wrap_adl_handle* adlh);
    int wrap_adl_get_gpucount(wrap_adl_handle* adlh, int* gpucount);
    int wrap_adl_get_gpu_name(wrap_adl_handle* adlh, int gpuindex, char* namebuf, int bufsize);
    int wrap_adl_get_gpu_pci_id(wrap_adl_handle* adlh, int gpuindex, char* idbuf, int bufsize);
    int wrap_adl_get_tempC(wrap_adl_handle* adlh, int gpuindex, unsigned int* tempC);
    int wrap_adl_get_fanpcnt(wrap_adl_handle* adlh, int gpuindex, unsigned int* fanpcnt);
    int wrap_adl_get_power_usage(wrap_adl_handle* adlh, int gpuindex, unsigned int* milliwatts);
    int wrap_nvml_get_current_clock(wrap_nvml_handle* nvmlh, int gpuindex, unsigned int *CoreClock, unsigned int *MemoryClock);
    int wrap_nvml_get_base_clock(wrap_nvml_handle* nvmlh, int gpuindex, unsigned int *CoreClock, unsigned int *MemoryClock);

    typedef void wrap_amdsysfs_handle;
    wrap_amdsysfs_handle* wrap_amdsysfs_create();
    int wrap_amdsysfs_destroy(wrap_amdsysfs_handle* sysfsh);
    int wrap_amdsysfs_get_gpucount(wrap_amdsysfs_handle* sysfsh, int* gpucount);
    int wrap_amdsysfs_get_tempC(wrap_amdsysfs_handle* sysfsh, int index, unsigned int* tempC);
    int wrap_amdsysfs_get_fanpcnt(wrap_amdsysfs_handle* sysfsh, int index, unsigned int* fanpcnt);
    int wrap_amdsysfs_get_power_usage(wrap_amdsysfs_handle* sysfsh, int index, unsigned int* milliwatts);
    int wrap_amdsysfs_get_gpu_pci(wrap_amdsysfs_handle* sysfsh, int index, char* pcibuf, int bufsize);
    int wrap_amdsysfs_get_vid_pid_subsysid(wrap_amdsysfs_handle* sysfsh, int index, char* buf, int bufsize);
    int wrap_amdsysfs_get_clock(wrap_amdsysfs_handle* sysfsh, int index, unsigned int *baseCoreClock, unsigned int *baseMemoryClock, unsigned int *coreClock, unsigned int *memoryClock);
    int wrap_amdsysfs_get_gpu_mem_maker(wrap_amdsysfs_handle* sysfsh, int index, char* makerbuf, int bufsize);

''')

if platform.system() == 'Linux':
    lib = ffi.dlopen('./gpumon/libgpumon.so')
    print("lib.wrap_nvml_create")
    nvHandle = lib.wrap_nvml_create()
    print("lib.wrap_adl_create")
    amdHandle = lib.wrap_adl_create()
    print("lib.wrap_amdsysfs_create")
    fsHandle = lib.wrap_amdsysfs_create()
else:
    nvHandle = None
    amdHandle = None
    fsHandle = None

def nvmlGetGpuCount():
    gpuCount = 0
    if nvHandle:
        count = ffi.new("int*", 0)
        lib.wrap_nvml_get_gpucount(nvHandle, count)
        gpuCount = count[0]
        ffi.release(count)
    return gpuCount

def nvmlGetGpuName():
    gpuName = None
    if nvHandle:
        count = ffi.new("int*", 0)
        lib.wrap_nvml_get_gpucount(nvHandle, count)
        name = ffi.new("char[128]")
        if count[0]:
            lib.wrap_nvml_get_gpu_name(nvHandle, 0, name, 128)
            gpuName = ffi.string(name).decode()
        ffi.release(count)
        ffi.release(name)
    return gpuName

def nvmlGetGpuInfo():
    print("=========start nvmlGetGpuInfo===============")
    info = []
    if nvHandle:
        count = ffi.new("int*", 0)
        lib.wrap_nvml_get_gpucount(nvHandle, count)
        name = ffi.new("char[128]")
        tempC = ffi.new("unsigned int*", 0)
        fanpcnt = ffi.new("unsigned int*", 0)
        power_usage = ffi.new("unsigned int*", 0)
        for i in range(count[0]):
            deviceinfo = {}
            lib.wrap_nvml_get_gpu_name(nvHandle, i, name, 128)
            deviceinfo['name'] = ffi.string(name).decode()
            lib.wrap_nvml_get_tempC(nvHandle, i, tempC)
            deviceinfo['tempC'] = tempC[0]
            lib.wrap_nvml_get_fanpcnt(nvHandle, i, fanpcnt)
            deviceinfo['fanpcnt'] = fanpcnt[0]
            lib.wrap_nvml_get_power_usage(nvHandle, i, power_usage)
            deviceinfo['power_usage'] = power_usage[0]
            info.append(deviceinfo)
        ffi.release(count)
        ffi.release(name)
        ffi.release(tempC)
        ffi.release(fanpcnt)
        ffi.release(power_usage)
    print("=========end nvmlGetGpuInfo===============")
    return info

def nvmlGetGpuClock():
    print("=========start nvmlGetGpuClock===============")
    info = []
    if nvHandle:
        count = ffi.new("int*", 0)
        lib.wrap_nvml_get_gpucount(nvHandle, count)
        baseCoreClock = ffi.new("unsigned int*", 0)
        baseMemoryClock = ffi.new("unsigned int*", 0)
        currentCoreClock = ffi.new("unsigned int*", 0)
        currentMemoryClock = ffi.new("unsigned int*", 0)
        for i in range(count[0]):
            deviceinfo = {}
            lib.wrap_nvml_get_base_clock(nvHandle, i, baseCoreClock, baseMemoryClock)
            deviceinfo['baseCoreClock'] = baseCoreClock[0]
            deviceinfo['baseMemoryClock'] = baseMemoryClock[0]
            lib.wrap_nvml_get_current_clock(nvHandle, i, currentCoreClock, currentMemoryClock)
            deviceinfo['currentCoreClock'] = currentCoreClock[0]
            deviceinfo['currentMemoryClock'] = currentMemoryClock[0]
            deviceinfo['memmaker'] = ""
            info.append(deviceinfo)
        ffi.release(count)
        ffi.release(baseCoreClock)
        ffi.release(baseMemoryClock)
        ffi.release(currentCoreClock)
        ffi.release(currentMemoryClock)
    print("=========end nvmlGetGpuClock===============")
    return info
    
def amdGetGpuCount():
    gpuCount = 0
    if amdHandle:
        count = ffi.new("int*", 0)
        lib.wrap_adl_get_gpucount(amdHandle, count)
        gpuCount = count[0]
        ffi.release(count)
    return gpuCount

def amdGetGpuName():
    gpuName = None
    if amdHandle:
        count = ffi.new("int*", 0)
        lib.wrap_adl_get_gpucount(amdHandle, count)
        name = ffi.new("char[128]")
        if count[0]:
            lib.wrap_adl_get_gpu_name(amdHandle, 0, name, 128)
            gpuName = ffi.string(name).decode()
        ffi.release(count)
        ffi.release(name)
    return gpuName

def amdGetGpuInfo():
    info = []
    if amdHandle:
        count = ffi.new("int*", 0)
        lib.wrap_adl_get_gpucount(amdHandle, count)        
        name = ffi.new("char[128]")
        tempC = ffi.new("unsigned int*", 0)
        fanpcnt = ffi.new("unsigned int*", 0)
        power_usage = ffi.new("unsigned int*", 0)
        for i in range(count[0]):
            deviceinfo = {}
            lib.wrap_adl_get_gpu_name(amdHandle, i, name, 128)
            deviceinfo['name'] = ffi.string(name).decode()
            lib.wrap_adl_get_tempC(amdHandle, i, tempC)
            deviceinfo['tempC'] = tempC[0]
            lib.wrap_adl_get_fanpcnt(amdHandle, i, fanpcnt)
            deviceinfo['fanpcnt'] = fanpcnt[0]
            lib.wrap_adl_get_power_usage(amdHandle, i, power_usage)
            deviceinfo['power_usage'] = power_usage[0]
            info.append(deviceinfo)
        ffi.release(count)
        ffi.release(name)
        ffi.release(tempC)
        ffi.release(fanpcnt)
        ffi.release(power_usage)
    return info

def fsGetGpuCount():
    gpuCount = 0
    if fsHandle:
        count = ffi.new("int*", 0)
        lib.wrap_amdsysfs_get_gpucount(fsHandle, count)
        gpuCount = count[0]
        ffi.release(count)
    return gpuCount

def fsGetGpuNameByPci(pcinum):
    with os.popen('lspci | grep VGA') as p:
        lines = p.read().splitlines(False)
        for l in lines:
            pci = l.split('VGA compatible controller:')[0].strip()
            name = l.split('VGA compatible controller:')[1].strip()
            if pci == pcinum:
                return name
    return ''

def fsGetGpuName():
    gpuName = ''
    if fsHandle:
        count = ffi.new("int*", 0)
        pci = ffi.new("char[128]")
        lib.wrap_amdsysfs_get_gpucount(fsHandle, count)
        if count[0]:
            lib.wrap_amdsysfs_get_gpu_pci(fsHandle, 0, pci, 128)
            pcinum = ffi.string(pci).decode().strip()
            gpuName = fsGetGpuNameByPci(pcinum)
        ffi.release(count)
        ffi.release(pci)
    return gpuName

def getBoardName():
    try:
        boardname = []
        with open("/opt/clinfo.txt", "r") as fs:
            pci = fs.read().splitlines(False)
            for l in pci:
                if 'Board name:' in l:
                    name = l.split(':')[1].strip()
                    print(name)
                    boardname.append(name)
        return boardname
    except Exception as e:
        logging.error("function getBoardName exception. msg: " + str(e))
        logging.exception(e)
    return 0

def fsGetGpuInfo():
    info = []
    if fsHandle:
        count = ffi.new("int*", 0)
        lib.wrap_amdsysfs_get_gpucount(fsHandle, count)
        print(count[0])
        name = ffi.new("char[128]")
        tempC = ffi.new("unsigned int*", 0)
        fanpcnt = ffi.new("unsigned int*", 0)
        power_usage = ffi.new("unsigned int*", 0)
        bname = getBoardName()
        for i in range(count[0]):
            deviceinfo = {}
            #if bname:
            deviceinfo['name'] = bname[i] + '#'
            #else:
            lib.wrap_amdsysfs_get_vid_pid_subsysid(fsHandle, i, name, 128)
            deviceinfo['name'] += ffi.string(name).decode().strip()
            lib.wrap_amdsysfs_get_tempC(fsHandle, i, tempC)
            deviceinfo['tempC'] = tempC[0]
            lib.wrap_amdsysfs_get_fanpcnt(fsHandle, i, fanpcnt)
            deviceinfo['fanpcnt'] = fanpcnt[0]
            lib.wrap_amdsysfs_get_power_usage(fsHandle, i, power_usage)
            deviceinfo['power_usage'] = power_usage[0]
            info.append(deviceinfo)
        ffi.release(count)
        ffi.release(name)
        ffi.release(tempC)
        ffi.release(fanpcnt)
        ffi.release(power_usage)
    return info

def fsGetGpuClock():
    info = []
    if nvHandle:
        count = ffi.new("int*", 0)
        lib.wrap_amdsysfs_get_gpucount(fsHandle, count)
        print(count[0])
        memmaker = ffi.new("char[128]")
        baseCoreClock = ffi.new("unsigned int*", 0)
        baseMemoryClock = ffi.new("unsigned int*", 0)
        currentCoreClock = ffi.new("unsigned int*", 0)
        currentMemoryClock = ffi.new("unsigned int*", 0)
        for i in range(count[0]):
            deviceinfo = {}
            lib.wrap_amdsysfs_get_clock(fsHandle, i, baseCoreClock, baseMemoryClock, currentCoreClock, currentMemoryClock)
            deviceinfo['baseCoreClock'] = baseCoreClock[0]
            deviceinfo['baseMemoryClock'] = baseMemoryClock[0]
            deviceinfo['currentCoreClock'] = currentCoreClock[0]
            deviceinfo['currentMemoryClock'] = currentMemoryClock[0]
            lib.wrap_amdsysfs_get_gpu_mem_maker(fsHandle, i, memmaker, 128)
            deviceinfo['memmaker'] = ffi.string(memmaker).decode().strip()
            info.append(deviceinfo)
        ffi.release(count)
        ffi.release(memmaker)
        ffi.release(baseCoreClock)
        ffi.release(baseMemoryClock)
        ffi.release(currentCoreClock)
        ffi.release(currentMemoryClock)
    return info
    
if __name__ == '__main__':
    print(amdGetGpuInfo())
    #print(nvmlGetGpuInfo())
    print(fsGetGpuInfo())    
    #print(nvmlGetGpuClock())
    print(fsGetGpuClock())
    pass
