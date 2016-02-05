''' rig '''
import maya.cmds as mc
import maya.mel as mm
import os, sys

from tool.utils import pipelineTools as pt
reload(pt)
from tool.utils import fileUtils
from tool.publish.asset import setting 
reload(setting)
from tool.utils.batch import rigPublish
reload(rigPublish)

version = mc.about(v = True)

def publish(asset, batch) : 
	result = dict()
	result1 = exportRig(asset, batch)
	result2 = exportHData(asset)
	result3 = exportABC(asset)
	result4 = exportDevRig(asset)

	result.update(result1)
	result.update(result2)
	result.update(result3)
	result.update(result4)

	return result

def exportRig(asset, batch) : 
	refPath = asset.getPath('ref')
	refFile = asset.getRefNaming('anim')
	src = asset.thisScene()
	dst = '%s/%s' % (refPath, refFile)
	status = False
	message = str()
	returnResult = dict()

	if batch : 
		# back up
		backupResult = pt.backupRef(dst)

		# publish
		cmds = "['importRef', 'clean', 'removeSet']"
		rigPublish.run(src, dst, cmds)

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

def exportHData(asset) : 
	# get publish maya file 
	pubMayaFile = asset.publishFile()

	# replace to yml 
	pubHDataFile = pubMayaFile.replace('.ma', '.yml')
	hDir = asset.rigDataPath('hdata')
	hFileName = '%s/%s' % (hDir, os.path.basename(pubHDataFile))

	if not os.path.exists(hDir) : 
		os.makedirs(hDir)

	if not os.path.exists(os.path.dirname(pubHDataFile)) : 
		os.makedirs(os.path.dirname(pubHDataFile))
		
	result = pt.exportHierarchyData(setting.exportGrp, pubHDataFile)

	if result : 
		# copy to work area 
		fileUtils.copy(pubHDataFile, hFileName)

	status = False 

	if result : 
		status = True 

	return {'Export H-Data': {'status': status, 'message': '', 'hero': result}}

def exportABC(asset) : 
	mc.loadPlugin("C:/Program Files/Autodesk/Maya2015/bin/plug-ins/AbcImport.mll", qt = True)
	from tool.ptAlembic import abcUtils
	reload(abcUtils)

	ctrl = setting.superRootCtrl
	geoGrp = setting.exportGrp

	# get publish maya file 
	pubMayaFile = asset.publishFile()

	# replace to yml 
	abcFile = pubMayaFile.replace('.ma', '.abc')
	abcDir = asset.rigDataPath('abc')
	abcFileName = '%s/%s' % (abcDir, os.path.basename(abcFile))

	if not os.path.exists(abcDir) : 
		os.makedirs(abcDir)

	if not os.path.exists(os.path.dirname(abcFile)) : 
		os.makedirs(os.path.dirname(abcFile))

	if mc.objExists(ctrl) : 
		start = mc.playbackOptions(q = True, min = True)
		end = mc.playbackOptions(q = True, max = True)

		# set animation 
		setTurnAnimation(ctrl)

		# export abc
		result = abcUtils.exportABC(geoGrp, abcFile)

		if os.path.exists(abcFile) : 
			# copy to work area 
			copyResult = fileUtils.copy(abcFile, abcFileName)

		# remove key
		removeKey(ctrl, start, end)
		status = False 

		if os.path.exists(abcFile) : 
			status = True

		return {'Export abc': {'status': status, 'message': result, 'hero': result}}

def exportDevRig(asset) : 
	# dev rig
	devFile = asset.getRefNaming('devRig')
	devPath = asset.getPath('dev')
	devRigPath = '%s/%s' % (devPath, devFile)

	# ref/Anim
	refPath = asset.getPath('ref')
	refFile = asset.getRefNaming('anim')
	ref = '%s/%s' % (refPath, refFile)

	src = asset.thisScene()
	dst = devRigPath

	if not os.path.exists(devPath) : 
		os.makedirs(devPath)

	# publish 
	mtime = None
	dstExists = os.path.exists(dst)

	if dstExists : 
		mtime = os.path.getmtime(dst)

	cmds = "['importRef', 'clean', 'removeSet', 'tmpShd']"
	rigPublish.run(src, dst, cmds)

	status = False 
	if os.path.exists(dst) : 
		status = True
		nmtime = os.path.getmtime(dst)

		if dstExists : 
			if mtime == nmtime : 
				status = False

	return {'Dev Rig': {'status': status, 'message': ''}}

def setTurnAnimation(ctrl) : 
	minV = 1
	maxV = 10 
	mc.playbackOptions(min = minV)
	mc.playbackOptions(max = maxV)
	mc.currentTime(minV)
	mc.setKeyframe(ctrl, v = 0, at = 'rotateY')
	mc.currentTime(maxV)
	mc.setKeyframe(ctrl, v = 360, at = 'rotateY')

def removeKey(ctrl, start, end) : 
	mc.cutKey(ctrl, cl = True, at = 'ry')
	mc.setAttr('%s.ry' % ctrl, 0)
	mc.playbackOptions(min = start)
	mc.playbackOptions(max = end)
	

