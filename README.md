Anylfest provides and API for parsing and analyzing an AndroidManifest.xml file. It requires the following to function as intended:
 - apktool (https://code.google.com/p/android-apktool/)
 - android sdk (http://developer.android.com/sdk/index.html)

Takes in an AndroidManifest file and parses it into an object tree. It has API methods:

  Returns Boolean:
    hasLocationPermission
    isDebuggable

  Returns List:
    getExportedActivity
    getExportedService
    getExportedProvider
    getExportedReceiver
    getSecretCodes
    getSensitivePermissions
    getHiddenMenuActivities