''' extra command '''
import sys, os 
import maya.cmds as mc

from tool.utils import mayaTools
reload(mayaTools)
from tool.check import check_core
reload(check_core)
from tool.rig.mergeRigUv import geoMatchBatch
reload(geoMatchBatch)

import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

def publish(asset, batch = True, mainUI=None) : 
	step = asset.department()
	result = depPublish(step, asset, batch, mainUI)

	# testResult = {'test': {'status': True, 'meesage': ''}}
	# result.update(testResult)

	return result


def depPublish(step, asset, batch = True, mainUI=None) : 
	if step == 'model' : 
		# GPU
		# find Geo_Grp
		from tool.publish.asset import model 
		reload(model)
		return model.publish(asset)

	if step == 'uv' : 
		from tool.publish.asset import uv 
		reload(uv)
		return uv.publish(asset, mainUI)

	if step == 'rig' : 
		from tool.publish.asset import rig
		reload(rig)
		return rig.publish(asset, batch)

	if step == 'surface' : 
		from tool.publish.asset import shade
		reload(shade)
		return shade.publish(asset, batch)

# def mergeUvToAnimRig(asset): 
# 	step = asset.department()
# 	from tool.rig.mergeRigUv import geoMatchBatch
# 	reload(geoMatchBatch)
# 	step = asset.department()

# 	if asset.project() == 'Lego_Pipeline': 

# 		logger.info('try to merge uv to anim rig')
# 		logger.debug(step)
# 		result = check_core.get_newest_publish(asset, compare=['rig', 'uv'], ext='ma')

# 		pubFile = result[0]
# 		latestStep = result[1]
# 		logger.debug('publish step is %s' % latestStep)
# 		logger.debug('publish file is %s' % pubFile)
		
# 		refPath = asset.getPath('ref')
# 		animRig = '%s/%s' % (refPath, asset.getRefNaming('anim'))
# 		logger.debug('anim rig is %s' % animRig)

# 		if os.path.exists(pubFile) and os.path.exists(animRig): 
# 			if step == 'rig': 
# 				logger.debug('publishing at rig department')
# 				logger.debug('checking for latest published department')

# 				if latestStep == 'uv': 
# 					logger.info('This is Rig department and uv publish is newer. Merge uv into AnimRig will be processing')
# 					geoMatchBatch.inputPath(animRig, pubFile)
# 				return {'Merge uv-AnimRig': {'status': True, 'message': 'dummy'}}

# 			if step == 'uv': 
# 				logger.info('This is Uv department. Merge uv into AnimRig will be processing')
# 				geoMatchBatch.inputPath(animRig, pubFile)

# 				return {'Merge uv-AnimRig': {'status': True, 'message': 'dummy'}}

# 		else: 
# 			logger.warning('pub file and anim rig not exists on the disk')


def mergeUvToAnimRig(pubFile, animRig): 
	geoMatchBatch.inputPath(animRig, pubFile)
	return {'Merge uv-AnimRig': {'status': True, 'message': 'dummy'}} 

