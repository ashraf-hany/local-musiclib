from src.move import musiclib_move
from src.sort import musiclib_sort

def musiclib_aio(src: str, dst: str):
  musiclib_move(src=src, dst=dst)
  musiclib_sort(dir=dst)