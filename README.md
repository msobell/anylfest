Anylfest
================================
Anylfest provides and API for parsing and analyzing an AndroidManifest.xml file or files.

REQUIRES
-------------------------
It requires the following tools to be installed/in the current PATH for *some* functionality to work
 - apktool (https://code.google.com/p/android-apktool/)
 - android sdk (http://developer.android.com/sdk/index.html)

RUNNING
-------------------------
Anylfest can be installed to sys.path:
```
$ sudo python setup.py install
```
In order to use the library. Alternatively, run anylfest without installation using:
```
$ python anylfest/main.py
```
And has the following options:
```
usage: main.py [-h] [-p [PATH]] [-v] [--picky] [-g] [-f [FILTER]] [-d] [-m]

Process some manifests.

optional arguments:
  -h, --help            show this help message and exit
  -p [PATH], --path [PATH]
                        Path to search for AndroidManifest.xml files. Default
                        = current directory
  -v, --verbose         Turn debugging statements on
  --picky               Don't analyze Google and standard APKs
  -g, --get             Download apks from the device via ADB. Use -f for
                        filtering.
  -f [FILTER], --filter [FILTER]
                        Download only apps which has this keyword in the class
                        name (e.g. OEM name)
  -d, --decompile       Decompile applications after download.
  -m, --perm-map        Create a map of custom permissions and which apps
                        request them. Default true.
```
FUNCTIONS
-------------------------
Its API functions are:

  Returns Boolean:
    isDebuggable
    isUIDShare

  Returns List:
    getExportedActivity
    getExportedService
    getExportedProvider
    getExportedReceiver
    getHiddenMenuActivities
    getSecretCodes
    getUsesPermissions
    getCustomPermissions

See each function's PyDocs string for a short description. None of the API calls take parameters.

TODO
-------------------------
 - [X] Add custom permissions
 - [X] Add UID sharing
 - [ ] Default intent-filter false in Android 4.1+
 - [ ] Finish mapping permissions

CONTRIBUTING
-------------------------
To contribute to anylfest, please email:
sobell@gmail.com
nitin.jami@intrepidusgroup.com