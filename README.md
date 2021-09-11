# bs_manager
Simple BlueStacks manager to setting root, adb and so on.

## Usage
You can run either python script ``main.py`` or windows executable file ``main.exe`` inside ``dist`` folder.
````
usage: main.py [-h] [-d DATA_DIR] [-p PROGRAM_DIR] [-a ADB_EXECUTABLE]

Simple BlueStacks manager to setting root, adb and so on.

optional arguments:
  -h, --help            show this help message and exit
  -d DATA_DIR, --data_dir DATA_DIR
                        Path to ProgramData folder
  -p PROGRAM_DIR, --program_dir PROGRAM_DIR
                        Path to ProgramFiles folder
  -a ADB_EXECUTABLE, --adb_executable ADB_EXECUTABLE
                        Path to adb.exe
````

## Build Windows exe file
1. Get pyinstaller from pypi 
    ````
    pip install pyinstaller
    ````
2. Run the command at bs_manager folder 
   ````
   pyinstaller main.py --onefile
   ````

