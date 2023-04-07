#!/usr/bin/env python

from lib import settings, data, disks, utility
import os

# %%
def run_recovery():

    #Check for sudo priviledges
    if utility.isAdmin():
        pass
    else:
        print('Not running with sudo priviledges!')
    
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


    #Confirm device selection or exit
    while ( res:=input("Do you want to continue? (Enter y/n)").lower() ) not in {"y", "n"}: pass

    if res == 'y':
        


if __name__ == "__main__":
    run_recovery()


    



