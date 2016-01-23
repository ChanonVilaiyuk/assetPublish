''' rig '''
import maya.cmds as mc
import maya.mel as mm
import os, sys

def publish(asset) : 
	result = dict()
	result1 = exportRig(asset)

	result.update(result1)

	return result

def exportRig(asset) : 
	from tool.utils.batch import rigPublish
	reload(rigPublish)
	refPath = asset.getPath('ref')
	refFile = asset.getRefNaming('anim')
	src = asset.thisScene()
	dst = '%s/%s' % (refPath, refFile)
	rigPublish.run(src, dst)
	return {'Export %s' % refFile: {'status': True, 'message': ''}}