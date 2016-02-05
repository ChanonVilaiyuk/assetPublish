''' shade '''
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

vrayProxyGrp = setting.vrayProxyGrp
exportGrp = setting.exportGrp 

def publish(asset, batch) : 
	result = dict()

	refPath = asset.getPath('ref')
	refRender = asset.getRefNaming('render')
	refCache = asset.getRefNaming('cache')
	refVrayProxy = asset.getRefNaming('vrayProxy')
	refVProxy = asset.getRefNaming('vProxy')
	src = asset.thisScene()

	# export ref render
	title1 = 'Export Render'
	dst1 = '%s/%s' % (refPath, refRender)
	cmds1 = "['importRef', 'clean', 'removeSet', 'removeVrayProxy']"
	result1 = exportCmd(asset, title1, src, dst1, cmds1)

	# export ref cache
	title2 = 'Export Cache'
	dst2 = '%s/%s' % (refPath, refCache)
	cmds2 = "['importRef', 'clean', 'removeSet', 'removeRig', 'removeVrayProxy']"
	result2 = exportCmd(asset, title2, src, dst2, cmds2)

	# export ref vrayProxy
	if mc.objExists(vrayProxyGrp) : 
		title3 = 'Export VrayProxy'
		title4 = 'Export VProxy'
		dst3 = '%s/%s' % (refPath, refVrayProxy)
		dst4 = '%s/%s' % (refPath, refVProxy)
		cmds3 = "['importRef', 'clean', 'removeSet', 'removeRig', 'keepVrayProxy', 'removeVrayNode']"
		cmds4 = "['importRef', 'clean', 'removeSet', 'removeRig', 'vProxy', 'removeVrayNode']"
		result3 = exportCmd(asset, title3, src, dst3, cmds3)
		result4 = exportCmd(asset, title4, src, dst4, cmds4, exportGrp, 'export')
		# result4 = exportVrayProxy(asset, title4, dst4)

	# result3 = exportVrayProxy(asset)

	result.update(result1)
	result.update(result2)
	result.update(result3)
	result.update(result4)


	return result


def exportCmd(asset, title, src, dst, cmds, content = '', output = 'save') : 
	returnResult = dict()
	message = str()
	status = False

	# back up
	backupResult = pt.backupRef(dst)

	# publish
	# cmds = "['importRef', 'clean', 'removeSet']"
	rigPublish.run(src, dst, cmds, content, output)

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


	returnResult.update({title: {'status': status, 'message': message, 'hero': dst}})

	return returnResult
	
def exportVrayProxy(asset, title, dst) : 
	returnResult = dict()
	# unparenting to world 
	if mc.listRelatives(vrayProxyGrp, p = True) : 
		mc.parent(vrayProxyGrp, w = True)

	mc.select(vrayProxyGrp)
	fileExists = os.path.exists(dst)

	if fileExists : 
		pMTime = os.path.getmtime(dst)

	result = mc.file(dst, f = True, options = 'v=0', type = 'mayaAscii', pr = True, es = True)

	# parent back
	mc.parent(vrayProxyGrp, exportGrp)

	status = False 
	message = ''

	if os.path.exists(dst) : 
		if fileExists : 
			cMTime = os.path.getmtime(dst)

			if not pMTime == cMTime : 
				status = True
				message = 'File overwriten failed'

		else : 
			status = True
			message = 'Export failed'


	returnResult.update({title: {'status': status, 'message': message, 'hero': dst}})
	return returnResult



