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
	refShade = asset.getRefNaming('shade')
	src = asset.thisScene()
	print 'from tool.rig.cmd import rig_cmd as rigCmd'

	# export shade 
	# title = 'Export Shade'
	# result5 = exportShade(asset, title)

	# export vray data 
	title6 = 'Export vray data' 
	result6 = doExportVrayNode(asset, title6)

	# export ref render
	title1 = 'Export Render'
	dst1 = '%s/%s' % (refPath, refRender)
	cmds1 = "['importRef', 'removeUnknownPlugin', 'clean', 'removeSet', 'removeFixSet', 'removeVrayProxy']"
	cmds1Log = [setting.rigCmd[a] for a in eval(cmds1)]
	result1 = exportCmd(asset, title1, src, dst1, cmds1)
	print cmds1Log

	# export ref cache
	title2 = 'Export Cache'
	dst2 = '%s/%s' % (refPath, refCache)
	cmds2 = "['importRef', 'removeUnknownPlugin', 'clean', 'removeSet', 'removeFixSet', 'removeRig', 'removeVrayProxy']"
	cmds2Log = [setting.rigCmd[a] for a in eval(cmds2)]
	result2 = exportCmd(asset, title2, src, dst2, cmds2)
	print cmds2Log

	# export shade
	title5 = 'Export Shade'
	dst5 = '%s/%s' % (refPath, refShade)
	cmds5 = "['importRef', 'removeUnknownPlugin', 'exportShade']"
	cmds5Log = [setting.rigCmd[a] for a in eval(cmds5)]
	result5 = exportCmd(asset, title5, src, dst5, cmds5, exportGrp, 'None')
	print cmds5Log

	# export ref vrayProxy
	if mc.objExists(vrayProxyGrp) : 
		title3 = 'Export VrayProxy'
		title4 = 'Export VProxy'
		dst3 = '%s/%s' % (refPath, refVrayProxy)
		dst4 = '%s/%s' % (refPath, refVProxy)
		cmds3 = "['importRef', 'removeUnknownPlugin', 'clean', 'removeSet', 'removeFixSet', 'keepVrayProxy', 'removeVrayNode']"
		cmds4 = "['importRef', 'removeUnknownPlugin', 'clean', 'removeSet', 'removeFixSet', 'removeRig', 'vProxy', 'removeVrayNode']"
		cmds3Log = [setting.rigCmd[a] for a in eval(cmds3)]
		cmds4Log = [setting.rigCmd[a] for a in eval(cmds4)]
		result3 = exportCmd(asset, title3, src, dst3, cmds3)
		result4 = exportCmd(asset, title4, src, dst4, cmds4, exportGrp, 'export')

		print cmds3Log
		print cmds4Log
		# result4 = exportVrayProxy(asset, title4, dst4)

	# result3 = exportVrayProxy(asset)

	result.update(result1)
	result.update(result2)
	result.update(result5)
	result.update(result6)

	if mc.objExists(vrayProxyGrp) : 
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


def exportShade(asset, title) : 
	from tool.ptAlembic import exportShade as es
	reload(es)

	name = '%s_Shade' % asset.name()
	exportPath = asset.getPath('ref')
	exportName = '%s/%s' % (exportPath, name)

	# lock vray mtrl
	# mtrs = mc.ls(type = 'VRayMtl') + mc.ls(type = 'VRayBlendMtl')

	# for each in mtrs : 
	#     mc.setAttr('%s.vrayMaterialId' % each, l = True)

	# backup
	backupShadeFile = None 
	backupDataFile = None 
	
	if os.path.exists('%s.ma' % exportName) : 
		backupShadeFile = pt.backupRef('%s.ma' % exportName)

	if os.path.exists('%s.yml' % exportName) : 
		backupDataFile = pt.backupRef('%s.yml' % exportName)

	# run command export shade
	result = es.doShadeExport()
	returnResult = dict()

	status = False 
	message = 'Failed to export'
	dst = ''

	if result : 
		shadeFile = result[0]
		dataFile = result[1]

		status = True 
		message = 'Shade / Data export complete'


		if backupShadeFile and backupDataFile : 
			backupSMTime = backupShadeFile[1]
			backupDMTime = backupDataFile[1]
			currentSMTime = os.path.getmtime(shadeFile)
			currentDMTime = os.path.getmtime(dataFile)

			if backupSMTime == currentSMTime : 
				status = False 
				message = 'ShadeFile export failed'

			else : 
				status = True 
				message = 'ShadeFile export complete'

			if backupDMTime == currentDMTime : 
				status = False 
				message = 'DataFile export failed'

			else : 
				status = True 
				message = 'DataFile export complete'

		hero = '%s/%s' % (shadeFile, dataFile)


	returnResult.update({title: {'status': status, 'message': message, 'hero': hero}})
	return returnResult

def doExportVrayNode(asset, title) : 
	returnResult = dict()
	exportPath = asset.getPath('refData')
	nodeFile = '%s/%s' % (exportPath, asset.getRefNaming('vrayNode'))
	dataFile = '%s/%s' % (exportPath, asset.getRefNaming('vrayNodeData'))

	startMTime1 = None
	startMTime2 = None
	currentMTime1 = None
	currentMTime2 = None

	if os.path.exists(nodeFile) : 
		startMTime1 = os.path.getmtime(nodeFile)

	if os.path.exists(dataFile) : 
		startMTime2 = os.path.getmtime(dataFile)

	result = pt.exportVrayNode(dataFile, nodeFile)

	dataFileResult = result[0]
	nodeFileResult = result[1]

	if dataFileResult : 
		currentMTime1 = os.path.getmtime(dataFileResult)

	if nodeFileResult : 
		currentMTime2 = os.path.getmtime(nodeFileResult)

	status = False
	status1 = False 
	status2 = False
	message = ''

	if not currentMTime1 == startMTime1 : 
		status1 = True 
		message += 'Node file export complete - '

	if not currentMTime2 == startMTime2 : 
		status2 = True
		message += 'Node data file export complete'

	if status1 and status2 : 
		status = True

	hero = '%s/%s' % (dataFileResult, nodeFileResult)

	returnResult.update({title: {'status': status, 'message': message, 'hero': hero}})
	return returnResult