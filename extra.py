''' extra command '''
import sys, os 
import maya.cmds as mc

from tool.utils import mayaTools
reload(mayaTools)


def publish(asset) : 
	step = asset.department()
	result = depPublish(step, asset)
	# testResult = {'test': {'status': True, 'meesage': ''}}
	# result.update(testResult)

	return result


def depPublish(step, asset) : 
	if step == 'model' : 
		# GPU
		# find Geo_Grp
		from tool.publish.asset import model 
		reload(model)
		return model.publish(asset)

	if step == 'uv' : 
		from tool.publish.asset import uv 
		reload(uv)
		return uv.publish(asset)

	if step == 'rig' : 
		from tool.publish.asset import rig
		reload(rig)
		return rig.publish(asset)
