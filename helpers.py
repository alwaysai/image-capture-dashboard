
import os
import time

"""
Helper functions not associated with a particular
class are defined here for modularity.
"""

FOLDER = 'samples'

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
    
    if not os.path.exists(FOLDER):
        os.mkdir(FOLDER)

    if not os.path.exists(os.path.join(FOLDER, session)):
        os.mkdir(os.path.join(FOLDER, session))

    if not os.path.exists(os.path.join(FOLDER, session, folder)):
        os.mkdir(os.path.join(FOLDER, session, folder))

    if sample_type == 'image':
        name = time.asctime().replace(' ', '_').replace(':', '_') + '.jpeg'
    else:
        name = time.asctime().replace(' ', '_').replace(':', '_') + '.avi'
    
    file_name = os.path.join(FOLDER, session, folder, name)

    return file_name
