import os, sys 
import maya.cmds as mc 
from tool.ptAlembic import abcUtils
reload(abcUtils)
from tool.utils import entityInfo
reload(entityInfo)
from tool.utils import fileUtils
import rig
reload(rig)
import setting
reload(setting)

def exportABC(target = 'latest') : 
    """ from tool.publish.asset import assetPublish_utils as utils
    reload(utils)

    utils.exportABC('latest') """ 

    asset = entityInfo.info()
    abcDir = asset.rigDataPath('abc')
    files = fileUtils.listFile(abcDir)

    if target == 'latest' : 
        if files : 
            latest = files[-1]
            path = '%s/%s' % (abcDir, latest)
    
        else : 
            target = 'publish'

    if target == 'publish' : 
        publishFile = os.path.basename(asset.publishFile())
        abcFile = publishFile.replace('.ma', '.abc')
        path = '%s/%s' % (abcDir, abcFile)

    result = exportABCCmd(path)
        
    if result : 
        print 'Export success %s' % path



def exportABCCmd(abcFile) : 
    mc.loadPlugin("C:/Program Files/Autodesk/Maya2015/bin/plug-ins/AbcImport.mll", qt = True)

    ctrl = setting.superRootCtrl
    geoGrp = setting.exportGrp

    if mc.objExists(ctrl) : 
        start = mc.playbackOptions(q = True, min = True)
        end = mc.playbackOptions(q = True, max = True)

        # set animation 
        rig.setTurnAnimation(ctrl)

        # export abc
        result = abcUtils.exportABC(geoGrp, abcFile)

        # remove key
        rig.removeKey(ctrl, start, end)
        status = False 

        if os.path.exists(abcFile) : 
            status = True

        return status