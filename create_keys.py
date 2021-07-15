#!/usr/bin/env python
import psutil, re, subprocess, requests, os, collections
from tqdm import tqdm
from pathlib import Path



#Configuration
workdir = '/tmp/tmp.newbits'
configurl = 'https://dl.google.com/dl/edgedl/chromeos/recovery/recovery.conf?source=linux_recovery.sh'
ostoolversion='0.9.2'

#Temporary files
config='config.txt'

#Helper Functions

def makehash():
    return collections.defaultdict(makehash)

#Cleanup files
def cleanup(path, filename):
    file_path = os.path.join(path, filename)
    if os.path.exists(file_path):
        os.remove(file_path)

#Retrieve file from web
def get_file(url, filename,resume=False):
    file_path = os.path.join(workdir,filename)
    if resume is False:
        cleanup(workdir, filename)
        r = requests.get(url, stream=True, allow_redirects=True)
        total_size = int(r.headers.get('content-length'))
        initial_pos = 0

        with open(file_path, 'wb') as data:
            with tqdm(total=total_size, unit_scale=True,
            desc=filename,initial=initial_pos, ascii=True) as pbar:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        data.write(chunk)
                        pbar.update(len(chunk))
    if resume is True:
        resume_header = {'Range':f'bytes={Path(file_path).stat().st_size}-'}
        r = requests.get(url, stream=True, headers=resume_header)
        total_size = int(r.headers.get('content-length'))
        initial_pos = Path(file_path).stat().st_size
        with open(file_path, 'ab') as data:
             with tqdm(total=total_size, unit_scale=True,
            desc=filename,initial=initial_pos, ascii=True) as pbar:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        data.write(chunk)
                        pbar.update(len(chunk))
#Populate devices from config into dictionary
def populate_devices(dict):
    config_file = os.path.join(workdir, config)
    pattern = re.compile(r'(name=)')
    with open(config_file, 'r') as data:
        lines = data.readlines()
        for i, line in enumerate(lines):
            if re.search(pattern, line):
                device = line.strip()
                device = line.strip('name=')
                version = lines[i+1].strip('version=')
                desc = lines[i+2].strip('desc=')
                channel = lines[i+3].strip('channel=')
                hwidmatch = lines[i+4].strip('hwidmatch=')
                hwid = lines[i+5].strip('hwid=')
                md5 = lines[i+6].strip('md5=')
                sha1 = lines[i+7].strip('sha1=')
                zipfilesize = lines[i+8].strip('zipfilesize=')
                filename = lines[i+9].strip('file=')
                filesize = lines[i+10].strip('filesize=')
                url = lines[i+11].strip('url=')
                dict[device] = { 'version': version.strip(), 'desc': desc.strip(), 'channel': channel.strip(),'hwidmatch': hwidmatch.strip(), 'hwid': hwid.strip(), 'md5': md5.strip(), 'sha1': sha1.strip(), 'zipfilesize': zipfilesize.strip(), 'file': filename.strip(), 'filesize': filesize.strip(), 'url': url.strip() }


#Get All Drives SCSI devices, even the ones we don't want
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


#DO STUFF
if os.path.exists(workdir):
    pass
else:
    os.makedirs(workdir)

testurl = 'https://dl.google.com/dl/edgedl/chromeos/recovery/chromeos_13904.55.0_asuka_recovery_stable-channel_mp.bin.zip'
get_file(configurl, config)
get_file(testurl, 'test.zip', resume=True)

