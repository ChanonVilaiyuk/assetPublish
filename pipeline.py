''' pipeline check '''

from tool.utils import customLog
import maya.cmds as mc
import pymel.core as pm
import setting

scriptName = 'tool.publish.asset.pipeline'
logger = customLog.customLog()
logger.setLevel(customLog.DEBUG)
logger.setLogName(scriptName)


rigGrp = 'Rig_Grp'
geoGrp = 'Geo_Grp'
namespace = 'Rig'

def group() : 
	# check Geo_Grp

	if mc.objExists(geoGrp) : 
		return geoGrp

	elif mc.objExists('%s:%s' % (namespace, geoGrp)) : 
		return '%s:%s' % (namespace, geoGrp)

		
def name() : 
	geoGrp = group()
	if geoGrp : 
		try : 
			mc.select(geoGrp, hi = True)
			objs = mc.ls(sl = True, type = 'transform')
			dups = []

			for each in objs : 
				if '|' in each : 
					dups.append(each)

			mc.select(cl = True)

			if not dups : 
				return True 

			else : 
				return dups

		except Exception as e : 
			print e 
			return False


def cleanDefaultRenderLayer() : 
    layers = mc.ls(type = 'renderLayer')
    valid = 'defaultRenderLayer'
    removes = []

    if layers : 
        for each in layers : 
            if not each == valid : 
                mc.delete(each)
                logger.debug('Delete %s' % each)
                removes.append(each)

    return [True, removes]


def cleanTurtleRender() : 
    cleanNodes = [u'TurtleBakeLayerManager', u'TurtleRenderOptions', u'TurtleUIOptions', u'TurtleDefaultBakeLayer']
    removes = []

    for each in cleanNodes : 
    	if mc.objExists(each) : 
	        mc.lockNode(each, l = False)
	        mc.delete(each)
	        logger.debug('Delete %s' % each)
	        removes.append(each)

    return [True, removes]


def cleanUnknownNode() : 
    nodes = mc.ls(type = 'unknown')

    if nodes : 
        mc.delete(nodes)
    
    return [True, nodes]

def cleanDisplayLayer() : 
	valid = 'defaultLayer'
	layers = mc.ls(type = 'displayLayer')

	if layers : 
		for each in layers : 
			if not each == valid : 
				mc.delete(each)
				logger.debug('Remove layer %s' % each)

	return [True, layers]


def cleanNamespace() : 
	from tool.utils import mayaTools 
	reload(mayaTools)
	mayaTools.cleanNamespace()



def texturePath() : 
	from tool.utils import entityInfo 
	reload(entityInfo)

	nodes = mc.ls(type = 'file')
	paths = []

	if nodes : 
		for each in nodes : 
			path = mc.getAttr('%s.fileTextureName' % each)
			paths.append(path)

	asset = entityInfo.info()
	assetPath = asset.texturePath()
	invalidPath = []

	if asset.department() in setting.textureCheckStep : 
		if paths : 
			for each in paths : 
				if not assetPath in each : 
					invalidPath.append(each)

		if invalidPath : 
			return [False, invalidPath]

		else : 
			return [True, invalidPath]

	else : 
		return [True, 'Not check for this department']

def removeUnknownPlugin() : 
	from tool.utils import pipelineTools 
	reload(pipelineTools)
	result = pipelineTools.removeUnknownPlugin()

	if result : 
		return [True, result]

	else : 
		return [False, result]


def rigGrpHiddenCheck() : 
	for obj in pm.ls(type='transform'):
		obj.hiddenInOutliner.unlock()
		obj.hiddenInOutliner.set(False)

	return [True, None]