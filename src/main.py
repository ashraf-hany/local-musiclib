from src.move import musiclib_move
from src.sort import musiclib_sort
from argparse import ArgumentParser
from re import fullmatch

PATH_REGEX = r"^[a-zA-Z]{1}:{1}[\\/]{1}([\w.-]+(\s+[\w.-]+)*[\\/]?)*$"

def main():
  path_ok: dict[str, bool] = {}

  parser = ArgumentParser(
    prog="musiclib",
    description="Local Music Library ID3Tags-Based Manager",
    usage="python -m src.main"
  )

  sub = parser.add_subparsers(dest="command", help="Available application modes")

  parser_move = sub.add_parser("move", help="move(src, dst): Move all .flac files recursively from source to destination root")
  parser_move.add_argument("--src", type=str, required=True, help="Source root path")
  parser_move.add_argument("--dst", type=str, required=True, help="Destination path")
  
  parser_sort = sub.add_parser("sort", help="sort(dir): Sort all .flac files found in the given root directory based on ID3 tags")
  parser_sort.add_argument("--dir", type=str, required=True, help="Directory to sort the .flac files in")
  
  parser_aio = sub.add_parser("aio", help="aio(src, dst): All-in-one, calls move(src, dst) then sort(dst)")
  parser_aio.add_argument("--src", type=str, required=True, help="Source root path")
  parser_aio.add_argument("--dst", type=str, required=True, help="Destination path")

  args = parser.parse_args()

  if args.command == "move":
    path_ok[args.src] = True if fullmatch(PATH_REGEX, args.src) else False
    path_ok[args.dst] = True if fullmatch(PATH_REGEX, args.dst) else False
    
    for key, val in path_ok.items():
      if not val:
        e = f"[{key}] is not a valid path. Re-run the script."
        raise ValueError(e)
    
    musiclib_move(src=args.src, dst=args.dst)

  elif args.command == "sort":
    path_ok[args.dir] = True if fullmatch(PATH_REGEX, args.dir) else False
    
    for key, val in path_ok.items():
      if not val:
        e = f"[{key}] is not a valid path. Re-run the script."
        raise ValueError(e)
  
    musiclib_sort(dir=args.dir)
    
  elif args.command == "aio":
    path_ok[args.src] = True if fullmatch(PATH_REGEX, args.src) else False
    path_ok[args.dst] = True if fullmatch(PATH_REGEX, args.dst) else False
    
    for key, val in path_ok.items():
      if not val:
        e = f"[{key}] is not a valid path. Re-run the script."
        raise ValueError(e)
      
    musiclib_move(src=args.src, dst=args.dst)
    musiclib_sort(dir=args.dst)

if __name__ == "__main__":
  main()