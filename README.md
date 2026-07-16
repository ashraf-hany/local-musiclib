# Local Music-Lib
## About this project
This is a small personal project which helps manage a local music library. The folder structure is catered towards a structure that is most functional with the [**Navidrome**](https://github.com/navidrome/navidrome) self-hosted server (tested and running on the developer's machine). It features a simple **ArgumentParser** interface with three main modes: 

1. `move`  
└── moves files in a batch from a source directory to a destination directory.

2. `sort`  
└── sorts files in a directory based on their metadata (artist, album, etc.), and tries to find lyrics for each song using **LrcLibAPI**.

3. `aio`  
└── all-in-one mode which combines the functionalities of `move` and `sort` in a single command.

## How to use
### Pre-requisites
⚠️ This project was developed and tested using **Python 3.13**. It is recommended to use the same version or a later one.
1. Ensure you are in the root directory of the project when running commands.
```bash
$ cd local-musiclib/
```
2. Install dependencies using:
```bash
$ pip install -r ./env/requirements.txt
```
3. Proceed to directly copy the path of desired directories from your file explorer and paste them in the command line (Make sure that they are enclosed in quotes like described below).
### 1. Move mode
To move files from a source directory to a destination directory, use the following command:
```bash
$ python -m src.main move --src "/path/to/source" --dst "/path/to/destination"
```

### 2. Sort mode
To sort files in a directory based on their metadata and fetch lyrics, use the following command:
```bash
$ python -m src.main sort --dir "/path/to/directory"
```

### 3. All-in-one mode
To move files from a source directory to a destination directory and sort the destination directory in a single command, use the following command:
```bash
$ python -m src.main aio --src "/path/to/source" --dst "/path/to/destination"
```
## Future plans
1. Implement a GUI to facilitate selecting the relevant user inputs (mode, directories) instead of using command line arguments.
2. Add disc number to the sorting criteria.
3. Implement asynchronous parallel sorting to improve performance when dealing with large music libraries.