import tempfile
import os
import time
import threading
from pathlib import Path

def _view_file_for_time_thread(file_data:bytes,file_name:str,duration:int,open_folder:bool):
    """Thread"""
    direct = tempfile.TemporaryDirectory()

    name = Path(direct.name) / Path(file_name)
    name.write_bytes(file_data)

    if open_folder:
        os.system(f"start {direct.name}")
    else:
        os.system("start " + name.as_posix())

    time.sleep(duration)

    direct.cleanup()    # Kill folder

def view_file_for_time(file_data:bytes,file_name:str,duration:int=300,open_folder:bool=False):
    """
    Non-blocking
    Opens a file temporarely and deletes it after duration seconds
    :param open_folder: True, if you want to open the temp-folder instead of the file
    :param file_data: Encoded file-data
    :param file_name: Filename, important for the ending
    :param duration: How many seconds the file should exist
    :return:
    """
    threading.Thread(
        target=_view_file_for_time_thread,
        args=(file_data, file_name, duration, open_folder),
        daemon=True
    ).start()

