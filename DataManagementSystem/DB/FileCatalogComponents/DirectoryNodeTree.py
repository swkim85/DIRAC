########################################################################
# $HeadURL:  $
########################################################################

""" DIRAC FileCatalog component representing a directory tree with simple
    nodes
"""

__RCSID__ = "$Id:  $"

import time
from DIRAC import S_OK, S_ERROR

class DirectoryNodeTree:
  """ Class managing Directory Tree as a self-linked structure with directory 
      names stored in each node
  """
  
  def __init__(self, database=None):
    """ Constructor
    """
    self.db = database
    
  def setDatabase(self,database):
    
    self.db = database   
    
  def findDir(self,path):
    """ Find the identifier of a directory specified by its path
    """
    dpath = path 
    if path[1] == "/":
      dpath = path[1:]  
    elements = dpath.split('/')
    
    req = " "
    for level in range(len(elements),0,-1):
      if level > 1:
        req += "SELECT DirID from FC_DirectoryTreeM WHERE Level=%d AND DirName='%s' AND Parent=(" % (level,elements[level-1])
      else:
        req += "SELECT DirID from FC_DirectoryTreeM WHERE Level=%d AND DirName='%s'" % (level,elements[level-1])       
    req += ")"*(len(elements)-1)    
    #print req
    result = self.db._query(req)
    #print "in findDir",result
    if not result['OK']:
      return result
    if not result['Value']:
      return S_OK(0)
    
    return S_OK(result['Value'][0][0])  

  def makeDir(self,path):
    """ Create a single directory
    """
    result = self.findDir(path)
    if not result['OK']:
      return result
    dirID = result['Value']
    if dirID:
      return S_OK(dirID)     
    
    dpath = path 
    if path[1] == "/":
      dpath = path[1:]  
    elements = dpath.split('/')
    level = len(elements)
    dirName = elements[-1]
    
    result = self.getParent(path)
    if not result['OK']:
      return result
    parentDirID = result['Value']
    
    names = ['DirName','Level','Parent']
    values = [dirName,level,parentDirID]
    result = self.db._insert('FC_DirectoryTreeM',names,values)
    if not result['OK']:
      return result
    return S_OK(result['lastRowId'])
  
  def existsDir(self,path):
    """ Check the existence of a directory at the specified path
    """
    result = self.findDir(path)
    if not result['OK']:
      return result
    if not result['Value']:
      return S_OK({"Exists":False})
    else:
      return S_OK({"Exists":True,"DirID":result['Value']})  
    
  def getParent(self,path):
    """ Get the parent ID of the given directory
    """  
    dpath = path 
    if path[1] == "/":
      dpath = path[1:]  
    elements = dpath.split('/')    
    if len(elements) > 1:
      parentDir = os.path.dirname(path)      
      result = self.findDir(parentDir)
      if not result['OK']:
        return result
      parentDirID = result['Value']
      if not parentDirID:
        return S_ERROR('No parent directory') 
      return S_OK(parentDirID)
    else:
      return S_OK(0)
    
  def getParentID(self,dirID):
    """
    """
    
    if dirID == 0:
      return S_ERROR('Root directory ID given')
    
    req = "SELECT Parent FROM FC_DirectoryTreeM WHERE DirID=%d" % dirID
    result = self._query(req)
    if not result['OK']:
      return result
    if not result['Value']:
      return S_ERROR('No parent found')
    
    return S_OK(result['Value'][0][0])
  
  def getDirectoryName(self,dirID):
    """ Get directory name by directory ID
    """
    req = "SELECT DirName FROM FC_DirectoryTreeM WHERE DirID=%d" % int(dirID)
    result = self._query(req)
    if not result['OK']:
      return result
    if not result['Value']:
      return S_ERROR('Directory with id %d not found' % int(dirID) )
    
    return S_OK(result['Value'][0][0])
  
  def getDirectoryPath(self,dirID):
    """ Get directory path by directory ID
    """
    
    dirPath = ''
    dID = dirID
    while 1:
      result = self.getDirectoryName(dID)
      if not result['OK']:
        return result
      dirPath.prepend('/'+result['Value'])
      result = self.getParentID(dID)
      if not result['OK']:
        return result
      if result['Value'] == 0:
        break
      else:
        dID = result['Value']
        
    return S_OK('/'+dirPath)
  
  def getPathIDs(self,path):
    """ Get IDs of all the directories in the parent hierarchy
    """    
    result = self.findDir(path)
    if not result['OK']:
      return result
    dID = result['Value']
    parentIDs = []
    while 1:
      result = self.getParent(dID)
      if not result['OK']:
        return result
      dID = result['Value']
      parentIDs.prepend(dID)
      if dID == 0:
        break
       
    parentIDs.prepend(0)
    return S_OK(parentIDs)
    
  def getChildren(self,path):
    """ Get child directory IDs for the given directory 
    """  
    if type(path) in StringTypes:
      result = self.findDir(path)
      if not result['OK']:
        return result
      dirID = result['Value']
    else:
      dirID = path
        
    req = "SELECD DirID FROM FC_DirectoryTreeM WHERE Parent=%d" % dirID
    result = self._query(req)
    if not result['OK']:
      return result
    if not result['Value']:
      return S_OK([])
    
    return S_OK([ x[0] for x in result['Value'] ])