from mutagen.flac import FLAC
from src.utils import sanitize_name, remove_empty_folders
from math import ceil
from pathlib import Path
from lrclib import LrcLibAPI
from time import sleep
import os
import requests

BAD_CHARACTERS = "\\/:*?\"|<>"
GET_ENDPOINT_URL = "https://lrclib.net/api/get"
LYRICS_EXTENSIONS = [
  'yaml',
  'yml',
  'lrc',
  'txt'
]

def musiclib_sort(dir: str):
  dir_root = Path(dir)
  
  os.makedirs(dir_root, exist_ok=True)
  
  # ----------------------------------------------------
  # Will probably be used for /api/search endpoint later
  # ----------------------------------------------------
  # api = LrcLibAPI(user_agent="local-musiclib/1.1.0")
  
  req = {
    "url": GET_ENDPOINT_URL,
    "headers": {
        "User-Agent": "local-musiclib/1.1.0"
      },
    "params": {
      "track_name": "",
      "artist_name": "",
      "album_name": "",
      "duration": 0,
    }
  }

  with os.scandir(dir_root) as items:
    for item in items:
      if item.is_file() and item.name.endswith('flac'):
        # --- Part 1 of script ---
        # Rename music file to metadata["TRACKNUMBER"] - metadata["TITLE"].flac
        item_path = dir_root / item.name
        metadata = FLAC(item_path)
        
        file_name = sanitize_name(full_str=metadata["TITLE"][0] + ".flac", blacklist=BAD_CHARACTERS)
        track_number = metadata["TRACKNUMBER"][0].split("/")[0].zfill(3)
        
        src_path = item_path
        dst_path = Path(os.path.join(dir_root, file_name))
        
        if src_path != dst_path:
          os.replace(src=src_path, dst=dst_path)
        
        # --- Part 2 of the script ---
        # Put song in album/tracknum - title/title.flac directory
        album_name = metadata["ALBUM"][0].replace("/", "-").replace("\\", "-")
        album_name = Path(sanitize_name(full_str=album_name, blacklist=BAD_CHARACTERS))
        
        track_folder = (track_number + " - " + file_name.split(".flac")[0]).replace("/", "-").replace("\\", "-")
        track_folder = Path(sanitize_name(full_str=track_folder, blacklist=BAD_CHARACTERS))
        
        final_path = dir_root / Path(album_name / track_folder) / file_name
        
        src_path = dst_path
        dst_path = final_path
        
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        os.replace(src=src_path, dst=dst_path)
        
        # --- Part 3 of the script ---
        # Search for lyrics using lrclibapi, clear embedded LYRICS tag if exists, don't search for lyrics if file already exists
        lyrics_path = dst_path.parent / dst_path.stem
        
        exist_paths = [
          f"{lyrics_path}.{ext}" for ext in LYRICS_EXTENSIONS
        ]
        
        exist_paths = [
          Path(path).exists() for path in exist_paths
        ]
        
        title = sanitize_name(metadata["TITLE"][0], blacklist=BAD_CHARACTERS)
        artist = sanitize_name(metadata["ARTIST"][0], blacklist=BAD_CHARACTERS)
        album = sanitize_name(metadata["ALBUM"][0], blacklist=BAD_CHARACTERS)
        duration = ceil(metadata.info.length)
        
        log_identifier = f"{artist}/{album}/{title} ({int(duration / 60)}:{str(duration % 60).zfill(2)})"
        
        if not any(exist_paths):
          print(f"\n\u27a1  SEARCHING LYRICS FOR {log_identifier}")

          req["params"]["track_name"] = title
          req["params"]["artist_name"] = artist
          req["params"]["album_name"] = album
          req["params"]["duration"] = duration
          
          resp = requests.get(
            url=req["url"],
            headers=req["headers"],
            params=req["params"],
          )
          
          # Wait 500ms before the next request to respect rate limiting
          sleep(0.5)
          
          track_data = resp.json()
          extension = ""
          
          if resp.status_code == 200:
            if track_data.get("instrumental"):
              print(f"\t└──[INSTRUMENTAL]")
              lyrics = '[Instrumental]'
              extension = LYRICS_EXTENSIONS[2] # .lrc
            else:
              if track_data.get("lyricsfile"):
                print(f"\t└──[FOUND LYRICSFILE]")
                lyrics = track_data.get("lyricsfile")
                extension = LYRICS_EXTENSIONS[0] # .yaml
              else:
                print("\t└──[COULDN'T FIND LYRICSFILE, SEARCHING FOR SYNCEDLYRICS]...")
                if track_data.get("syncedLyrics"):
                  print(f"\t\t└──[FOUND SYNCEDLYRICS]")
                  lyrics = track_data.get("syncedLyrics")
                  extension = LYRICS_EXTENSIONS[2] # .lrc
                else:
                  print("\t\t└──[COULDN'T FIND SYNCEDLYRICS, SEARCHING FOR PLAINLYRICS]...")
                  if track_data.get("plainLyrics"):
                    print("\t\t\t└──[FOUND PLAINLYRICS]")
                    lyrics = track_data.get("syncedLyrics")
                    extension = LYRICS_EXTENSIONS[3] # .txt
                  else:
                    print("\t\t\t└──[COULDN'T FIND PLAINLYRICS, DEFAULTING TO INSTRUMENTAL]")
                    lyrics = '[Instrumental]'
                    extension = LYRICS_EXTENSIONS[2] # .lrc
            
            lyrics_path = Path(f"{lyrics_path}.{extension}")
            
            with open(lyrics_path, 'w', encoding='utf-8') as file:
              file.write(lyrics)
            
            metadata = FLAC(dst_path)
            
            metadata.pop('LYRICS', None)
            metadata.pop('LYRICIST', None)
            metadata.pop('UNSYNCEDLYRICS', None)
            
            metadata.save()
          
          elif resp.status_code == 404:
            print(f"\t└──[COULDN'T FIND LYRICS FOR {log_identifier}), DEFAULTING TO INSTRUMENTAL]...")
            ## ------------------------------------------------
            ## Maybe prompt user to resort to /api/search here?
            ## ------------------------------------------------
            lyrics = '[Instrumental]'
            extension = LYRICS_EXTENSIONS[2] # .lrc
            lyrics_path = Path(f"{lyrics_path}.{extension}") # .lrc
            with open(lyrics_path, 'w', encoding='utf-8') as file:
                file.write(lyrics)
        
        else:
          print(f'\n\u27a1  LYRICS ALREADY EXIST FOR {log_identifier}, SKIPPING...')
      # --- Part 4 of the script ---
      # Remove deleted songs' old empty folders
      elif item.is_dir():
        if not os.listdir(item.path):
          os.rmdir(item.path)
          continue
        
        # Remove deleted album's old empty folders
        remove_empty_folders(item.path)