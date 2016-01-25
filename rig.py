''' rig '''
import maya.cmds as mc
import maya.mel as mm
import os, sys

from tool.utils import pipelineTools as pt
reload(pt)

def publish(asset, batch) : 
	result = dict()
	result1 = exportRig(asset, batch)

	result.update(result1)

	return result

def exportRig(asset, batch) : 
	from tool.utils.batch import rigPublish
	reload(rigPublish)

	refPath = asset.getPath('ref')
	refFile = asset.getRefNaming('anim')
	src = asset.thisScene()
	dst = '%s/%s' % (refPath, refFile)

	if batch : 

		rigPublish.run(src, dst)
		status = True

	else : 
	    pt.importRef() 
	    pt.clean()
	    mc.file(rename = dst)
	    result = mc.file(save = True, type = 'mayaAscii', f = True)

	    if result : 
	    	status = True

	return {'Export %s' % refFile: {'status': True, 'message': '', 'hero': dst}}

