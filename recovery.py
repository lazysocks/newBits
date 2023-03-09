#!/usr/bin/env python

import lib.settings as settings
import lib.utility as utility
import lib.data as data
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
    
    #Get data from recovery file
    results = data.get_json_data(settings.recovery_file_path)

    #Filter choice set by prefix
    choices = data.find_model_keys(results)

    #Get final device selection
    selected_device = data.get_choice(choices)

    utility.print_device_info(selected_device)

    #Confirm device selection or exit
    while ( res:=input("Do you want to continue? (Enter y/n)").lower() ) not in {"y", "n"}: pass

    if res == 'y':
        


if __name__ == "__main__":
    run_recovery()


    



