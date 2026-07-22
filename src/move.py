import os
import shutil

from src.utils import remove_empty_folders
from pathlib import Path

def musiclib_move(src: str, dst: str):
    src_root = Path(src)
    dst_root = Path(dst)
    
    # Add any other directories which will not be inspected
    ignored_dirs = [dst_root]

    os.makedirs(src_root, exist_ok=True)
    os.makedirs(dst_root, exist_ok=True)

    for curr_root, sub_dirs, items in os.walk(src_root):
        ## Don't modify anything in the ignored directories, or children of the destination root
        if curr_root in ignored_dirs or Path(curr_root).resolve().is_relative_to(dst_root):
            continue
        
        ## Check if current root has children (bad practice, but works for soulseekqt/nicotine, should check for files in each root before moving)
        if sub_dirs:
            continue
        
        ## Check if items are .flac files only
        src_dirs = [os.path.join(curr_root, item) for item in items]
        dst_dirs = [os.path.join(dst_root, item) for item in items]
        
        for src_dir, dst_dir in zip(src_dirs, dst_dirs):
            shutil.move(src_dir, dst_dir)
            
        remove_empty_folders(curr_root)
