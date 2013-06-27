class Node(object):
  """
  All manifest objects inherit from this class
  """
  def __init__(self, obj, parent_map):
    self.xmlns = '{http://schemas.android.com/apk/res/android}'
    self._wrapper_obj = obj
    self._parent_map = parent_map
    return

  def __getattr__(self, attrname):
    return getattr(self._wrapper_obj, attrname)

  def _getActions(self):
    ret_list = list()
    
    for intents in self._wrapper_obj.getchildren():
      if intents.tag == 'intent-filter':
        for actions in intents.getchildren():
          if actions.tag == 'action':
            ret_list.append(actions.attrib["{0}name".format(self.xmlns)])
    return ret_list

class Manifest(Node):
  """
  A class for the Android Manifest uses-permission tag

  Attributes:
    -
  """
  def __init__(self, obj, parent_map):
    Node.__init__(self, obj, parent_map)
    try:
      self.sharesUID = (obj.attrib["{0}sharedUserId".format(self.xmlns)] == 'android.uid.system')
    except:
      self.sharesUID = False
  
  def __repr__(self):
    retstr = "This is a manifest object\n"
    for k, v in self._wrapper_obj.attrib.iteritems():
      retstr += "[%r]: %r\n" % (k,v)
    return retstr

class Activity(Node):
  """

  """
  def __init__(self, obj, parent_map):
    Node.__init__(self, obj, parent_map)
    self.tag = obj.tag
    self.name = obj.attrib["{0}name".format(self.xmlns)]
    self.exported = obj.attrib["{0}exported".format(self.xmlns)]
    self.fmtstr = ""

  def __repr__(self):
    return self.fmtstr

  def _isProtected(self):
    return self._wrapper_obj.attrib.has_key("{0}permission".format(self.xmlns)) or\
           self._parent_map[self._wrapper_obj].attrib.has_key("{0}permission".format(self.xmlns))


class Activity_alias(Node):
  """

  """
  def __init__(self, obj, parent_map):
    Node.__init__(self, obj, parent_map)
    self.tag = obj.tag
    self.name = obj.attrib["{0}name".format(self.xmlns)]
    self.exported = obj.attrib["{0}exported".format(self.xmlns)]

  def __repr__(self):
    return ""

  def _isProtected(self):
    return self._wrapper_obj.attrib.has_key("{0}permission".format(self.xmlns)) or\
           self._parent_map[self._wrapper_obj].attrib.has_key("{0}permission".format(self.xmlns))


class Service(Node):
  """
  http://developer.android.com/guide/components/services.html

  """
  def __init__(self, obj, parent_map):
    Node.__init__(self, obj, parent_map)
    self.tag = obj.tag
    self.name = obj.attrib["{0}name".format(self.xmlns)]
    self.exported = obj.attrib["{0}exported".format(self.xmlns)]
    self.fmtstr = ""

  def __repr__(self):
    return self.fmtstr

  def _isProtected(self):
    return self._wrapper_obj.attrib.has_key("{0}permission".format(self.xmlns))

class Receiver(Node):
  """
  A class for the Android Manifest receiver tag

  Attributes:
    -
  """
  def __init__(self, obj, parent_map):
    Node.__init__(self, obj, parent_map)
    self.tag = obj.tag
    self.name = obj.attrib["{0}name".format(self.xmlns)]
    self.exported = obj.attrib["{0}exported".format(self.xmlns)]
    self.fmtstr = ""

  def __repr__(self):
    return self.fmtstr

  def _isProtected(self):
    return self._wrapper_obj.attrib.has_key("{0}permission".format(self.xmlns)) or\
           self._parent_map[self._wrapper_obj].attrib.has_key("{0}permission".format(self.xmlns))

class Provider(Node):
  """
  A class for the Android Manifest provider tag

  Attributes:
    -
  """
  def __init__(self, obj, parent_map):
    Node.__init__(self, obj, parent_map)
    self.tag = obj.tag
    self.name = obj.attrib["{0}name".format(self.xmlns)]
    self.exported = obj.attrib["{0}exported".format(self.xmlns)]
    self.fmtstr = ""

  def __repr__(self):
    # TODO: SQL statement here
    return self.fmtstr

  def _isProtected(self):
    return self._wrapper_obj.attrib.has_key("{0}permission".format(self.xmlns))

class Permission(object):
  """
  A class for the Android Manifest permission tag

  Attributes:
    -
  """
  def __init__(self, obj, parent_map):
    Node.__init__(self, obj, parent_map)

  def __repr__(self):
    return ""

class Uses_permission(Node):
  """
  A class for the Android Manifest uses-permission tag

  Attributes:
    -
  """
  android_perm_list = []
  custom_perm_list = []
  
  def __init__(self, obj, parent_map):
    Node.__init__(self, obj, parent_map)
    self.location_perms = ['android.permission.ACCESS_FINE_LOCATION',\
                           'android.permission.ACCESS_COARSE_LOCATION',\
                           'android.permission.ACCESS_LOCATION_EXTRA_COMMANDS',\
                           'android.permission.INSTALL_LOCATION_PROVIDER']
    
    self.sensitive_perms = ['android.permission.CAMERA',\
                            'android.permission.READ_SMS',\
                            'android.permission.RECEIVE_SMS',\
                            'android.permission.SEND_SMS',\
                            'android.permission.WRITE_SMS',
                            'android.permission.BROADCAST_SMS',\
                            'android.permission.WRITE_CALL_LOG',\
                            'android.permission.WRITE_CONTACTS',\
                            'android.permission.READ_CALL_LOG',\
                            'android.permission.READ_CONTACTS']
    
    self._getPermissions()

  def __repr__(self):
    retstr = '\nAndroid Permissions:\n'
    for perm in Uses_permission.android_perm_list:
      retstr += perm + '\n'
    retstr += '\nCustom Permissions:\n'
    for perm in Uses_permission.custom_perm_list:
      retstr += perm + '\n'
    return retstr

  def _getPermissions(self):
    if self._wrapper_obj.attrib['{http://schemas.android.com/apk/res/android}name'].startswith("android."):
      Uses_permission.android_perm_list.append(self._wrapper_obj.attrib['{http://schemas.android.com/apk/res/android}name'])
    else:
      Uses_permission.custom_perm_list.append(self._wrapper_obj.attrib['{http://schemas.android.com/apk/res/android}name'])

  def _hasLocationPermission(self):
    return self._wrapper_obj.attrib['{http://schemas.android.com/apk/res/android}name'] in self.location_perms

  def _getSensitivePermissions(self):
    perm = self._wrapper_obj.attrib['{http://schemas.android.com/apk/res/android}name']
    return (perm in self.sensitive_perms, perm)
    

class IntentFilter(object):
  """
  A class for the Android Manifest intent-filter tag

  Attributes:
    -
  """
  def __init__(self, obj, parent_map):
    Node.__init__(self, obj, parent_map)

  #def __repr__(self):
  #  return ""



class Application(Node):
  """

  """
  def __init__(self, obj, parent_map):
    Node.__init__(self, obj, parent_map)
    try:
      self.debuggable = (obj.attrib["{0}debuggable".format(self.xmlns)] == 'true')
    except:
      self.debuggable = False      

  def __repr__(self):
    return ""

class Data(Node):

  def __init__(self, obj, parent_map):
    Node.__init__(self, obj, parent_map)

  def _hasSecretCode(self):
    if self._wrapper_obj.attrib.has_key('{http://schemas.android.com/apk/res/android}scheme'):
      return (self._wrapper_obj.attrib['{http://schemas.android.com/apk/res/android}scheme'].find('secret_code') != -1)
    else:
      return False

  def _hasPermission(self):
    return (self._parent_map[self._parent_map[\
            self._wrapper_obj]].attrib.has_key(\
            '{http://schemas.android.com/apk/res/android}permission'))

  def _getHost(self):
    for each_child in self._parent_map[self._wrapper_obj].getchildren():
      if each_child.tag == "data" and each_child.attrib.has_key('{http://schemas.android.com/apk/res/android}host'):
        return each_child.attrib['{http://schemas.android.com/apk/res/android}host']

  def _getName(self):
    return self._parent_map[self._parent_map[self._wrapper_obj]].attrib['{http://schemas.android.com/apk/res/android}name'].split('.')[-1]

  def _getSecretCode(self, manifest):
    if not self._hasPermission():
      return self._getName() + ' (' + manifest.attrib["package"] + ') : ' + '*#*#%s#*#*' % self._getHost()
    else:
      return self._getName() + " Secret Codes are secured by permissions"