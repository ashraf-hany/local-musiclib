import argparse
import jsonlines
import difflib
from src.move import musiclib_move
from src.sort import musiclib_sort
from src.aio import musiclib_aio
import os
from sys import argv, exit
from platform import system
from re import compile

if system() == "Windows":
  PATH_REGEX = r"^[a-zA-Z]:[\\/]([\w.-]+(\s+[\w.-]+)*[\\/]?)*$"
elif system() == "Linux":
  PATH_REGEX = r"^/([\w.-]+(\s+[\w.-]+)*/?)*$"

COMPILED_REGEX = compile(PATH_REGEX)

def main():
  path_ok: dict[str, bool] = {}
  cmd_hist_file = "./log/past_command.jsonl"
  
  # Ensure logging directory is created, if git didn't create it already
  os.makedirs(os.path.dirname(cmd_hist_file), exist_ok=True)
  
  hist_exec = True

  parser = argparse.ArgumentParser(
    prog="musiclib",
    description="Local Music Library ID3Tags-Based Manager",
    usage="python -m src.main [move|sort|aio] [POSARG|PATH...]",
  )

  sub = parser.add_subparsers(dest="command", required=True, metavar="")

  parser_move = sub.add_parser("move", help="move(src, dst): Move all .flac files recursively from source to destination root")
  parser_move.add_argument("src", type=str, help="Source root path")
  parser_move.add_argument("dst", type=str, help="Destination path")
  
  parser_sort = sub.add_parser("sort", help="sort(dir): Sort all .flac files found in the given root directory based on ID3 tags")
  parser_sort.add_argument("dir", type=str, help="Directory to sort the .flac files in")
  
  parser_aio = sub.add_parser("aio", help="aio(src, dst): All-in-one, calls move(src, dst) then sort(dst)")
  parser_aio.add_argument("src", type=str, help="Source root path")
  parser_aio.add_argument("dst", type=str, help="Destination path")

  # User ran default with no arguments, or less than required arguments
  if len(argv) == 1:
    # Old command file exists, use it
    if os.path.exists(cmd_hist_file) and os.path.getsize(cmd_hist_file) != 0:
      raw_cmd_hist = []
      cmd_hist: list[list[str]] = []
      
      with jsonlines.open(cmd_hist_file, mode="r") as rd:
        for ln in rd:
          raw_cmd_hist.append(ln)

      for c, a in raw_cmd_hist:
        cmd_hist.append([c] + a)
        
      print("Found past command(s) in the history file, the command(s) are: ( \n", end="")
      for i, cmd in enumerate(cmd_hist):
        print(f"\t[{i+1}] {" ".join(cmd)}" , end=", \n" if i < len(cmd_hist) - 1 else "\n")
      print(")\n")
      
      print("Would you like to run the same command(s) as last time? [Y/n] ", end="")
      inp = input().lower()
      if inp:
        if inp in ['y', 'n']:
          hist_exec = False if inp == 'n' else True
        else:
          raise ValueError(f"[{inp}] is not a valid choice. Re-run the script")
      else:
        pass
      
      ## Execute the command
      if hist_exec:
        for cmd in cmd_hist:
          args = parser.parse_args(cmd)

          match args.command:
            case "move":
              musiclib_move(src=args.src, dst=args.dst)
            case "sort":
              musiclib_sort(dir=args.dir) 
            case "aio":
              musiclib_aio(src=args.src, dst=args.dst)
      
      else:
        exit("Please re-run the script providing the required arguments. Type in -h for more info.")
        
    # Intentionally crash the program
    else:
      parser.parse_args()
  
  # User provided custom arguments
  else:
    s_com_opts = []
    arg_opts = set()
    
    ## Store all available program modules
    s_com_opts = [action for action in parser._actions if type(action) == argparse._SubParsersAction]
    
    for scom_opt in s_com_opts:
      s_com_opts = list(scom_opt.choices.keys())
    
    ## Store all available sub-command arguments
    sub_parsers = [parser_move, parser_sort, parser_aio]
    for p in sub_parsers:
      parser_opts = [opt for opt in (action.dest for action in p._actions if type(action) != argparse._HelpAction)]
      for opt in parser_opts:
        arg_opts.add(opt)
      
    ## Remove positional argument names if entered by accident
    raw_args = [arg for arg in argv[1:]]
    filt_args = [arg for arg in raw_args.copy() if arg not in arg_opts]
    path_args = [arg for arg in filt_args.copy() if arg not in s_com_opts]
    
    ## Check if user mistyped one of the commands
    for arg in path_args:
      matches = difflib.get_close_matches(arg, s_com_opts)
      
      ### Another check to make sure its not a path
      if matches and not COMPILED_REGEX.fullmatch(arg):
        raise(ValueError(f"[{arg}] is not a valid command. Did you mean '{matches[0]}'?"))

    ## Check if path arguments are valid
    for path in path_args:
      path_ok[path] = True if COMPILED_REGEX.fullmatch(path) else False
      
      for key, val in path_ok.items():
        if not val:
          e = f"[{key}] is not a valid path. Re-run the script."
          raise ValueError(e)
    
    ## Start logging command to file
    s_com_log: list[list[str]] = []
    
    while filt_args:
      s_com = filt_args.pop(0)
      s_com_args = []

      ### Check if user entered the command without its required arguments before parsing
      match s_com:
        case "move" | "aio":
          if len(filt_args) < 2:
            raise ValueError(f"Not enough arguments for command [{s_com}]. Re-run the script.")
          else:
            s_com_args = [filt_args.pop(0), filt_args.pop(0)]
        case "sort":
          if len(filt_args) < 1:
            raise ValueError(f"Not enough arguments for command [{s_com}]. Re-run the script.")
          else:
            s_com_args = [filt_args.pop(0)]
      
      s_com_log.append([s_com, s_com_args])
      
    
    with jsonlines.open(cmd_hist_file, mode="w") as wr:
      for c, a in s_com_log:
        wr.write([c, a])
    
    ## Parse commands one by one to feed to parser
    cmd_list: list[list[str]] = []
    for cmd, args in s_com_log:
      cmd_list.append([cmd] + args)
    
    for cmd in cmd_list:
      args = parser.parse_args(cmd)
      
      match args.command:
        case "move":
          musiclib_move(src=args.src, dst=args.dst)
        case "sort":
          musiclib_sort(dir=args.dir) 
        case "aio":
          musiclib_aio(src=args.src, dst=args.dst)\
            
if __name__ == "__main__":
  main()