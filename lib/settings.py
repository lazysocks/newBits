import os
#Configurable settings
workdir = '/tmp/tmp.newbits'
configurl = 'https://dl.google.com/dl/edgedl/chromeos/recovery/'
recovery_file = 'recovery2.json'



#DO NOT MODIFY BELOW
url = configurl + recovery_file
recovery_file_path = os.path.join(workdir, recovery_file)

def device_image_paths(selected_device):
    imagefile = selected_device['file']
    imagefile = os.path.join(workdir, imagefile)
    zipfile = selected_device['file'] + '.zip'
    zipfile = os.path.join(workdir, zipfile)
    paths = { 'imagefile': imagefile, 'zipfile': zipfile}
    return paths