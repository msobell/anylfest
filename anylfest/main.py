#!/usr/bin/python
"""
This file implements the anylfest API and performs preliminary analysis on AndroidManifest.xml files.
"""
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
	parser.add_argument('-m','--perm-map', action='store_true', default=True,
		help='Create a map of custom permissions and which apps request them. Default true.')

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

	apkdb = []
	stash = {
		"provider_violator": [],
		"secret_code": [],
		"hidden_menu": [],
		"debuggable_app": [],
		"uid_app": [],
		"custom_perms": []
		}

	# Send the files off to loader to get parsed
	for curr_file in files:
		i += 1
		try:
			lobj['file'+str(i)] = loader.Loader(curr_file)
		except:
			print "error parsing file %s" % str(i)

	for apk in lobj.keys():
		# initialize apk data structure
		current = {}

		current["package"] = lobj[apk].manifest.attrib["package"]
		picky_package = 'com.google' not in current["package"] and 'com.android' not in current["package"]
		if args.verbose:
			print "Picky package returned",picky_package

		if (not args.picky) or (args.picky and picky_package):

			##############
			# DEBUGGABLE
			##############
			try:
				current["debuggable"] = lobj[apk].isDebuggable()

				if current["debuggable"]:
					stash["debuggable_app"].append(lobj[apk].manifest.attrib["package"])

			except Exception, e:
				print "PROBLEM: %s" % e # Debugging help
				current["debuggable"] = False 


			##############
			# UID SHARE 
			##############
			try:
				current["sharesUID"] = lobj[apk].isUIDShare()

				if current["sharesUID"]:
					stash["uid_app"].append(lobj[apk].manifest.attrib["package"])

			except Exception, e:
				print "PROBLEM: %s" % e # Debugging help
				current["sharesUID"] = False

			# map is hackish method of casting all items as strings for serialization purposes
			current["codes"] = map(str, lobj[apk].getSecretCodes())
			current["activities"] = map(str, lobj[apk].getExportedActivity())
			current["services"] = map(str, lobj[apk].getExportedService())
			current["receivers"] = map(str, lobj[apk].getExportedReceiver())
			current["providers"] = map(str, lobj[apk].getExportedProvider())
			current["menus"] = map(str, lobj[apk].getHiddenMenuActivities())
			current["cust_perms"] = map(str, lobj[apk].getCustomPermissions())
			current["uses_perms"] = map(str, lobj[apk].getUsesPermissions())

			# do_the_thing just iterates through the 3rd arg and prints it 
			pretty_print("Package: %s\n" % current["package"])
			pretty_print("Debuggable: %s\n" % current["debuggable"])
			pretty_print("Shares System UID: %s\n" % current["sharesUID"])
			do_the_thing(1,"List of secret codes:", current["codes"])
			do_the_thing(2,"List of exported activities:",current["activities"])
			do_the_thing(3,"List of exported services:",current["services"])
			do_the_thing(4,"List of exported broadcast receivers:",current["receivers"])
			do_the_thing(5,"List of exported content providers:",current["providers"])
			do_the_thing(6,"Potential hidden menu activities:",current["menus"])
			do_the_thing(7,"List of custom permissions defined:",current["cust_perms"])
			do_the_thing(8,"List of permissions requested:",current["uses_perms"])

			stash["secret_code"] += current["codes"]
			stash["provider_violator"] += current["providers"]
			stash["hidden_menu"] += current["menus"]
			stash["custom_perms"] += current["cust_perms"]

			# add to the overall database
			apkdb.append(current)

		pretty_print("---------------===== END OF MANIFEST =====---------------")

	###############
	## Synopsis
	###############
	end_print("Unprotected provider stash:",stash["provider_violator"])
	end_print("Hidden code stash:", stash["secret_code"])
	end_print("Hidden menu stash:", stash["hidden_menu"])
	end_print("Debuggable app stash:", stash["debuggable_app"])
	end_print("UID Sharing stash:", stash["uid_app"])
	end_print("Custom perms stash:", stash["custom_perms"])

	#######################
	## Export to database (depending on flag?)
	#######################
	import json
	db = "anylfest.db" # TODO: set depending on flag?
	with open(db, 'w') as outfile:
		json.dump(apkdb,outfile)

if __name__ == '__main__':
		main()
