import shutil, re, subprocess
from .utility import convert_size

class USB:
    def __init__(self):
        self.drives = self.get_drives()
        self.removable = self.get_removable(self.drives)
                

    def get_drives(self):
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
 
    def get_removable(self, drives):
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
        removable_drives = {}
        for device in usb_drives:
            vendor = subprocess.run(['cat', f'/sys/block/{device}/device/vendor'], capture_output=True, text=True).stdout.strip()
            model = subprocess.run(['cat', f'/sys/block/{device}/device/model'], capture_output=True, text=True).stdout.strip()
            size = subprocess.run(['cat', f'/sys/block/{device}/size'], capture_output=True).stdout
            removable_drives[device] = {'vendor': vendor, 'model': model, 'human_readable_size': convert_size(int(size)), 'size': int(size)}
        return removable_drives

    def print_disk_info(self):
        print('These devices were found!')
        for device, device_info in self.removable.items():
            msg = f'''
            Device Make/Model:  {device_info['vendor']} {device_info['model']}   
            Device path: /dev/{device}
            Size: {device_info['human_readable_size']}
            '''
            print(msg)

    def prompt_to_proceed(self):
        self.print_disk_info()
        print(f'Total number of devices found: {len(self.removable)}')
        while ( res:=input("Proceed with the devices listed above?  CAUTION: THIS WILL ERASE ALL DATA ON LISTED DEVICES! (Enter y/n)").lower() ) not in {"y", "n"}: pass
        if res == 'y':
            proceed = True
            return proceed
        else:
           proceed = False
           return proceed
        


def check_disk_space(required, mount):
    total, used, free = shutil.disk_usage(mount)
    if required >= free:
        print('Not enough disk space to download image')
        exit()
    else:
        return True

#Get raw size
def get_device_size(device):
    sector = subprocess.run(['cat', f'/sys/block/{device}/size'], capture_output=True).stdout
    sector = int(sector) * 512 / 1024 / 1024
    return sector
