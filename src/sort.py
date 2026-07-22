from mutagen.flac import FLAC
from src.utils import sanitize_name, remove_empty_folders
from math import ceil
from pathlib import Path
from lrclib import LrcLibAPI
import os

BAD_CHARACTERS = "\\/:*?\"|<>"

def musiclib_sort(dir: str):
  dir_root = Path(dir)
  
  os.makedirs(dir_root, exist_ok=True)
  
  api = LrcLibAPI(user_agent="local-musiclib/1.0.0")

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
        exist_paths = [Path(str(lyrics_path) + '.lrc').exists(), Path(str(lyrics_path) + '.txt').exists()]
        
        if not any(exist_paths):
          try:
            title = sanitize_name(metadata["TITLE"][0], blacklist=BAD_CHARACTERS)
            artist = sanitize_name(metadata["ARTIST"][0], blacklist=BAD_CHARACTERS)
            album = sanitize_name(metadata["ALBUM"][0], blacklist=BAD_CHARACTERS)
            duration = ceil(metadata.info.length)
            
            lyrics = api.get_lyrics(
              track_name=title,
              album_name=album,
              artist_name=artist,
              duration=duration
            )
            
            # Failsafe for if lyrics are none (put as instrumental)
            print(f"---- SEARCHING LYRICS FOR {artist}/{album}/{title} ({int(duration / 60)}:{str(duration % 60).zfill(2)}) ----")
            
            lyrics = lyrics.synced_lyrics or lyrics.plain_lyrics
            
            if lyrics is None:
              lyrics = '[Instrumental]'
            
            print(f"---- FOUND {'SYNCED' if '[' in lyrics else 'PLAIN'} LYRICS. ----\n")
            
            extension = str('.lrc' if '[' in lyrics else '.txt') or '.lrc'
            
            lyrics_path = Path(str(lyrics_path) + extension)
            
            if not lyrics_path.exists():
              with open(lyrics_path, 'w', encoding='utf-8') as file:
                if lyrics:
                  file.write(lyrics)
                else:
                  file.write('[Instrumental]')
            
            metadata = FLAC(dst_path)
            
            metadata.pop('LYRICS', None)
            metadata.pop('LYRICIST', None)
            metadata.pop('UNSYNCEDLYRICS', None)
            
            metadata.save()
          except Exception as _:
            print(f"Couldn't find lyrics for {artist}/{album}/{title} ({int(duration / 60)}:{str(duration % 60).zfill(2)}), replacing with default lyrics file")
            
            lyrics_path = Path(str(lyrics_path) + '.lrc')
            with open(lyrics_path, 'w', encoding='utf-8') as file:
                file.write('[Instrumental]')
        
        else:
          print(f'Lyrics already exists for {dst_path.stem}')
      # --- Part 4 of the script ---
      # Remove deleted songs' old empty folders
      elif item.is_dir():
        if not os.listdir(item.path):
          os.rmdir(item.path)
          continue
        
        # Remove deleted album's old empty folders
        remove_empty_folders(item.path)