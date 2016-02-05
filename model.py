''' model '''
import maya.cmds as mc
import maya.mel as mm
import os, sys
from tool.publish.asset import setting 
reload(setting)
from tool.rig.cmd import rig_cmd as rigCmd 
reload(rigCmd)
from tool.utils.batch import rigPublish
reload(rigPublish)
from tool.utils import pipelineTools as pt
reload(pt)


def publish(asset) : 

	result = dict()
	print asset.type()
	if asset.type() in setting.checkExportSetting['hero-gpu'] : 
		print 'hero-gpu'
		result1 = exportGPU(asset)
		result.update(result1)

	if asset.type() in setting.checkExportSetting['hero-ad'] : 
		print 'hero-ad'
		result2 = createAD(asset)
		result.update(result2)

	if asset.type() in setting.checkExportSetting['hero-geo'] : 
		print 'hero-geo'
		result3 = exportGeo(asset)
		result.update(result3)

	return result

def exportGPU(asset) : 
	from tool.sceneAssembly import asm_utils
	reload(asm_utils)
	status = False 

	exportGrp = 'Geo_Grp'
	refPath = asset.getPath('ref')
	abcName = asset.getRefNaming('gpu', showExt = False)

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
	message = ''

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


def exportGeo(asset, batch = True) : 
	refPath = asset.getPath('ref')
	refFile = asset.getRefNaming('geo')
	src = asset.thisScene()
	dst = '%s/%s' % (refPath, refFile)
	status = False
	message = str()
	returnResult = dict()

	if batch : 
		# back up
		backupResult = pt.backupRef(dst)

		# publish
		cmds = "['clean']"
		rigPublish.run(src, dst, cmds, setting.exportGrp, 'export')

		if backupResult : 
			backupMTime = backupResult[1]
			currentMTime = os.path.getmtime(dst)
			returnResult.update({'Backup Ref file': {'status': True, 'message': ''}})


			if backupMTime == currentMTime : 
				status = False 
				message = 'File export failed'
				# print 'File export failed'

			else : 
				status = True 
				message = 'Export overwriten success %s' % dst
				# print 'Export overwriten success %s' % dst

		else : 
			if os.path.exists(dst) : 
				status = True
				message = 'Export success %s' % dst
				# print 'Export success %s' % dst



	else : 
	    pt.importRef() 
	    pt.clean()
	    mc.file(rename = dst)
	    result = mc.file(save = True, type = 'mayaAscii', f = True)

	    if result : 
	    	status = True

	returnResult.update({'Export %s' % refFile: {'status': status, 'message': message, 'hero': dst}})

	return returnResult
