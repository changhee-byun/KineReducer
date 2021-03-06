from kine_logger import KineLogger
from pathlib import Path
import mimetypes
import shutil
import os

def read_kine_files(args):
    kine_files = []
    if len(args) == 0:
        for user_input_path in Path().iterdir():
            if user_input_path.suffix == '.kine':
                kine_files.append(user_input_path)
    else:
        for arg in args:
            # if os.path.isdir(arg):
            if Path(arg).is_dir():
                for user_input_path in Path(arg).iterdir():
                    if user_input_path.suffix == '.kine':
                        kine_files.append(user_input_path)
            else:
                if Path(arg).suffix == '.kine':
                    kine_files.append(arg)

    return kine_files

def get_kmproj_file(project_folder):
    for file_path in Path(project_folder).iterdir():
        if file_path.suffix == '.kmproject':
            return file_path
    return ""

def get_resources(path, filter):
    if not path.exists():
        return []
        
    files = Path(path).iterdir()
    mimetypes.init()
    resources = []
    for file in files:
        mimestart = mimetypes.guess_type(file)[0]
        if mimestart != None:
            mimestart = mimestart.split('/')[0]
            #if mimestart in ['audio', 'video', 'image']:
            if mimestart in [filter]:
                resources.append(file)

    return resources

def delete(path):
    if path.exists():
        if path.is_dir():
            shutil.rmtree(path)
        else:
            os.remove(path)