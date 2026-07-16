from os import scandir, listdir, rmdir

def sanitize_name(full_str: str, blacklist: str):
    clean = full_str
    for ch in blacklist:
        clean = clean.replace(ch, "")
    return clean

def remove_empty_folders(path):
    with scandir(path) as it:
        for item in it:
            if item.is_dir() and len(listdir(item.path)) == 0:
                rmdir(item.path)