#!/usr/bin/python
import argparse
import loader
import os
import getter

def getFiles(dirname):
  files = list()
  for r, d, f in os.walk(dirname, followlinks=True):
    for curr_file in f:
      if curr_file.startswith("AndroidManifest") and curr_file.endswith(".xml"):
        files.append(os.path.join(r, curr_file))
  print "Looking through",len(files),"files."
  return files

def pretty_print(s):
  print s

def end_print(s,l):
  # takes list, string to print
  pretty_print("\n%s" % s)
  if len(l) == 0:
    pretty_print("None. Good to go.")
  for item in l:
    pretty_print(item)

def do_the_thing(i,s,l):
  pretty_print("[%i] %s" % (i,s))
  if len(l) > 0:
    for item in l:
      pretty_print(item)
    print ""

def main():
  """
  Function Doc String
  """

  parser = argparse.ArgumentParser(description='Process some manifests.')
  parser.add_argument('-p','--path', nargs='?', default='.',
    help='Path to search for AndroidManifest.xml files. Default = current directory')
  parser.add_argument('-v','--verbose', action='store_true',
    help='Turn debugging statements on')
  parser.add_argument('--picky', action='store_true',
    help='Don\'t analyze Google and standard APKs')
  #parser.add_argument('-k','--keywords', help='Additional keywords for the hidden menu search. Default: \'test\',\'hidden\'', nargs='*') #TODO - this is wrong
  parser.add_argument('-g','--get', action='store_true',
    help='Download apks from the device via ADB. Use -f for filtering.')
  parser.add_argument('-f','--filter', nargs='?',
    help='Download only apps which has this keyword in the class name (e.g. OEM name)')
  parser.add_argument('-d','--decompile', action='store_true', default=True,
    help='Decompile applications after download.')

  args = parser.parse_args()
  path = args.path
  if args.get:
    print 'Download mode'
    if args.filter:
      g = getter.Getter(args.filter)
    else:
      g = getter.Getter()
    g.get()
    path = g.model
  print 'Running on folder',path
  if args.verbose:
    print 'Verbosity turned on'

  lobj = dict()
  i = 0

  files = getFiles(args.path)

  provider_violator_stash = list()
  secret_code_stash = list()
  hidden_menu_stash = list()
  debuggable_app_stash = list()
  uid_app_stash = list()

  # Send the files off to loader to get parsed
  for curr_file in files:
    i += 1
    try:
      lobj['file'+str(i)] = loader.Loader(curr_file)
    except:
      print "error parsing file %s" % str(i)

  for apk in lobj.keys():
    idx = 1
    package = lobj[apk].manifest.attrib["package"]
    picky_package = 'com.google' not in package and 'com.android' not in package
    if args.verbose:
      print "Picky package returned",picky_package

    if (not args.picky) or (args.picky and picky_package):

      pretty_print("Package: %s\n" % lobj[apk].manifest.attrib["package"])

      try:
        isDebug = lobj[apk].isDebuggable()
        pretty_print("Debuggable: %s" % isDebug )
        if isDebug:
          debuggable_app_stash.append(lobj[apk].manifest.attrib["package"])
      except:
        pretty_print("No debuggable attribute")

      try:
        sharesUID = lobj[apk].isUIDShare()
        pretty_print("Shares System UID: %s" % sharesUID )
        if sharesUID:
          uid_app_stash.append(lobj[apk].manifest.attrib["package"])
      except:
        pretty_print("No System UID sharing")
      
      codes = lobj[apk].getSecretCodes()
      do_the_thing(idx,"List of secret codes:",codes)
      for code in codes:
        secret_code_stash.append(code)
      idx += 1

      activities = lobj[apk].getExportedActivity()
      do_the_thing(idx,"List of exported activities:",activities)
      idx += 1

      services = lobj[apk].getExportedService()
      do_the_thing(idx,"List of exported services:",services)
      idx += 1

      receivers = lobj[apk].getExportedReceiver()
      do_the_thing(idx,"List of exported broadcast receivers:",receivers)
      idx += 1
      
      providers = lobj[apk].getExportedProvider()
      do_the_thing(idx,"List of exported content providers:",providers)
      idx += 1
      for provider in providers:
        provider_violator_stash.append(provider)

      menus = lobj[apk].getHiddenMenuActivities()
      do_the_thing(idx,"Potential hidden menu activities:",menus)
      idx += 1
      for menu in menus:
        hidden_menu_stash.append(menu)

    pretty_print("---------------===== END OF MANIFEST =====---------------")

  end_print("Unprotected provider stash:",provider_violator_stash)

  end_print("Hidden code stash:",secret_code_stash)

  end_print("Hidden menu stash:",hidden_menu_stash)

  end_print("Debuggable app stash:",debuggable_app_stash)

  end_print("UID Sharing stash:",uid_app_stash)

if __name__ == '__main__':
    main()