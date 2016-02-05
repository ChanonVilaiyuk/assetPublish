# asset publish
#Import python modules
import sys, os
import subprocess
from datetime import datetime

from functools import partial

#Import GUI
from qtshim import QtCore, QtGui
from qtshim import Signal
from qtshim import wrapinstance

from tool.publish.asset import assetPublishUI as ui
from tool.publish.asset import mayaHook as hook
from tool.publish.asset import check, shotgunPublish, extra, setting
reload(ui)
reload(hook)
reload(check)
reload(shotgunPublish)
reload(extra)
reload(setting)

moduleDir = sys.modules[__name__].__file__

from tool.utils import pipelineTools, fileUtils, entityInfo, projectInfo, mayaTools
reload(pipelineTools)
reload(fileUtils)
reload(projectInfo)
reload(mayaTools)

from tool.utils import entityInfo2 as entityInfo
reload(entityInfo)

# logger 
from tool.utils import customLog
reload(customLog)

scriptName = 'ptAssetPublish'
logger = customLog.customLog()
logger.setLevel(customLog.DEBUG)
logger.setLogName(scriptName)

#Import maya commands
import maya.cmds as mc
import maya.mel as mm
import maya.OpenMayaUI as mui


# If inside Maya open Maya GUI
def getMayaWindow():
    ptr = mui.MQtUtil.mainWindow()
    if ptr is None:
        raise RuntimeError('No Maya window found.')
    window = wrapinstance(ptr)
    assert isinstance(window, QtGui.QMainWindow)
    return window


class MyForm(QtGui.QMainWindow):

	def __init__(self, parent=None):
		self.count = 0
		#Setup Window
		super(MyForm, self).__init__(parent)
		# QtGui.QWidget.__init__(self, parent)
		self.ui = ui.Ui_AssetPublishWin()
		self.ui.setupUi(self)
		self.setWindowTitle('PT Asset Publish v.1.0')

		# icons 
		self.logo = '%s/%s' % (os.path.dirname(moduleDir), 'icons/logo.png')
		self.logo2 = '%s/%s' % (os.path.dirname(moduleDir), 'icons/alembic_logo.png')
		self.okIcon = '%s/%s' % (os.path.dirname(moduleDir), 'icons/ok_icon.png')
		self.xIcon = '%s/%s' % (os.path.dirname(moduleDir), 'icons/x_icon.png')
		self.rdyIcon = '%s/%s' % (os.path.dirname(moduleDir), 'icons/rdy_icon.png')
		self.ipIcon = '%s/%s' % (os.path.dirname(moduleDir), 'icons/ip_icon.png')
		self.refreshIcon = '%s/%s' % (os.path.dirname(moduleDir), 'icons/refresh_icon.png')
		self.mayaIcon = '%s/%s' % (os.path.dirname(moduleDir), 'icons/maya_icon.png')
		self.iconPath = '%s/icons' % os.path.dirname(moduleDir)
		self.sgStatusIcon = {'Approved':'%s/green_icon.png' % self.iconPath, 'Pending Client':'%s/yellow_icon.png' % self.iconPath, 'Pending Internal':'%s/red_icon.png' % self.iconPath, 'Review':'%s/daily_icon.png' % self.iconPath}
		self.sgStatusMap = {'Approved':'aprv', 'Pending Client':'intapr', 'Pending Internal':'noapr', 'Review':'daily'}
		self.iconSize = 15
		self.w = 1280
		self.h = 1024

		# data
		self.screenShotDst = str()

		self.checkList = {'screenShot': False}

		self.initData()
		self.initFunctions()
		self.initSignals()


	# refreshUI 
	def refresh(self) : 
		self.initData()
		# set project title 
		self.setEntityInfo()

		# list publish 
		self.listPublishFiles()

		# list Ref 
		self.listRefFiles()

	def initData(self) : 
		# data 
		self.asset = entityInfo.info()
		self.statusMap = self.getProjectSetting('statusMap')
		self.outputMap = self.getProjectSetting('outputMap')
		self.svPublishFile = self.asset.publishFile()

	def initFunctions(self) : 
		# UI
		self.fillUI()


	def initSignals(self) : 
		self.ui.screenShot_pushButton.clicked.connect(self.doSnapScreen)
		self.ui.publish_pushButton.clicked.connect(self.doPublish)
		self.ui.publish_listWidget.itemSelectionChanged.connect(self.doDisplayThumbnail)

		self.ui.thumbnail_lineEdit.textChanged.connect(self.runRecheck)
		# self.ui.media_lineEdit.textChanged.connect(self.runRecheck)

		# right click 
		self.ui.ref_listWidget.customContextMenuRequested.connect(self.showMenu)
		self.ui.publish_listWidget.customContextMenuRequested.connect(self.showMenu2)


	def fillUI(self) : 
		# set Logo 
		self.setLogo()

		# set project title 
		self.setEntityInfo()

		# list publish 
		self.listPublishFiles()

		# list Ref 
		self.listRefFiles()

		# set shotgun status
		self.setStatusComboBox()

		# pre check 
		self.preCheck()


	def runRecheck(self) : 
		# set shotgun status
		self.setStatusComboBox()

		# pre check 
		self.preCheck()



	def setLogo(self) : 
		self.ui.logo_label.setPixmap(QtGui.QPixmap(self.logo).scaled(200, 60, QtCore.Qt.KeepAspectRatio))


	def setEntityInfo(self) : 
		self.ui.assetName_label.setText('%s   -   %s' % (self.asset.name(), self.asset.task()))
		self.ui.project_label.setText(self.asset.project())
		self.ui.type_label.setText(self.asset.type())
		self.ui.subType_label.setText(self.asset.subType())
		self.ui.step_label.setText(self.asset.department())

		publishFile = self.asset.publishFile()
		if publishFile : 
			self.ui.publish_label.setText(os.path.basename(publishFile))

		dependency = self.getDependency()

		if dependency : 
			text = '/'.join(dependency)
			self.ui.dependency_label.setText(str(text))

		output = self.getOutputStep()

		if output : 
			text = '/'.join(output)
			self.ui.output_label.setText(str(text))

	
	def getDependency(self) : 
		kw = '%s-%s' % (self.asset.department(), self.asset.task())
		if kw in self.statusMap.keys() : 
			dependency = self.statusMap[kw]
			return dependency 


	def getOutputStep(self) : 
		kw = '%s-%s' % (self.asset.department(), self.asset.task())
		if kw in self.outputMap.keys() : 
			output = self.outputMap[kw]

			export = []
			# for each in output : 
				# if each in setting.modelExportSetting.keys() : 
				# 	exportType = setting.modelExportSetting[each]
				# 	if self.asset.type() in exportType : 
				# 		export.append(each)
			# return export
			return output


	def getProjectSetting(self, settingType) : 
		project = self.asset.project()

		if project in setting.projectSetting.keys() : 
			settingValue = setting.projectSetting[project]

		else : 
			settingValue = setting.projectSetting['all']

		value = setting.settingMap[settingValue]

		if value : 
			if settingType == 'statusMap' : 
				return value['statusMap']

			if settingType == 'outputMap' : 
				return value['outputMap']
			

	''' button commands '''
	def doSnapScreen(self) : 
		dst = self.asset.publishImageFile()
		dirname = os.path.dirname(dst)

		if not os.path.exists(dirname) : 
			os.makedirs(dirname)

		result = hook.snapShotCmd(dst, self.w, self.h)

		if result : 
			self.displayCapture(result, 0.5)
			self.checkList['screenShot'] = True
			self.screenShotDst = result

			# assign to lineEdit
			self.ui.thumbnail_lineEdit.setText(result)
			self.ui.media_lineEdit.setText(result)


		self.preCheck()


	def doPublish(self) : 
		# start time
		start = datetime.now()

		# self.check
		# check 
		allowPublish, resultList = self.check()

		if allowPublish : 

			# publish files 
			if self.ui.publishFile_checkBox.isChecked() : 
				result1 = self.publishFile()
				duration = datetime.now() - start 
				self.setDuration(duration, 'sum')

			# publish shotgun 
			if self.ui.publishShotgun_checkBox.isChecked() : 
				start2 = datetime.now()
				result2 = self.publishShotgun()
				duration = datetime.now() - start2 
				self.setDuration(duration, 'sum')

			# set total
			duration = datetime.now() - start 
			self.setDuration(duration, 'total')
			self.refresh()
			self.ui.publish_pushButton.setEnabled(False)
			self.completeDialog('Publish Complete', 'Publish %s - %s Complete' % (self.asset.name(), self.asset.task()))

		else : 
			for each in resultList : 
				status = resultList[each]['status']
				self.setStatus(each, status) 


	def doDisplayThumbnail(self) : 
		thumbnailDir = os.path.dirname(self.asset.publishImageFile())
		ext = self.asset.publishImageFile().split('.')[-1]
		sel = self.ui.publish_listWidget.currentItem()

		if sel : 
			selection = str(sel.text())
			fileName = '%s.%s' % (selection.split('.')[0], ext)
			filePath = '%s/%s' % (thumbnailDir, fileName)
			self.displayCapture(filePath, 0.5)


	def check(self) : 
		allowPublish = True
		resultList = dict()
		for each in self.checkList : 
			status = self.checkList[each]
			logger.debug('%s - %s' % (each, status))
			resultList.update({each: {'status': True, 'message': ''}})

			if not status : 
				allowPublish = False 
				resultList.update({each: {'status': allowPublish, 'message': ''}})

		return allowPublish, resultList


	def preCheck(self) : 
		allowPublish = True

		# clear status 
		self.ui.status_listWidget.clear()

		# set pre check status
		self.setStatus('--- Pre-Check ---', True, [40, 40, 40], 0)

		# pipeline check 
		results = check.pipelineCheck()

		# add info 
		infoResult = self.addInfo()
		results.update(infoResult)

		# check screen shot 
		dst = self.asset.publishImageFile()
		
		if str(self.ui.thumbnail_lineEdit.text()) : 
			dst = str(self.ui.thumbnail_lineEdit.text())

		if dst : 
			if os.path.exists(dst) : 
				results.update({'screenShot': {'status': True, 'message': ''}})
				self.checkList['screenShot'] = True

				# display 
				self.displayCapture(dst, 0.5)

			# check dependency
			dependency = self.getDependency()
			outputFile = self.getOutputStep()

			dStatus = True 
			dMessage = ''
			if not dependency and not outputFile : 
				dStatus = False 
				dMessage = 'No task found "%s"' % self.asset.task()

			results.update({'Check dependency': {'status': dStatus, 'message': dMessage}})
			
			# loop setting status 
			for each in sorted(results) : 
				title = each
				status = results[each]['status']
				message = results[each]['message']
				self.setStatus(title, status)

				if not status : 
					logger.debug(title)
					logger.debug('Error Message : %s' % message)
					allowPublish = False

			self.ui.publish_pushButton.setEnabled(allowPublish)


	def publishShotgun(self) : 
		# publish shotgun
		''' version
		- Version, Thumbnails, Media
		# task 

		'''
		logger.debug('--- publishing Shotgun ---')
		self.setStatus('--- Shotgun Publish ---', True, [40, 40, 40], 0)

		# UI value 
		status = str(self.ui.status_comboBox.currentText())
		thumbnail = str(self.ui.thumbnail_lineEdit.text())
		media = str(self.ui.media_lineEdit.text())
		sg_status_list = self.sgStatusMap[status]
		
		# entity value
		project = self.asset.project()
		assetType = self.asset.type()
		assetSubType = self.asset.subType()
		assetName = self.asset.name()
		stepName = self.asset.department()
		taskName = self.asset.task()
		publishFile = os.path.basename(self.svPublishFile).split('.')[0]
		user = hook.getUser()

		''' version ''' 
		logger.debug('Create version %s' % publishFile)
		logger.debug('%s %s %s %s %s %s %s %s %s' % (project, assetType, assetSubType, assetName, stepName, taskName, publishFile, sg_status_list, user))
		versionEntity, assetEntity, taskEntity = shotgunPublish.publishVersion(project, assetType, assetSubType, assetName, stepName, taskName, publishFile, sg_status_list, user)
		self.setStatus('Create version %s' % publishFile, versionEntity)
		logger.info('Create version %s %s' % (publishFile, versionEntity))

		
		if versionEntity and assetEntity and taskEntity : 

			''' upload thumbnail ''' 
			logger.debug('Upload thumbnail %s' % thumbnail)
			thumbResult = shotgunPublish.uploadThumbnail(versionEntity, thumbnail)
			self.setStatus('Upload thumbnail', thumbResult)
			logger.info('Upload thumbnail %s' % thumbResult)
			

			''' upload media ''' 
			logger.debug('Upload media %s' % media)
			mediaResult = shotgunPublish.uploadMedia(versionEntity, media)
			self.setStatus('Upload media', mediaResult)
			logger.info('Upload media %s' % mediaResult)


			''' set task and dependency tasks ''' 
			logger.debug('Set task')
			taskResult = shotgunPublish.publishTask(self.asset, assetEntity, stepName, taskEntity, sg_status_list, self.svPublishFile)
			self.setStatus('Set Task', taskResult)
			
			''' set geo info ID ''' 
			# set ID 
			pipelineTools.setGeoInfo('id', assetEntity['id'])


	''' cmds ''' 
	def publishFile(self) : 
		logger.debug('--- publishing ---')

		# publish file 
		publishFile = self.svPublishFile
		workFile = self.asset.publishFile(showUser = True)
		workDir = self.asset.workDir()
		user = hook.getUser()
		self.setStatus('--- File Publish ---', True, [40, 40, 40], 0)

		if publishFile and workDir : 
			saveFile = '%s/%s' % (workDir, os.path.basename(workFile))
			# saveFile = hook.addUser(saveFile, user)

			# save file 
			logger.debug('Saving file -> %s' % saveFile)
			saveResult = hook.save(saveFile)
			logger.info('Save file done %s' % saveResult)
			self.setStatus('Save', saveResult)

			# get increment version
			thisFile = entityInfo.info()
			incrementFile = thisFile.nextVersion()

			# manage thumbnail / media
			self.manageMediaFile()

			# extra command 
			batch = not self.ui.noBatch_checkBox.isChecked()
			refPath = self.asset.getPath('ref')
			logger.debug('Extra export -> %s' % refPath)
			extraResults = extra.publish(self.asset, batch)

			if extraResults : 
				for each in extraResults : 
					title = each
					status = extraResults[each]['status']
					message = extraResults[each]['message']
					self.setStatus('%s' % title, status)
					logger.info('%s %s' % (title, message))

			# copy publish 
			logger.debug('Publish file from %s -> %s' % (saveResult, publishFile))
			copyResult = fileUtils.copy(saveResult, publishFile)
			logger.info('Publish file to %s' % publishFile)
			self.setStatus('Published', copyResult)

			if saveResult : 
				# set status 
				logger.debug('Increment file -> %s' % incrementFile)

				# increment file
				if batch : 
					incrementResult = hook.save(incrementFile)

				else : 
					incrementResult = fileUtils.copy(saveResult, incrementFile)

				if incrementResult : 
					self.setStatus('Increment File', incrementResult)
					logger.info('Increment file to %s' % incrementFile)


	def listPublishFiles(self) : 
		publishDir = self.asset.publishDir()
		files = fileUtils.listFile(publishDir, 'ma')
		listWidget = 'publish_listWidget'
		iconPath = self.mayaIcon
		color = [0, 0, 0]

		self.ui.publish_listWidget.clear()

		for eachFile in files : 
			self.addListWidgetItem(listWidget, eachFile, iconPath, color, 1)


	def listRefFiles(self) : 
		refPath = self.asset.getPath('ref')
		files = fileUtils.listFile(refPath)
		listWidget = 'ref_listWidget'
		iconPath = self.mayaIcon
		color = [0, 0, 0]

		self.ui.ref_listWidget.clear()

		for eachFile in files : 
			self.addListWidgetItem(listWidget, eachFile, iconPath, color, 1)



	def addInfo(self) : 
		try : 
			# add attr 
			pipelineTools.assignGeoInfo()

			# assign department info 
			pipelineTools.setGeoInfo(self.asset.department(), self.asset.fileName())

			# assign basic info 
			pipelineTools.setGeoInfo('project', self.asset.project())
			pipelineTools.setGeoInfo('assetName', self.asset.name())
			data = pipelineTools.readGeoInfo('data')

			# assign data 
			datas = []
			if data : 
				datas = eval(data)
				
			if not self.asset.fileName() in datas : 
				datas.append(self.asset.fileName())

			pipelineTools.setGeoInfo('data', str(datas))

			return {'Add info': {'status': True, 'message': ''}}

		except Exception as e : 
			logger.debug(e)
			return {'Add info': {'status': False, 'message': e}}


	def manageMediaFile(self) : 
		# target file
		targetFile = self.asset.publishImageFile()
		dir = os.path.dirname(targetFile)

		# input files 
		current = str(self.ui.thumbnail_lineEdit.text())
		currentMedia = str(self.ui.media_lineEdit.text())

		print targetFile
		print current
		print currentMedia

		if os.path.exists(current) : 
			if not current == targetFile : 
				fileUtils.copy(current, targetFile)
				logger.debug('Copy thumbnail %s -> %s' % (current, targetFile))

			else : 
				logger.debug('Thumbnail not copy')

		if os.path.exists(currentMedia) : 
			ext = currentMedia.split('.')[-1]
			targetMedia = '%s.%s' % (targetFile.split('.')[0], ext)

			if not targetMedia == targetFile : 
				fileUtils.copy(currentMedia, targetMedia)
				logger.debug('Copy media %s -> %s' % (currentMedia, targetMedia))

			else : 
				logger.debug('Media not copy')

		return True 



	def setStatusComboBox(self) : 
		# clear UI
		self.ui.status_comboBox.clear()

		i = 0
		for each in sorted(self.sgStatusIcon) : 
			text = each 
			iconPath = self.sgStatusIcon[each]
			self.addComboBoxItem(i, text, iconPath)

			i += 1


	''' utils '''

	def showMenu(self,pos):
		if self.ui.ref_listWidget.currentItem() : 
			menu=QtGui.QMenu(self)
			# menu.addAction('Rename')
			# menu.addAction('Delete')

			subMenu = QtGui.QMenu('Open', self)
			subMenu.addAction('Open')
			subMenu.addAction('Open as work file')

			subMenu2 = QtGui.QMenu('Import', self)
			subMenu2.addAction('Import')
			subMenu2.addAction('Import to new file')

			subMenu3 = QtGui.QMenu('Reference', self)
			subMenu3.addAction('Reference')
			subMenu3.addAction('Reference to new file')
			# items = self.getPlayblastFile()

			# for each in items : 
			# 	subMenu3.addAction(each)

			menu.addMenu(subMenu)
			menu.addMenu(subMenu2)
			menu.addMenu(subMenu3)

			menu.popup(self.ui.ref_listWidget.mapToGlobal(pos))
			result = menu.exec_(self.ui.ref_listWidget.mapToGlobal(pos))

			if result : 
				self.menuCommand(result.text(), result.parentWidget().title())


	def menuCommand(self, command, catagories) : 
		selItem = str(self.ui.ref_listWidget.currentItem().text())
		filePath = '%s/%s' % (self.asset.getPath('ref'), selItem)

		if os.path.exists(filePath) : 

			if catagories == 'Open' : 
				if command == 'Open' : 
					hook.openFile(filePath)

				if command == 'Open as work file' : 
					workFile = self.asset.nextVersion()
					hook.openFile(filePath)
					hook.save(workFile)

			if catagories == 'Import' : 
				if command == 'Import' : 
					hook.importFile(filePath)

				if command == 'Import to new file' : 
					hook.newFile()
					hook.importFile(filePath)

			if catagories == 'Reference' : 
				namespace = self.asset.name()

				if command == 'Reference' : 
					hook.createReference(namespace, filePath)

				if command == 'Reference to new file' : 
					hook.newFile()
					hook.createReference(namespace, filePath)

		else : 
			self.messageBox('Error', 'File %s not exists' % filePath)


	def showMenu2(self,pos):
		if self.ui.publish_listWidget.currentItem() : 
			item = str(self.ui.publish_listWidget.currentItem().text())
			publishDir = self.asset.publishDir()
			path = '%s/%s' % (publishDir, item)

			menu=QtGui.QMenu(self)
			menu.addAction('Open file')
			menu.addAction('Open in Explorer')
			menu.addAction('Copy Path')

			menu.popup(self.ui.publish_listWidget.mapToGlobal(pos))
			result = menu.exec_(self.ui.publish_listWidget.mapToGlobal(pos))

			if result : 
				self.menuCommand2(result.text(), path)


	def menuCommand2(self, command, path) : 
		if os.path.exists(path) : 
			if command == 'Open file' : 
				hook.openFile(path)

			if command == 'Open in Explorer' : 
				path = path.replace('/', '\\')
				subprocess.Popen(r'explorer /select,"%s"' % path)

			if command == 'Copy Path' : 
				mayaTools.copyToClipboard(path)

		else : 
			self.messageBox('Error', '%s not found' % path)


	def displayCapture(self, iconPath, display = 1) : 
		w = self.h * display
		h = self.w * display
		self.ui.snap_label.setPixmap(QtGui.QPixmap(iconPath).scaled(w, h, QtCore.Qt.KeepAspectRatio))


	def setStatus(self, text, status, color = [0, 0, 0], icon = 1) : 
		iconPath = self.xIcon
		if status : 
			iconPath = self.okIcon

		widget = 'status_listWidget'
		self.addListWidgetItem(widget, text, iconPath, color, icon)

		QtGui.QApplication.processEvents()


	def setDuration(self, duration, total = 'total') : 
		widget = 'status_listWidget'
		iconPath = ''
		if total == 'total' : 
			text = '=== Finish in %s ===' % str(duration)
			color = [20, 20, 100]

		if total == 'sum' : 
			text = '--- %s ---' % str(duration)
			color = [40, 100, 40]

		self.addListWidgetItem(widget, text, iconPath, color, 0)

		QtGui.QApplication.processEvents()



	''' UI widget utils '''
	def addListWidgetItem(self, listWidget, text, iconPath, color, addIcon = 1) : 
		cmd = 'QtGui.QListWidgetItem(self.ui.%s)' % listWidget
		item = eval(cmd)

		if addIcon : 
			icon = QtGui.QIcon()
			icon.addPixmap(QtGui.QPixmap(iconPath),QtGui.QIcon.Normal,QtGui.QIcon.Off)
			item.setIcon(icon)

		item.setText(text)
		item.setBackground(QtGui.QColor(color[0], color[1], color[2]))
		size = 16

		cmd2 = 'self.ui.%s.setIconSize(QtCore.QSize(%s, %s))' % (listWidget, size, size)
		eval(cmd2)
		QtGui.QApplication.processEvents()


	def addComboBoxItem(self, i, text, iconPath) : 
		self.ui.status_comboBox.addItem(text)
		icon = QtGui.QIcon()
		icon.addPixmap(QtGui.QPixmap(iconPath), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.ui.status_comboBox.setItemIcon(i, icon)


	def messageBox(self, title, description) : 
		result = QtGui.QMessageBox.question(self,title,description ,QtGui.QMessageBox.Ok, QtGui.QMessageBox.Cancel)

		return result


	def completeDialog(self, title, description) : 
		result = QtGui.QMessageBox.question(self,title,description ,QtGui.QMessageBox.Ok)

		return result 