
import os
import time
import shutil

"""
Helper functions not associated with a particular
class are defined here for modularity.
"""
STATIC = 'static'
HOME = 'samples'
FOLDER = os.path.join('static', 'samples')

def file_set_up(sample_type, session):
    """Takes in a file type, either
    'image' or 'video', creates a new folder for the
    data to be stored and returns the name of the file.

    Args:
        sample_type (string): either 'image' or 'video'

    Returns:
        string: name of newly created folder and filename
    """
    folder = "Images" if sample_type == "image" else "Videos"
    if not os.path.exists(STATIC):
        os.mkdir(STATIC)

    if not os.path.exists(FOLDER):
        os.mkdir(FOLDER)

    if not os.path.exists(os.path.join(FOLDER, session)):
        os.mkdir(os.path.join(FOLDER, session))

    if not os.path.exists(os.path.join(FOLDER, session, folder)):
        os.mkdir(os.path.join(FOLDER, session, folder))

    if sample_type == 'image':
        name = time.asctime().replace(' ', '_').replace(':', '_') + '.jpeg'
    else:
        name = time.asctime().replace(' ', '_').replace(':', '_') + '.mp4'
    
    file_name = os.path.join(FOLDER, session, folder, name)

    return file_name

def get_all_files():
    all_files = []
    if not os.path.exists(FOLDER):
        return None
    else:
        for root, _, files in os.walk(FOLDER):
            for f in files:
                if os.path.isfile(os.path.join(root, f)) and '.DS_Store' not in f:
                    all_files.append(f)
        all_files = sorted(all_files)
        return all_files

def get_file(filename):
    if not os.path.exists(FOLDER):
        return None
    else:
        for root, _, files in os.walk(FOLDER):
            for file_set_up in files:
                if file_set_up == filename:
                    return os.path.join(root, file_set_up)
                     
    return None    

def delete_file(filename):
    if os.path.exists(filename):
        os.remove(filename)
    empties = get_empty_dirs()
    while len(empties) > 0:
        for f in empties:
            if os.path.exists(f):
                os.rmdir(f)
        empties = get_empty_dirs()
    
def get_empty_dirs():
    empty_files = []
    for root, dirs, _, in os.walk(FOLDER):
        if len(os.listdir(root)) == 0:
            empty_files.append(root)
        for d in dirs:
            if os.path.exists(os.path.join(root, d)) \
                and len(os.listdir(os.path.join(root, d))) == 1 \
                and '.DS_Store' in os.listdir(os.path.join(root, d)):
                    shutil.rmtree(os.path.join(root, d))
    return empty_files
        
