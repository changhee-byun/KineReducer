import os
from zipfile import ZIP_STORED, ZipFile
import shutil

def unzip(zip_file_path, dest_path):
    os.makedirs(dest_path, exist_ok=True)
    with ZipFile(zip_file_path, mode='r') as zf:
        zf.extractall(dest_path)


def zip_dir(source_path, dest_path, zip_file_name):
    os.makedirs(dest_path, exist_ok=True)
    dest_zip_file = os.path.join(dest_path, zip_file_name)
    zip_handle = ZipFile(dest_zip_file, 'w', ZIP_STORED)
    for root, dirs, files in os.walk(source_path):
        for file in files:
            zip_handle.write(os.path.join(root, file), 
                            os.path.relpath(os.path.join(root, file), 
                            os.path.join(source_path, '..')))
    zip_handle.close()


def zip_dir_shutil(source_path, dest_path, zip_file_name):
    os.makedirs(dest_path, exist_ok=True)
    dest_zip_file = os.path.join(dest_path, zip_file_name)
    shutil.make_archive(dest_zip_file, 'zip', source_path)