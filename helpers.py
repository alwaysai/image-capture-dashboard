
import os
import time

"""
Helper functions not associated with a particular
class are defined here for modularity.
"""


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
    
    if not os.path.exists('samples'):
        os.mkdir('samples')

    if not os.path.exists('samples/{}'.format(session)):
        os.mkdir('samples/{}'.format(session))

    if not os.path.exists('samples/{}/{}'.format(session, folder)):
        os.mkdir('samples/{}/{}'.format(session, folder))

    if sample_type == "image":
        file_name = 'samples/{}/{}/{}'.format(session, folder, time.asctime().replace(" ", "_").replace(":", "_") + ".jpeg")
    else:
        file_name = 'samples/{}/{}/{}'.format(session, folder, time.asctime().replace(" ", "_").replace(":", "_") + ".avi")

    return file_name
