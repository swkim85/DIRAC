########################################################################
# $HeadURL:  $
########################################################################
""" This agents feeds the ClientsCache table.
"""

from DIRAC import S_OK, S_ERROR
from DIRAC import gLogger
from DIRAC.Core.Base.AgentModule import AgentModule
from DIRAC.Core.DISET.RPCClient import RPCClient
from DIRAC.ResourceStatusSystem.DB.ResourceStatusDB import *
from DIRAC.ResourceStatusSystem.Utilities.Exceptions import *
from DIRAC.ResourceStatusSystem.Policy import Configurations
from DIRAC.ResourceStatusSystem.Client.Command.CommandCaller import CommandCaller
from DIRAC.ResourceStatusSystem.Client.Command.ClientsInvoker import ClientsInvoker

__RCSID__ = "$Id:  $"

AGENT_NAME = 'ResourceStatus/ClientsCacheFeeder'

class ClientsCacheFeeder(AgentModule):


  def initialize(self):
    """ ClientsCacheFeeder initialization
    """
    
    try:

      try:
        self.rsDB = ResourceStatusDB()
      except RSSDBException, x:
        gLogger.error(whoRaised(x))
      except RSSException, x:
        gLogger.error(whoRaised(x))
      
      self.clientsInvoker = ClientsInvoker()

      commandsList = Configurations.Commands_to_use

      self.commandObjectsList = []

      cc = CommandCaller()

      RPCWMSAdmin = RPCClient("WorkloadManagement/WMSAdministrator")

      for command in commandsList:
        cObj = cc.setCommandObject(command)
        cc.setCommandClient(command, cObj, RPCWMSAdmin = RPCWMSAdmin)
        self.commandObjectsList.append((command, cObj))
        
      return S_OK()

    except Exception:
      errorStr = "ClientsCacheFeeder initialization"
      gLogger.exception(errorStr)
      return S_ERROR(errorStr)


  def execute(self):
    """ The main ClientsCacheFeeder execution method
    """
    
    try:
      
      for co in self.commandObjectsList:
        self.clientsInvoker.setCommand(co[1])
        res = self.clientsInvoker.doCommand()
        for key in res.keys():
          self.rsDB.addOrModifyClientsCacheRes(key, co[0], res[key])
      
      return S_OK()
    
    except Exception:
      errorStr = "ClientsCacheFeeder execution"
      gLogger.exception(errorStr)
      return S_ERROR(errorStr)