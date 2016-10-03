#Import python modules
import os, sys
from datetime import datetime

#Import GUI
from PySide import QtCore
from PySide import QtGui
from PySide import QtUiTools
from shiboken import wrapInstance

# Import Maya module
import maya.OpenMayaUI as mui
import maya.cmds as mc
import maya.mel as mm

from tool.utils import fileUtils, entityInfo

moduleFile = sys.modules[__name__].__file__
moduleDir = os.path.dirname(moduleFile)
sys.path.append(moduleDir)

def getMayaWindow():
    ptr = mui.MQtUtil.mainWindow()
    if ptr is not  None:
        return wrapInstance(long(ptr), QtGui.QMainWindow)

class MyForm(QtGui.QMainWindow):

    def __init__(self, parent=None):
        self.count = 0
        #Setup Window
        super(MyForm, self).__init__(parent)

        self.mayaUI = 'assetFixUI'
        deleteUI(self.mayaUI)

        self.loadUI()
        

        self.initSignals()
        self.initFunctions()

    def initSignals(self): 
        self.ui.add_pushButton.clicked.connect(self.add)
        self.ui.remove_pushButton.clicked.connect(self.remove)
        self.ui.clearAll_pushButton.clicked.connect(self.removeAll)
        self.ui.refresh_pushButton.clicked.connect(self.refreshUI)

    def initFunctions(self): 
        self.setUI()
        self.loadSet()

    def setUI(self): 
        asset = entityInfo.info()
        self.ui.asset_label.setText(asset.name())
        self.ui.department_label.setText(asset.department())
        self.ui.lod_label.setText(asset.taskLOD())

    def setName(self): 
        asset = entityInfo.info()
        date = str(datetime.now()).split(' ')[0].replace('-', '_')
        setName = '%s%s_%s_fixSet' % (asset.department(), asset.taskLOD().capitalize(), date)

        return setName

    def findSetName(self): 
        asset = entityInfo.info()
        setName = '%s%s_*_fixSet' % (asset.department(), asset.taskLOD().capitalize())
        sets = mc.ls(setName)

        if sets: 
            return sets[0]


    def createSet(self): 
        setName = self.setName()

        if not mc.objExists(setName): 
            setName = mc.sets(n=setName)

        return setName

    def loadSet(self): 
        setName = self.findSetName()

        if not setName: 
            setName = ''
        
        self.ui.set_listWidget.clear()
        if not mc.objExists(setName): 
            self.ui.set_listWidget.addItem('No Item')

        else: 
            members = mc.sets(setName, q=True)

            if members: 
                self.ui.set_listWidget.addItems(members)

            else: 
                slef.ui.set_listWidget.addItem('No Item')

    def add(self): 
        """ add objects to set """ 
        objs = mc.ls(sl=True)

        if objs: 
            setName = self.findSetName()

            if not setName: 
                setName = self.createSet()

            mc.sets(objs, add=setName)

        self.loadSet()

    def remove(self): 
        """ remove objects to set """ 
        objs = mc.ls(sl=True)
        setName = self.findSetName()

        if objs: 
            mc.sets(objs, rm=setName)

        members = mc.sets(setName, q=True)
        if not members: 
            mc.delete(setName)

        self.loadSet()

    def removeAll(self): 
        """ remove all members from set """ 
        setName = self.findSetName()

        if mc.objExists(setName): 
            mc.delete(setName) 

        self.loadSet()

    def refreshUI(self): 
        self.loadSet()
        
    def loadUI(self): 
        # read .ui directly
        loader = QtUiTools.QUiLoader()
        loader.setWorkingDirectory(moduleDir)

        f = QtCore.QFile("%s/assetFixUI.ui" % moduleDir)
        f.open(QtCore.QFile.ReadOnly)

        self.myWidget = loader.load(f, self)
        self.ui = self.myWidget

        f.close()

        self.ui.show()
        self.ui.setWindowTitle('Asset Fix Manager')

def deleteUI(ui): 
    if mc.window(ui, exists=True): 
        mc.deleteUI(ui)
        deleteUI(ui)