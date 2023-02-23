#!/usr/bin/env python
import psutil, re, subprocess, requests, os, collections, hashlib, shutil, ctypes, json
from tqdm import tqdm
from pathlib import Path
from subprocess import Popen



#Configuration
workdir = '/tmp/tmp.newbits'
configurl = 'https://dl.google.com/dl/edgedl/chromeos/recovery/recovery2.json'
ostoolversion='0.9.2'
images = {}
#Temporary files
json_file='recovery2.json'

#Helper Functions
def isAdmin():
    is_admin = (os.getuid() == 0)
    return is_admin

def makehash():
    return collections.defaultdict(makehash)

def check_disk_space(required, mount):
    total, used, free = shutil.disk_usage(mount)
    if required >= free:
        print('Not enough disk space to download image')
        exit()
    else:
        return True

#Cleanup files
def cleanup(path, filename):
    file_path = os.path.join(path, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
def check_sha1(filename, filehash):
    sha = hashlib.sha1()
    with open(filename, 'rb') as f:
        chunk = f.read()
        if chunk:
            sha.update(chunk)
    try:
        assert sha.hexdigest() == filehash
    except AssertionError:
        print('File is corrupt, restart program!')
    else:
        print('File has been validated!')
        return True



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
                    
def unpack_image(zipfile, filesize):
    zip_path = os.path.join(workdir, zipfile)
    image_file = re.sub('.zip', '', zipfile)
    image_path = os.path.join(workdir, image_file)
    if os.path.exists(zip_path):
        if os.path.exists(image_path):
            cleanup(workdir, image_path)
        subprocess.run(['unzip', f'{zip_path}', '-d', f'{workdir}'])
    print('Checking bin file size matches..')
    print(f'Local file size is: {Path(image_path).stat().st_size} ')
    print(f'Expected file size is: {filesize}')
    if Path(image_path).stat().st_size == int(filesize):
        print('File size matches, proceeding..')
    else:
        print('File size does not match.. exiting program.')
        exit()
    
def apply_image(image_file, usb_keys):
    cmds = []
    image_file = re.sub('.zip', '', image_file)
    image_path = os.path.join(workdir, image_file)
    for key in usb_keys:
        print(f'Applying image {image_file} to key /dev/{key}')
        cmd = f'dd bs=4194304 of=/dev/{key} if={image_path} conv=sync status=progress'
        cmds.append(cmd)
    procs = [ Popen(i, shell=True) for i in cmds ]
    for p in procs:
        p.wait()

class Image:
    def __init__(self, name, channel, hwidmatch, url, sha1, filename, zipfilesize, filesize):
        self.name = name
        self.channel = channel
        self.hwidmatch = hwidmatch
        self.url = url
        self.sha1 = sha1
        self.filename = filename
        self.zipfilesize = zipfilesize
        self.filesize = filesize

class USB:
    def __init__(self, device, vendor, model, size):
        self.device = device
        self.vendor = vendor
        self.model = model
        self.size = size
    

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
bprocess.run(['cat', f'/sys/block/{device}/device/model'], capture_output=True, text=True).stdout.strip()bprocess.run(['cat', f'/sys/block/{device}/device/model'], capture_output=True, text=True).stdout.strip()
    size = sub
    size = sub
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

def print_device_info(usb_devices):
    for usb_key in usb_devices:
        info = get_device_info()
    


#DO STUFF

def run_recovery():
    if isAdmin():
        pass
    else:
        print('Not running with admin priviledges!')
        exit()
    print('Checking for Working Directory...')
    if os.path.exists(workdir):
        print('Working Directory Found!')
    else:
        print('Creating Working Directory!')
        os.makedirs(workdir)
    print('Downloading recovery file from Google')
    get_file(configurl, config)
    print('Retrieving model information')
    populate_devices(images)
    choice = get_choices()
    image = Image(choice, images[choice]['channel'], images[choice]['hwidmatch'],images[choice]['url'], images[choice]['sha1'], images[choice]['file'], images[choice]['zipfilesize'], images[choice]['filesize'])
    msg = f'''
    You selected:
    {image.name}
    channel: {image.channel}
    pattern: {image.hwidmatch}
    '''
    print(msg)
    while ( res:=input("Do you want to continue? (Enter y/n)").lower() ) not in {"y", "n"}: pass

    if res == 'y':
        filename = image.filename + '.zip'
        file_path = os.path.join(workdir, filename)
        check_disk_space(int(image.zipfilesize), workdir)
        if os.path.exists(file_path):
            if Path(file_path).stat().st_size == image.zipfilesize:
                print('File already exists, skipping download!')
            else:
                get_file(image.url, filename, resume=True)
        else:
            get_file(image.url, filename)
    else:
        print('Exiting program..')
        exit()
    if check_sha1(file_path, image.sha1):
        pass
    else:
        print('Image did not pass SHA1 hash check..exiting.')
        exit()
    
    print('Unpacking Image..')
    unpack_image(filename, image.filesize)
    print('Gathering infromation about USB drives..')
    usb_drives = get_usbdrives(get_drives())
    usbdict = {}
    for usb_drive in usb_drives:
        get_device_info(usbdict, usb_drive)
    
    
    for device, info in usbdict.items():
        print(f'Device: /dev/{device}')
        for key in info:
            print(f'{key}: {info[key]}')
        print('\n')
    
    print('These devices were found!')
    print(f'Total number of devices: {len(usb_drives)}')
    while ( res:=input("Proceed devices listed above? CAUTION: THIS WILL ERASE ALL DATA ON LISTED DEVICES! (Enter y/n)").lower() ) not in {"y", "n"}: pass
    if res == 'y':
        apply_image(image.filename, usb_drives)
        
    while ( res:=input("Process Complete.\nDo you want to cleanup all files? (Enter y/n)").lower() ) not in {"y", "n"}: pass
    if res == 'y':
        cleanup(workdir,filename)
        cleanup(workdir, image.filename)

if __name__ == "__main__":
    run_recovery()
