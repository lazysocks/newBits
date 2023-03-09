#!/usr/bin/env python

#imports
from lib.data import find_model_keys, get_choice

import psutil, re, subprocess, requests, os, collections, hashlib, shutil, ctypes, json

from subprocess import Popen




images = {}
#Temporary files
json_file='recovery2.json'










                    


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
    channel: {image.channel}2
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
