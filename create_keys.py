import psutil, re, subprocess

#Get All Drives, even the ones we don't want
def get_drives():
    devices = subprocess.run(['cat', '/proc/partitions'], capture_output=True, text=True).stdout.splitlines()
    drives = []
    for device in devices:
        match = r'sd[a-z]'
        if re.search(match, device):
            replace = r'[0-9\.]+'
            result = re.sub(replace, '', device)
            if result.strip() in drives:
                pass
            else:
                drives.append(result.strip())
    return drives

#Sort and find just USB drives
def get_usbdrives(drives):
    usb_drives = []
    for drive in drives:
        
        drive_type = subprocess.run(['cat', f'/sys/block/{drive}/device/type'], capture_output=True, text=True).stdout.strip()
        drive_removable = subprocess.run(['cat', f'/sys/block/{drive}/removable'], capture_output=True, text=True).stdout.strip()
        drive_link = subprocess.run(['readlink', '-f', f'/sys/block/{drive}'], capture_output=True, text=True).stdout.strip()
        if drive_type == '0' and drive_removable == '1' and re.search('(usb)', drive_link):
            if drive in usb_drives:
                pass
            else:
                usb_drives.append(drive)
    return usb_drives

#Get raw size
def get_device_size(device):
    sector = subprocess.run(['cat', f'/sys/block/{device}/size'], capture_output=True).stdout
    sector = int(sector) * 512 / 1024 / 1024
    return sector

#Get device info, model, vendor, data size.
def get_device_info(devices, device):
    vendor = subprocess.run(['cat', f'/sys/block/{device}/device/vendor'], capture_output=True, text=True).stdout.strip()
    model = subprocess.run(['cat', f'/sys/block/{device}/device/model'], capture_output=True, text=True).stdout.strip()
    size = subprocess.run(['cat', f'/sys/block/{device}/size'], capture_output=True).stdout
    size = int(size) * 512 / 1000000
    devices[device] = {'vendor': vendor, 'model': model, 'size':size}
    return devices

          
drives = get_drives()
print(drives)
usb_drives = get_usbdrives(drives)
print(usb_drives)