
import os, collections, hashlib, requests, math
from tqdm import tqdm
from pathlib import Path
from lib import settings

#Helper Functions
def isAdmin():
    is_admin = (os.getuid() == 0)
    return is_admin

def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f'{s} {size_name[i]}'


def makehash():
    return collections.defaultdict(makehash)

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

def cleanup(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)

#Retrieve file from web
def get_file(url, filename, file_path,resume=False):
    if resume is False:
        cleanup(file_path)
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

def unpack_zipfile(zipfile, imagefile, imagefilesize):
    if os.path.exists(zipfile):
        if os.path.exists(imagefile):
            cleanup(imagefile)
        subprocess.run(['unzip', f'{zipfile}', '-d', f'{settings.workdir}'])
        print('Checking bin file size matches..')
        print(f'Local file size is {Path(imagefil).stat().st_size}')
        if Path(imagefile).stat().st_size == int(imagefilesize):
            print('File sie matches, proceeding..')
        else:
            print('File size does not match.. exiting program.')
            exit()
    
def apply_image(image_file, usb_keys):
    cmds = []
    for key in usb_keys:
        print(f'Applying image {image_file} to key /dev/{key}')
        cmd = f'dd bs=4194304 of=/dev/{key} if={image_path} conv=sync status=progress'
        cmds.append(cmd)
    procs = [ Popen(i, shell=True) for i in cmds ]
    for p in procs:
        p.wait()

    