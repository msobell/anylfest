#!/usr/bin/python

import subprocess
import os
import re
import shlex

class Getter(object):
	"""
	Good guy getter:

	Gets packages

	Decompiles them
	"""
	def __init__(self,oem_name="None"):
		self.packages = []
		self.model = ""
		self.debug = False
		self.filter = oem_name

	def get_device_name(self):
		""" Grab the device name from build.prop """
		q = os.popen("adb pull /system/build.prop").readlines()
		r = os.popen("cat build.prop | grep -m 1 ro.product.model -w | cut -d '=' -f2")
		model = r.read().strip()
		model = model.replace('\'','')
		model = model.replace('?','')
		model = model.replace('+','')
		model = model.replace(' ','_')
		print "Model is:  ",model
		if not os.path.isdir( model ):
			os.mkdir( model )
		os.remove( 'build.prop' )
		self.model = model

	def get_device_packages(self):
		""" Get the apks from the device and download them to the model name subdir of the current dir"""
		print '[+] Getting!'
		getstring = 'adb shell pm list packages -f '
		if self.filter is not 'None':
			getstring += self.filter
		packages = subprocess.check_output(getstring, shell=True)
		for app in packages.split('\n'):
			path = re.sub('package:','',app)
			path = re.sub('=.*','',path)
			if self.debug:
				print 'path is',path,'\nmodel is',self.model
			#cmd = 'adb pull ' + path + ' ' + os.path.abspath('.') + '/' + self.model + '/'
			cmd = 'adb pull ' + path + ' ' + self.model + '/'
			if self.debug:
				print 'checking if ' + os.path.abspath('.') + '/' + self.model + '/' + path.split('/')[-1] + ' exists'
			if not os.path.exists( self.model + '/' + path.split('/')[-1] ):
				if self.debug:
					print 'cmd is',cmd
				args = shlex.split(cmd)
				if self.debug:
					print args
				subprocess.call( args )
			self.packages.append(path.split('/')[-1][:-4])

	def decompile_dat_shit(self):
		""" Decompile the apks we got before and move them to the model subdirectory """
		print '[+] Decompiling!'
		for apk in os.listdir( self.model ):
			apk_dir = apk[:-4]
			if self.debug:
				print 'APK name',apk
				print 'Dir name',apk_dir
			if apk[-4:] == '.apk':
				if not os.path.exists( os.path.abspath('.') + '/' + self.model + '/' + apk_dir ):
					# decompile it
					# apktool d BooksTablet.apk
					cmd = 'apktool d ' + os.path.abspath('.') + '/' + self.model + '/' + apk
					subprocess.call( cmd, shell=True )
					# and move it to the model subdirectory
					# mv BooksTablet SAMSUNG-SCH747/BooksTablet
					cmd = 'mv ' + apk_dir + ' ' + self.model + '/' + apk_dir + '/'
					if self.debug:
						print 'Move command', cmd
					subprocess.call( cmd, shell=True )

	def get(self):
		self.get_device_name()
		self.get_device_packages()
		self.decompile_dat_shit()