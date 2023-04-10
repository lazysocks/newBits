#!/usr/bin/env python

from lib import settings, data, disks, utility
from pathlib import Path
import os

# %%
def run_recovery():

    #Check for sudo priviledges
    if utility.isAdmin():
        pass
    else:
        print('Not running with sudo priviledges!')
        exit()
    
    #Check for working directory
    print('Checking for Working Directory...')
    if os.path.exists(settings.workdir):
        print('Working Directory Found!')
    else:
        print('Working Directory Not Found!')
        print('Creating Working Directory!')
        os.makedirs(settings.workdir)
    
    #Download recovery file from Google
    print('Downloading recovery file form Google!')
    utility.get_file(settings.url, settings.recovery_file, settings.recovery_file_path)
    
    #Get device choice and print device details
    device = data.Image(settings.recovery_file_path)

    #Get USB Drives
    usb_keys = disks.USB()

    #display disk info and prompt to proceed with imaging

    proceed = usb_keys.prompt_to_proceed()

    if proceed:
        #check for diskspace
        disks.check_disk_space(int(device.choice['filesize']), settings.workdir)
        #set paths for image files
        filedir = settings.device_image_paths(device.choice)
        if os.path.exists(filedir['zipfile']):
            if Path(filedir['zipfile']).stat().st_size == device.choice['zipfilesize']:
                print('File already exists, skipping download!')
            else:
                utility.get_file(device.choice['url'], device.choice['file'] + '.zip', filedir['zipfile'], resume=True)
        else:
            utility.get_file(device.choice['url'], device.choice['file'] + '.zip', filedir['zipfile'])
        #check file integrity
        if utility.check_sha1(filedir['zipfile'], device.choice['sha1']):
            pass
        else:
            print('Image did not pass SHA1 hash check..exiting')
            exit()
        #time to unpack image
        utility.unpack_zipfile(filedir['zipfile'], filedir['imagefile'], device.choice['filesize'])

        #time to apply image
        utility.apply_image(filedir['imagefile'], usb_keys.removable)

        #end program and cleanup?
        utility.end_cleanup(filedir['zipfile', filedir['imagefile'])
    else:
        print("Aborting program...")
        exit()
     


if __name__ == "__main__":
    run_recovery()


    



