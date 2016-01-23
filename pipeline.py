''' pipeline check '''

from tool.utils import customLog
import maya.cmds as mc

scriptName = 'tool.publish.asset.pipeline'
logger = customLog.customLog()
logger.setLevel(customLog.DEBUG)
logger.setLogName(scriptName)


geoGrp = 'Geo_Grp'

def group() : 
	# check Geo_Grp

	if mc.objExists(geoGrp) : 
		return True


def name() : 
	if group() : 
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