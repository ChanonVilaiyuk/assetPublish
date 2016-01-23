''' model '''
import maya.cmds as mc
import maya.mel as mm
import os, sys

def publish(asset) : 
	result = dict()
	result1 = exportGPU(asset)
	result2 = createAD(asset)

	result.update(result1)
	result.update(result2)
	return result

def exportGPU(asset) : 
	from tool.sceneAssembly import asm_utils
	reload(asm_utils)
	status = False 

	exportGrp = 'Geo_Grp'
	refPath = asset.getPath('ref')
	abcName = asset.getRefNaming('gpu')

	result = asm_utils.exportGPUCacheGrp(exportGrp, refPath, abcName, time = 'still')
	if result : 
		status = True
		
	return {'GPU Export': {'status': status, 'message': result}}

def createAD(asset) : 
	from tool.utils.batch import initAD
	reload(initAD)

	assetName = asset.name()
	refPath = asset.getPath('ref')
	adFile = asset.getRefNaming('ad')
	adFilePath = '%s/%s' % (refPath, adFile)

	status = False
	key = 'Create AD'

	# create only file not exists 
	if not os.path.exists(adFilePath) : 
		initAD.run(asset.thisScene())

		# check if there is a result 
		if os.path.exists(adFilePath) : 
			status = True
			message = 'Create Success'

	# do not create if exists 
	else : 
		status = True 
		message = 'AD exists'
		key = 'AD exists'
		
	return {key: {'status': status, 'message': message}}