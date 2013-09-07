import xml.etree.ElementTree as ET
import model

class Loader(object):
	"""
	Takes in an AndroidManifest file and parses it into an object tree. It has API functions:

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

	TODO:
	Default intent-filter false in Android 4.1+
	Finish mapping permissions

	See each function's PyDocs string for a short description. None of the API calls take parameters.
	"""

	def __init__(self, name="AndroidManifest.xml"):
		"""
		::param:: path to AndroidManifest.xml file. Default ./AndroidManifest.xml.
		"""
	# Stuff for the XML parsing
	self.tree = ET.parse(name)
	self.xmlns = '{http://schemas.android.com/apk/res/android}'
	self.parent_map = {}
	self.manifest = None
	self.application = None

	# Android classes
	self.activity = []
	self.activity_alias = []
	self.service = []
	self.receiver = []
	self.provider = []
	self.uses_permission = []
	self.data = [] # for secret codes
	self.defines_permission = []

	self.exported_activity_list = []
	self.exported_service_list = []
	self.exported_receiver_list = []
	self.exported_provider_list = []
	
	# Don't need a class for intent filter, but need its children classes
	self.intent_filter = []
	self.action = []
	self.category = []

	# Manifest properties
	self.meta_data = []
	self.instrumentation = []
	self.uses_library = []
	self.uses_config = []
	self.secret_codes = []
	self.permission = []
	self.permission_grp = []
	self.permission_tree = []

	# Hidden menu activities
	self.exported_hidden_menu_activities = []

	# Pre-processing
	self._pre_process()
	
	# Post-processing
	self._post_process()

	############################
	## PRE-PROCESSING METHODS ##
	############################

	def _export_fix(self):
	# TODO: The default for exported should depend on the sdk version from <uses-sdk>

	# Set the tags that only have 'exported' tag...
	_required_tags = ["activity", "activity-alias", "service", "receiver", "provider"]

	# Get only those tags which have <intent-filter> as thier child...
	found_tag = [x for x in self.tree.getroot().findall(".//intent-filter/..")]

	# Parse the whole tree and set the default values for 'exported' accordingly...
	for curr_tag in self.tree.getiterator():
		# Check if the attribute is explicitly defined, if so get that value which is a
		# string and convert it to Bool respectively.
		if curr_tag.attrib.has_key("{0}exported".format(self.xmlns)):
		if curr_tag.attrib["{0}exported".format(self.xmlns)].lower() == "false":
			curr_tag.attrib["{0}exported".format(self.xmlns)] = False
		else:
			curr_tag.attrib["{0}exported".format(self.xmlns)] = True

		# If the attribute is not set explicitly, then we need to define them depending
		# upon whether alteast one <intent-filter> is specified as its child.
		else:
		# If we don't specify the following condition, 'exported' attribute will be set
		# to other tags' which orginally doesn't have this attribute at all. For eg.,
		# <manifest>. This happens because we parse the entire tree not just required
		# tags. We can do this other way by iterating thru _required_tags, but we are not.
		if curr_tag.tag in _required_tags:
			if curr_tag in found_tag:
			curr_tag.attrib["{0}exported".format(self.xmlns)] = True
			else:
			curr_tag.attrib["{0}exported".format(self.xmlns)] = False
	return

	def _mapParentChild(self):
	self.parent_map = dict((c, p) for p in self.tree.getiterator() for c in p)

	def _processActivities(self):
	for curr_obj in self.activity:
		if curr_obj.exported and not curr_obj._isProtected():
		fmtstr = ""
		multiple = False
		for curr_activity in curr_obj._getActions():
			if multiple:
			fmtstr += '\n'
			fmtstr += "adb shell am start -a %s -n %s/" \
			% (curr_activity, self.manifest.attrib["package"])
			if not (curr_obj.name[:4] == "com."):
			if curr_obj.name[0] != '.':
				fmtstr += '.'
			fmtstr += curr_obj.name
			multiple = True
		curr_obj.fmtstr += fmtstr
		self.exported_activity_list.append(curr_obj) # FLAG

	def _processServices(self):
	for curr_obj in self.service:
		if curr_obj.exported and not curr_obj._isProtected():
		fmtstr = ""
		multiple = False
		for each_action in curr_obj._getActions():
			if multiple:
			fmtstr += '\n'
			fmtstr += "adb shell am startservice -n "\
			 + self.manifest.attrib["package"] + "/"
			if not (curr_obj.name[:4] == "com."):
			#fmtstr += self.manifest.attrib["package"]
			if curr_obj.name[0] != '.':
				fmtstr += '.'
			fmtstr += curr_obj.name
			multiple = True
		curr_obj.fmtstr += fmtstr
		self.exported_service_list.append(str(curr_obj)) # FLAG - shouldn't this be a string...

	def _processProviders(self):
	for curr_obj in self.provider:
		if curr_obj.exported and not curr_obj._isProtected():
		fmtstr = self.manifest.attrib["package"] + " : " + curr_obj.name
		curr_obj.fmtstr = fmtstr
		self.exported_provider_list.append(curr_obj) # FLAG

	def _processReceivers(self):
	for curr_obj in self.receiver:
		if curr_obj.exported and not curr_obj._isProtected():
		# ./adb shell am broadcast -a android.intent.action.BOOT_COMPLETED\
		# -c android.intent.category.HOME -n net.fstab.checkit_android/.StartupReceiver
		fmtstr = ""
		multiple = False
		for each_action in curr_obj._getActions():
			#print "Each action:",each_action
			#print "Each obj:",curr_obj
			if multiple:
			fmtstr += '\n'
			fmtstr += "adb shell am broadcast -a " + each_action
			if len(self.category) > 0:
			#print self.category
			fmtstr += " -c " + self.category
			#fmtstr += " -n " + self.manifest.attrib["package"] + "/"
			#if not (curr_obj.name[:4] == "com."):
			#fmtstr += self.manifest.attrib["package"]
			#  if curr_obj.name[0] != '.':
			#    fmtstr += '.'
			#fmtstr += curr_obj.name
			multiple = True
		curr_obj.fmtstr = fmtstr
		self.exported_receiver_list.append(curr_obj)

	def _processHiddenMenuActivities(self):
	for curr_obj in self.exported_activity_list:
		#print "Looking at:",curr_obj
		for keyword in ['hidden','test']:
		if keyword in curr_obj.fmtstr.lower():
			self.exported_hidden_menu_activities.append(curr_obj)

	def _parse(self):
	for curr_tag in self.tree.getiterator():
		if curr_tag.tag == 'manifest':
		self.manifest = model.Manifest(curr_tag, self.parent_map)
		elif curr_tag.tag == 'application':
		self.application = model.Application(curr_tag, self.parent_map)
		elif curr_tag.tag == 'activity':
		self.activity.append(model.Activity(curr_tag, self.parent_map))
		elif curr_tag.tag == 'activity-alias':
		self.activity_alias.append(model.Activity_alias(curr_tag, self.parent_map))
		elif curr_tag.tag == 'service':
		self.service.append(model.Service(curr_tag, self.parent_map))
		elif curr_tag.tag == 'receiver':
		self.receiver.append(model.Receiver(curr_tag, self.parent_map))
		elif curr_tag.tag == 'provider':
		self.provider.append(model.Provider(curr_tag, self.parent_map))
		elif curr_tag.tag == 'uses-permission':
		self.uses_permission.append(model.Uses_permission(curr_tag, self.parent_map))
		elif curr_tag.tag == 'permission':
		self.defines_permission.append(model.Defines_permission(curr_tag, self.parent_map))
		elif curr_tag.tag == 'data':
		self.data.append(model.Data(curr_tag, self.parent_map))
		#elif curr_tag.tag == 'intent-filter':
		#  self.intent_filter.append(model.IntentFilter(curr_tag, self.parent_map))

	def _map_permissions(self):
	print ""

	def _post_process(self):
	self._map_permissions()

	def _pre_process(self):
	"""
	This method gets all the objects instatiated when parsing the xml file and
	wraps the objects with respective wrapper classes in model.py
	"""

	# Pre-processing methods
	self._export_fix()
	self._mapParentChild()
	self._parse()
	self._processActivities()
	self._processServices()
	self._processProviders()
	self._processReceivers()
	self._processHiddenMenuActivities()

	############################
	##       API METHODS      ##
	############################

	def isDebuggable(self):
	"""
	Returns true or false, based on the android:debuggable property in the manifest's <application> tag. Other applications or uses can run in the context of a debuggable application. Production applications should NOT be marked as debuggable.
	"""
	return self.application.debuggable

	def isUIDShare(self):
	"""
	Returns true or false, based on the android:sharedUserId="android.uid.system" property in the manifest's <manifest> tag. Applications which share a UID can access each others' /data/data/app directory, expanding the damage that can be caused by certain vulnerabilities, such as content provider directory traversal bugs.
	"""
	return self.manifest.sharesUID

	def getExportedActivity(self):
	"""
	Returns a list of exported activities. Activities are the visual portion of applications. Hidden menus are also activites and can be launched by other activities if they are exported.
	"""
	return self.exported_activity_list

	def getExportedService(self):
	"""
	Returns a list of exported services. Services run in a separate thread from the main application and can continue running after the main application has been backgrounded. Services can be bound by other processes if exported and can take in data from intents or other applications. Exported services are potentially dangerous and warrant further examination.
	"""

	return self.exported_service_list

	def getExportedProvider(self):
	"""
	Returns a list of exported content providers. Content Providers provide interprocess access to SQLite databases or an application's files. They can be vulnerable to SQL injection and directory traversal attacks. Content Providers can specify READ and WRITE permissions. Either permission set to "Null" warrants further examination.
	"""

	return self.exported_provider_list

	def getExportedReceiver(self):
	"""
	Returns a list of exported broadcast receivers. Broadcast receivers can trigger application actions or can take in data from Intent messages which gets processed by application code. They are a convenient entry point into the application.
	"""

	return self.exported_receiver_list

	def getHiddenMenuActivities(self):
	"""
	Returns a list of potential exported hidden menus. This call returns exported Activities which are suspected to be hidden application functionality.
	TODO: improve classification.
	"""

	return self.exported_hidden_menu_activities

	def getSecretCodes(self):
	"""
	Returns a list of secret codes in the manifest. Android appplications can specify secret codes which trigger application functionality. For OEM applications, this can include resetting the device or accessing hidden menus or functionality.
	"""

	for curr_data in self.data:
		#print "Getting actions", curr_data._getActions()
		if curr_data._hasSecretCode() and curr_data._getSecretCode(self.manifest) not in self.secret_codes:
		#print "Has secret code"
		self.secret_codes.append(curr_data._getSecretCode(self.manifest))
	return self.secret_codes

	def getUsesPermissions(self):
	"""
	Returns a list of the permissions the application requests at install time. Android applications must request access to system resources at install time by requesting from a standard set of Android permissions. Alternatively, an application can request a "custom" permission, defined by another application. See "getCustomPermissions" for more details.
	"""
	return self.uses_permission

	def getCustomPermissions(self):
	"""
	Returns a list of custom permissions defined by the application. Applications can create custom permissions outside of the standard set of Android permissions. The protectionLevel attribute specifies how access is granted to the permission. The user will be prompted for "normal", explicitly prompted for "dangerous", and not prompted for "signature" or "signatureOrSystem". The latter two are decided by the operating system. "signature" specifies only applications sharing the same signing certificate as the application which created the permission have access. "signatureOrSystem" expands that scope to /system/app/ (preinstalled) applications as well. The signature methods are the recommended protections for custom Android permissions.
	"""
	return self.defines_permission
