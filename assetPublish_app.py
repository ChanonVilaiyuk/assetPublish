# asset publish

#Import python modules
import sys, os, re, shutil, yaml
import subprocess
from datetime import datetime
import time

from functools import partial

#Import GUI
from qtshim import QtCore, QtGui
from qtshim import Signal
from qtshim import wrapinstance

from tool.publish.asset import assetPublishUI as ui
reload(ui)

moduleDir = sys.modules[__name__].__file__

from tool.utils import pipelineTools, fileUtils, entityInfo, projectInfo
reload(pipelineTools)
reload(fileUtils)
reload(projectInfo)

from tool.utils import entityInfo2 as entityInfo
reload(entityInfo)

# logger 
from tool.utils import customLog
reload(customLog)

scriptName = 'ptAssetPublish'
logger = customLog.customLog()
logger.setLevel(customLog.DEBUG)
logger.setLogName(scriptName)

#Import maya commands
import maya.cmds as mc
import maya.mel as mm
import maya.OpenMayaUI as mui


# If inside Maya open Maya GUI
def getMayaWindow():
    ptr = mui.MQtUtil.mainWindow()
    if ptr is None:
        raise RuntimeError('No Maya window found.')
    window = wrapinstance(ptr)
    assert isinstance(window, QtGui.QMainWindow)
    return window


class MyForm(QtGui.QMainWindow):

	def __init__(self, parent=None):
		self.count = 0
		#Setup Window
		super(MyForm, self).__init__(parent)
		# QtGui.QWidget.__init__(self, parent)
		self.ui = ui.Ui_AssetPublishWin()
		self.ui.setupUi(self)

		# icons 
		self.logo = '%s/%s' % (os.path.dirname(moduleDir), 'icons/logo.png')

		# data 
		self.asset = entityInfo.info()


		self.initFunctions()


	def initFunctions(self) : 
		# UI
		self.fillUI()


	def fillUI(self) : 
		# set Logo 
		self.setLogo()

		# set project title 
		self.setEntityInfo()


	def setLogo(self) : 
		self.ui.logo_label.setPixmap(QtGui.QPixmap(self.logo).scaled(200, 60, QtCore.Qt.KeepAspectRatio))


	def setEntityInfo(self) : 
		self.ui.assetName_label.setText('%s   -   %s' % (self.asset.name(), self.asset.task()))
		self.ui.project_label.setText(self.asset.project())
		self.ui.type_label.setText(self.asset.type())
		self.ui.subType_label.setText(self.asset.subType())
		self.ui.step_label.setText(self.asset.department())