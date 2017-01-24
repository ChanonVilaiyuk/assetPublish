# asset publish
#Import python modules
import sys, os
import subprocess
from datetime import datetime

# logger 
from tool.utils import customLog
reload(customLog)

scriptName = 'ptAssetPublish'
# logger = customLog.customLog()
# logger.setLevel(customLog.DEBUG)
# logger.setLogName(scriptName)

from tool.utils import logName
logFile = logName.name(toolName=scriptName, createDir=True)

import logging
# create logger with 'spam_application'
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

for each in logger.handlers[::-1] :
    if type(each).__name__ == 'StreamHandler':
        logger.removeHandler(each)

    if type(each).__name__== 'FileHandler': 
        logger.removeHandler(each)
        each.flush()
        each.close()

# create file handler which logs even debug messages
fh = logging.FileHandler(logFile)
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

from functools import partial

#Import GUI
from qtshim import QtCore, QtGui
from qtshim import Signal
from qtshim import wrapinstance

from tool.publish.asset import assetPublishUI as ui
from tool.publish.asset import mayaHook as hook
from tool.publish.asset import check, shotgunPublish, extra, setting, config
from tool.check import check_core
from tool.rig.mergeRigUv import geoMatchBatch
reload(ui)
reload(hook)
reload(check)
reload(shotgunPublish)
reload(extra)
reload(setting)
reload(config)
reload(check_core)
reload(geoMatchBatch)

moduleDir = sys.modules[__name__].__file__

from tool.utils import pipelineTools, fileUtils, entityInfo, projectInfo, mayaTools
reload(pipelineTools)
reload(fileUtils)
reload(projectInfo)
reload(mayaTools)

from tool.utils import entityInfo, emailUtils
reload(entityInfo)
reload(emailUtils)


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
        self.setWindowTitle('PT Asset Publish v.1.1')

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
        self.sgStatusIcon = {'Approved':'%s/green_icon.png' % self.iconPath, 'Pending Client':'%s/yellow_icon.png' % self.iconPath, 'Pending Internal':'%s/red_icon.png' % self.iconPath, 'Review':'%s/daily_icon.png' % self.iconPath, 'Place Holder': '%s/placeHolder_icon.png' % self.iconPath}
        self.sgStatusMap = {'Approved':'aprv', 'Pending Client':'intapr', 'Pending Internal':'noapr', 'Review':'daily', 'Place Holder': 'place'}
        self.iconSize = 15
        self.w = 1280
        self.h = 1024

        logger.info('############ Tool starting ... ############')

        # data
        self.screenShotDst = str()

        self.checkList = {'screenShot': False, 'Revision Details': False}

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
        logger.info('Initialized data ...')
        self.asset = entityInfo.info()
        logger.info('#### %s ####' % self.asset.name())

        self.statusMap = self.getProjectSetting('statusMap')
        self.outputMap = self.getProjectSetting('outputMap')
        self.svPublishFile = self.asset.publishFile()
        self.logFile = self.asset.getLogPath()
        logger.info('Completed')

    def initFunctions(self) : 
        # UI
        self.fillUI()


    def initSignals(self) : 
        self.ui.screenShot_pushButton.clicked.connect(self.doSnapScreen)
        self.ui.publish_pushButton.clicked.connect(self.doPublish)
        self.ui.publish_listWidget.itemSelectionChanged.connect(self.doDisplayThumbnail)

        self.ui.browse1_pushButton.clicked.connect(self.doBrowseImage)
        self.ui.browse2_pushButton.clicked.connect(self.doBrowseMedia)

        self.ui.thumbnail_lineEdit.textChanged.connect(self.runRecheck)
        # self.ui.media_lineEdit.textChanged.connect(self.runRecheck)
        self.ui.snap_pushButton.clicked.connect(self.doSnapRevision)

        # right click 
        self.ui.ref_listWidget.customContextMenuRequested.connect(self.showMenu)
        self.ui.publish_listWidget.customContextMenuRequested.connect(self.showMenu2)

        # snap 
        self.ui.snap_listWidget.itemSelectionChanged.connect(self.showSnapRevision)
        self.ui.removeSnap_pushButton.clicked.connect(self.removeSnapRevision)
        self.ui.message_plainTextEdit.cursorPositionChanged.connect(self.revisionTextCheck)


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

        # list revision
        self.listSnapRevision()


    def runRecheck(self) : 
        # set shotgun status
        self.setStatusComboBox()

        # pre check 
        self.preCheck()



    def setLogo(self) : 
        self.ui.logo_label.setPixmap(QtGui.QPixmap(self.logo).scaled(200, 60, QtCore.Qt.KeepAspectRatio))


    def setEntityInfo(self) : 
        logger.info('setting entityInfo ...')
        logger.info('setting ui labels ...')
        self.ui.assetName_label.setText('%s   -   %s' % (self.asset.name(), self.asset.task()))
        self.ui.project_label.setText(self.asset.project())
        self.ui.type_label.setText(self.asset.type())
        self.ui.subType_label.setText(self.asset.subType())
        self.ui.step_label.setText(self.asset.department())

        publishFile = self.asset.publishFile()
        if publishFile : 
            self.ui.publish_label.setText(os.path.basename(publishFile))

        logger.debug('publish file : %s' % publishFile)

        dependency = self.getDependency()
        logger.debug('dependency : %s' % dependency)

        if dependency : 
            text = '/'.join(dependency)
            self.ui.dependency_label.setText(str(text))

        output = self.getOutputStep()
        logger.debug('output : %s' % output)

        if output : 
            text = '/'.join(output)
            self.ui.output_label.setText(str(text))

        # set increment file 
        incrementFile = self.getFileToIncrement()
        logger.debug('incrementFile : %s' % incrementFile)

        if incrementFile : 
            self.ui.incrementFile_lineEdit.setText(incrementFile)
            self.ui.incrementRoolFile_checkBox.setChecked(True)

        else : 
            self.ui.incrementFile_lineEdit.setEnabled(False)
            # self.ui.incrementFile_lineEdit.setText(self.asset.thisScene())

        logger.debug('setting extra buttons state ...')
        self.ui.texture_checkBox.setEnabled(False)
        self.ui.mergeUv_checkBox.setEnabled(False)
        if self.asset.department() == self.asset.uv: 
            self.ui.texture_checkBox.setEnabled(True)
            self.ui.mergeUv_checkBox.setEnabled(True)

        if self.asset.department() == self.asset.rig: 
            self.ui.mergeUv_checkBox.setEnabled(True)

        logger.info('Complete init entityInfo')


    def getFileToIncrement(self) : 
        duplicatedFiles = self.asset.duplicateVersion()
        thisFile = os.path.basename(self.asset.thisScene())

        if len(duplicatedFiles) > 1 : 
            # duplicate return lowest index
            return duplicatedFiles[0]


    
    def getDependency(self) : 
        kw = '%s-%s' % (self.asset.department(), self.asset.task())
        print kw
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
                #   exportType = setting.modelExportSetting[each]
                #   if self.asset.type() in exportType : 
                #       export.append(each)
            # return export
            return output


    def getProjectSetting(self, settingType) : 
        project = self.asset.project()

        if project in setting.projectSetting.keys() : 
            settingValue = setting.projectSetting[project]

        else : 
            settingValue = setting.projectSetting['all']

        value = setting.settingMap[settingValue]
        # print value
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
            self.displayCapture(self.ui.snap_label, result, 0.5)
            self.checkList['screenShot'] = True
            self.screenShotDst = result

            # assign to lineEdit
            self.ui.thumbnail_lineEdit.setText(result)
            self.ui.media_lineEdit.setText(result)


        self.preCheck()

    def doSnapRevision(self): 
        version = self.asset.getPublishVersion(padding=True)
        revisionDir = ('/').join([self.asset.getPath(), self.asset.publish, self.asset.department(), self.asset.task(), version])
        revFile = self.getRevisionVersion(revisionDir, version)

        if not os.path.exists(revisionDir): 
            os.makedirs(revisionDir)

        result = hook.snapShotCmd(revFile, self.w, self.h)

        if result : 
            self.displayCapture(self.ui.preview_label, result, 0.4)

        self.listSnapRevision()
        self.preCheck()

    def listSnapRevision(self): 
        """ list snap shot """ 
        version = self.asset.getPublishVersion(padding=True)
        revisionDir = ('/').join([self.asset.getPath(), self.asset.publish, self.asset.department(), self.asset.task(), version])
        files = fileUtils.listFile(revisionDir)
        self.ui.snap_listWidget.clear()

        for each in files: 
            iconPath = '%s/%s' % (revisionDir, each)
            self.addListWidgetItem('snap_listWidget', iconPath=iconPath, color=[0, 0, 0], addIcon = 1, data=iconPath, size=100)

    def showSnapRevision(self): 
        item = self.ui.snap_listWidget.currentItem()
        if item: 
            iconPath = item.data(QtCore.Qt.UserRole)
            self.displayCapture(self.ui.preview_label, iconPath, 0.4)

    def removeSnapRevision(self): 
        item = self.ui.snap_listWidget.currentItem()
        if item: 
            self.ui.snap_listWidget.takeItem(self.ui.snap_listWidget.currentRow())
            iconPath = item.data(QtCore.Qt.UserRole)
            os.remove(iconPath)

    def revisionTextCheck(self): 
        self.ui.message_plainTextEdit.setStyleSheet('')


    def doBrowseImage(self) : 
        path = self.asset.getPath(self.asset.department(), self.asset.task())
        imgPath = '%s/%s' % (path, self.asset.images)

        fileName = QtGui.QFileDialog.getOpenFileName(self,'File Browse',imgPath,'Media(*.png *.tif *.exr *.jpg *.jpeg)')

        if fileName : 
            self.ui.thumbnail_lineEdit.setText(fileName[0])


    def doBrowseMedia(self) : 
        path = self.asset.getPath(self.asset.department(), self.asset.task())
        mediaPath = '%s/%s' % (path, self.asset.images)

        fileName = QtGui.QFileDialog.getOpenFileName(self,'File Browse',mediaPath,'Media(*.mov *.mp4 *.avi)')

        if fileName : 
            self.ui.media_lineEdit.setText(fileName[0])


    def doPublish(self) : 
        # start time
        start = datetime.now()

        if self.inputCheck(): 

            # self.check
            # check 
            allowPublish, resultList = self.check()

            if allowPublish : 
                result1 = None
                result2 = None

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

                # email 
                self.sendEmail()

                # set total
                duration = datetime.now() - start 
                self.setDuration(duration, 'total')
                self.refresh()
                self.ui.publish_pushButton.setEnabled(False)

                if result1 and result2 : 
                    self.completeDialog('Publish Complete', 'Publish %s - %s Complete' % (self.asset.name(), self.asset.task()))

                else : 
                    self.completeDialog('Publish not complete', 'Publish %s - %s Not Complete' % (self.asset.name(), self.asset.task()))


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
            self.displayCapture(self.ui.snap_label, filePath, 0.5)


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

    def inputCheck(self): 
        # check input description 
        if self.ui.message_plainTextEdit.toPlainText(): 
            return True 

        else: 
            QtGui.QMessageBox.question(self, 'Warning', 'Please write commit message')
            self.ui.message_plainTextEdit.setStyleSheet('background-color: rgb(%s, %s, %s);' % (120, 40, 40))

    def checkRevision(self): 
        """ check if any snap png in revision dir """ 
        version = self.asset.getPublishVersion(padding=True)
        revisionDir = ('/').join([self.asset.getPath(), self.asset.publish, self.asset.department(), self.asset.task(), version])

        files = fileUtils.listFile(revisionDir)
        if not files: 
            return False 

        return True 

    def preCheck(self) : 
        logger.info('## Running Precheck ... ##')
        allowPublish = True

        # clear status 
        self.ui.status_listWidget.clear()

        # set pre check status
        self.setStatus('--- Pre-Check ---', True, [40, 40, 40], 0)

        # pipeline check 
        results = check.pipelineCheck(self.asset)

        if results : 
            # add info 
            infoResult = self.addInfo()
            results.update(infoResult)

            # check revision details 
            results.update({'Revision Details': {'status': False, 'message': 'Please snap changes details'}})

            if self.checkRevision(): 
                results.update({'Revision Details': {'status': True, 'message': ''}})
                self.checkList['Revision Details'] = True

            # check screen shot 
            dst = self.asset.publishImageFile()
            
            if str(self.ui.thumbnail_lineEdit.text()) : 
                dst = str(self.ui.thumbnail_lineEdit.text())

            if dst : 
                if os.path.exists(dst) : 
                    results.update({'screenShot': {'status': True, 'message': ''}})
                    self.checkList['screenShot'] = True

                    # display 
                    self.displayCapture(self.ui.snap_label, dst, 0.5)

                # check dependency
                logger.info('check dependency')
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
        task_sg_status_list = self.getShotgunStatus(status)
        
        # entity value
        project = self.asset.project()
        assetType = self.asset.type()
        assetSubType = self.asset.subType()
        assetName = self.asset.name()
        stepName = self.asset.department()
        taskName = self.asset.task()
        publishFile = os.path.basename(self.svPublishFile).split('.')[0]
        user = hook.getUser()
        description = str(self.ui.message_plainTextEdit.toPlainText())

        version = self.asset.getPublishVersion()
        versionStr = 'v%03d' % (version-1)
        revisionDir = '%s\\' % ('/').join([self.asset.getPath(), self.asset.publish, self.asset.department(), self.asset.task(), versionStr]).replace('/', '\\')

        ''' version ''' 
        logger.debug('Create version %s' % publishFile)
        logger.debug('%s %s %s %s %s %s %s %s %s' % (project, assetType, assetSubType, assetName, stepName, taskName, publishFile, sg_status_list, user))

        try : 
            versionEntity, assetEntity, taskEntity = shotgunPublish.publishVersion(project, assetType, assetSubType, assetName, stepName, taskName, publishFile, sg_status_list, user, description, revisionDir)

        except Exception as e : 
            logger.info('No asset in Shotgun')
            logger.debug(e)
            return False

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
            taskResult = shotgunPublish.publishTask(self.asset, assetEntity, stepName, taskEntity, task_sg_status_list, self.svPublishFile)
            self.setStatus('Set Task', taskResult)
            
            ''' set geo info ID ''' 
            # set ID 
            pipelineTools.setGeoInfo('id', assetEntity['id'])

        return True


    def getShotgunStatus(self, status) : 
        sg_status_list = self.sgStatusMap[status]
        if self.asset.department() in setting.shotgunStatusOverride : 
            return setting.overrideStatus

        else : 
            return sg_status_list


    ''' emails '''
    def sendEmail(self): 
        debug = self.ui.debug_checkBox.isChecked()
        send = self.ui.sendEmail_checkBox.isChecked()

        if send: 
            senderNameDisplay = '%s"%s"' % (config.title[self.asset.department()], self.asset.name())
            subject = '%s%s' % (config.subject[self.asset.department()], self.asset.name())
            senderEmail = config.senderEmail

            if not debug : 
                receivers = (',').join(config.publishReceivers[self.asset.department()])
                receiver_emails = (',').join(config.publishEmailReceivers[self.asset.department()])

            else : 
                receivers = (',').join(config.publishReceivers['debug'])
                receiver_emails = (',').join(config.publishEmailReceivers['debug'])

            emailBody = self.getEmailBodyFormat()
            emailUtils.doSendEmail(senderNameDisplay=senderNameDisplay, senderEmail=senderEmail, receivers=receivers, receiver_emails=receiver_emails, subject=subject, message=emailBody, files=[self.publishImage])
            logger.info('Email sent')

    def getEmailBodyFormat(self) : 
        body = []
        body.append('Project : %s' % self.asset.project())
        body.append('Asset Type : %s' % self.asset.type())
        body.append('Asset Name : %s' % self.asset.name())
        body.append('Published by : %s' % mc.optionVar(q='PTuser'))
        body.append('Version Name : %s' % self.svPublishFile)
        body.append('Status : %s' % str(self.ui.status_comboBox.currentText()))
        body.append('Publish File : %s' % self.svPublishFile)
        body.append('Publish Image : rvlink:// -l -play %s' % self.publishImage)

        body.append('Publish Message : %s' % self.translateUTF8(str(self.ui.message_plainTextEdit.toPlainText())))
        strBody = ('\n').join(body)

        return strBody

    def translateUTF8(self, text) : 
        return QtGui.QApplication.translate("ShotPublishUI", text, None, QtGui.QApplication.UnicodeUTF8)


    ''' cmds ''' 
    def publishFile(self) : 
        logger.info('### Start publishing files ... ###')

        # publish file 
        publishFile = self.svPublishFile
        workFile = self.asset.publishFile(showUser = True)
        workDir = self.asset.workDir()
        user = hook.getUser()
        self.setStatus('--- File Publish ---', True, [40, 40, 40], 0)

        if publishFile and workDir : 
            # uv merge AnimRig check 
            mergeUv = False
            needMerge = False 
            if self.asset.project() in setting.batchUvProject: 
                if self.asset.department() in [self.asset.rig, self.asset.uv] and self.ui.mergeUv_checkBox.isChecked(): 
                    logger.info('This is uv or rig department and checked always merge uv')
                # needMerge, publishUvFile, AnimRig = check_core.check_merge(self.asset)
                    publishDir, publishUvFiles = self.asset.listPublishFiles(self.asset.uv, '%s_%s' % (self.asset.uv, self.asset.taskLOD()))
                    print 'publishDir', publishDir
                    print 'publishUvFiles', publishUvFiles
                    if publishUvFiles: 
                        publishUvFile = '%s/%s' % (publishDir, sorted(publishUvFiles)[-1])
                        refPath = self.asset.getPath('ref')
                        animRig = '%s/%s' % (refPath, self.asset.getRefNaming('anim'))


                # if true, always merge 
                # if self.ui.mergeUv_checkBox.isChecked(): 
                #     logger.info('This is uv or rig department and checked always merge uv')
                #     mergeUv = True

                # auto 
                        message = 'Do you want to merge new uv to Anim Rig? If this publish has the same uv, click No'
                        # message = 'Uv published file is newer than rig. Do you want to merge new uv to Anim_Rig?'
                        # if self.asset.department() == self.asset.uv: 
                        #     message = 'Do you want to merge new uv to Anim Rig? If this publish has the same uv, click No'
                        confirmMerge = QtGui.QMessageBox.question(self, 'Merge uv require', message, QtGui.QMessageBox.Ok, QtGui.QMessageBox.No)

                        if confirmMerge == QtGui.QMessageBox.Ok: 
                            mergeUv = True

            else: 
                logger.debug('%s not in batchUv list project' % self.asset.project())

            
            saveFile = '%s/%s' % (workDir, os.path.basename(workFile))
            # saveFile = hook.addUser(saveFile, user)

            # save file 
            logger.debug('Saving file -> %s' % saveFile)
            saveResult = hook.save(saveFile, rename = False)
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
            extraResults = extra.publish(self.asset, batch, mainUI=self)

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
 
            # merge uv 
            if mergeUv: 
                if self.asset.department() == self.asset.uv: 
                    publishUvFile = publishFile

                logger.info('Start merging uv ...')
                logger.debug('param publishedUv %s' % publishUvFile)
                logger.debug('param AnimRig %s' % animRig)
                mergeResult = extra.mergeUvToAnimRig(publishUvFile, animRig)

                if mergeResult : 
                    if self.asset.department() == self.asset.rig: 
                        rigWithUv = incrementFile.replace('.ma', '_withUv.ma')
                        rigUvCopyResult = fileUtils.copy(animRig, rigWithUv)
                        if rigUvCopyResult: 
                            mergeResult.update({'Copy rig work with uv': {'status': True, 'message': ''}} )

                    for each in mergeResult : 
                        title = each
                        status = mergeResult[each]['status']
                        message = mergeResult[each]['message']
                        self.setStatus('%s' % title, status)
                        logger.info('%s %s' % (title, message))

            if saveResult : 
                # set status 
                logger.debug('Increment file -> %s' % incrementFile)

                # increment file
                # check increment override with root file 
                fileToIncrement = str(self.ui.incrementFile_lineEdit.text())
                incrementOverride = False 
                
                if os.path.exists(fileToIncrement) and self.ui.incrementRoolFile_checkBox.isChecked() : 
                    incrementOverride = True

                if batch : 
                    if not incrementOverride : 
                        incrementResult = hook.save(incrementFile)

                    # override increment 
                    else : 
                        increment = entityInfo.info(fileToIncrement)
                        incrementFile = increment.nextVersion()
                        incrementResult = fileUtils.copy(fileToIncrement, incrementFile)

                else : 
                    incrementResult = fileUtils.copy(saveResult, incrementFile)

                if incrementResult : 
                    self.setStatus('Increment File', incrementResult)
                    logger.info('Increment file to %s' % incrementFile)

        return True


    def listPublishFiles(self) : 
        logger.info('listing publish files ...')
        publishDir = self.asset.publishDir()
        files = fileUtils.listFile(publishDir, 'ma')
        listWidget = 'publish_listWidget'
        iconPath = self.mayaIcon
        color = [0, 0, 0]

        self.ui.publish_listWidget.clear()

        for eachFile in files : 
            self.addListWidgetItem(listWidget, eachFile, iconPath, color, 1)

        logger.info('completed')


    def listRefFiles(self) : 
        logger.info('listing ref files ...')
        refPath = self.asset.getPath('ref')
        files = fileUtils.listFile(refPath)
        listWidget = 'ref_listWidget'
        iconPath = self.mayaIcon
        color = [0, 0, 0]

        self.ui.ref_listWidget.clear()

        for eachFile in files : 
            self.addListWidgetItem(listWidget, eachFile, iconPath, color, 1)

        logger.info('completed')


    def addInfo(self) : 
        try : 
            # add attr 
            pipelineTools.assignGeoInfo()

            # assign department info 
            pipelineTools.setGeoInfo(self.asset.department(), self.asset.fileName())

            # assign basic info 
            pipelineTools.setGeoInfo('project', self.asset.project())
            pipelineTools.setGeoInfo('assetName', self.asset.name())
            pipelineTools.setGeoInfo('ref', self.asset.getPath('ref'))
            pipelineTools.setGeoInfo('lod', self.asset.taskLOD())
            data = pipelineTools.readGeoInfo('data')

            # assign data 
            datas = []
            if data : 
                datas = eval(data)
                
            if not self.asset.fileName() in datas : 
                datas.append(self.asset.fileName())

            pipelineTools.setGeoInfo('data', str(datas))

            if self.asset.department() in setting.addInfoDep : 
                pipelineTools.autoAssign()

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

        if os.path.exists(current) : 
            if not current == targetFile : 
                fileUtils.copy(current, targetFile)
                logger.debug('Copy thumbnail %s -> %s' % (current, targetFile))

            else : 
                logger.debug('Thumbnail not copy')

            # copy to images/icon 
            if self.asset.department() in setting.heroIconDept : 
                heroIcon = self.asset.getPath('icon')
                fileUtils.copy(current, heroIcon)
                logger.debug('Copy hero thumbnail')

        if os.path.exists(currentMedia) : 
            ext = currentMedia.split('.')[-1]
            targetMedia = '%s.%s' % (targetFile.split('.')[0], ext)
            self.publishImage = targetMedia

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
            #   subMenu3.addAction(each)

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

    def getRevisionVersion(self, revisionDir, version): 
        files = fileUtils.listFile(revisionDir, 'png')

        if files: 
            lastFile = sorted(files)[-1]
            digit = lastFile.split('.')[-2]

            if digit.isdigit(): 
                nextVersion = int(digit) + 1 
                padNum = '%03d' % nextVersion
                # Result: frz_sinkholeGndA_model_md #

            else: 
                padNum = '001'

        else: 
            padNum = '001'

        baseFile = self.asset.getFileNaming()
        fileName = '%s_%s_revision.%s.png' % (baseFile, version, padNum)
        snapFile = '%s/%s' % (revisionDir, fileName)

        return snapFile
        



    def displayCapture(self, widget, iconPath, display = 1) : 
        w = self.h * display
        h = self.w * display
        widget.setPixmap(QtGui.QPixmap(iconPath).scaled(w, h, QtCore.Qt.KeepAspectRatio))


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
    def addListWidgetItem(self, listWidget, text='', iconPath='', color=[], addIcon = 1, data='', size=16) : 
        cmd = 'QtGui.QListWidgetItem(self.ui.%s)' % listWidget
        item = eval(cmd)

        if addIcon : 
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(iconPath),QtGui.QIcon.Normal,QtGui.QIcon.Off)
            item.setIcon(icon)

        if data: 
            item.setData(QtCore.Qt.UserRole, data)

        if text: 
            item.setText(text)
        item.setBackground(QtGui.QColor(color[0], color[1], color[2]))

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