import sys, platform, os
from datetime import datetime

from tool.utils import customLog
reload(customLog)

from tool.publish.asset import setting
reload(setting)

scriptName = 'ptAssetPublish'
logger = customLog.customLog()
logger.setLevel(customLog.DEBUG)
logger.setLogName(scriptName)

if platform.system() == 'Windows':
	sys.path.append('O:/studioTools/lib')
	sys.path.append('//10.66.1.12/dsGlobal/studioTools/lib')

from shotgun_api3 import Shotgun

# connection to server
server = 'https://pts.shotgunstudio.com'
script = 'ptTools'
id = 'ec0b3324c1ab54cf4e21c68d18d70f2f347c3cbd'
sg = Shotgun(server, script, id)


''' shotgun '''

statusMap = setting.statusMap
statusMap2 = setting.statusMap2
outputMap2 = setting.outputMap2


def publishVersion(project, assetType, assetSubType, assetName, stepName, taskName, publishFile, status, user, description='', revisionLink='') : 
	# create version 
	logger.debug('publishVersion --------------------------------------------------')
	assetEntity = getAssetID(project, assetType, assetSubType, assetName)
	userEntity = getUser(user)

	if assetEntity : 
		assetID = assetEntity['id']
		projectEntity = assetEntity['project']
		taskEntity = getTaskID(assetEntity, stepName, taskName)

		if taskEntity : 
			versionEntity = createVersion(projectEntity, assetEntity, taskEntity, publishFile, status, userEntity, description=description, revisionLink=revisionLink)

			return versionEntity, assetEntity, taskEntity


def publishTask(asset, entity, stepName, taskEntity, status, path) : 
	logger.debug('publishTask --------------------------------------------------')
	taskID = taskEntity['id']
	task = taskEntity['content']
	path = path.replace('/', '\\')
	heroStatus = 'aprv'
	stepEntity = getStepEntity(stepName)

	try : 

		# update this task
		data = { 'sg_status_list': status, 
				'sg_hero_2' : {'local_path': path, 'name': os.path.basename(path)}
				}
		result = sg.update('Task', taskID, data) 
		logger.debug('Update task %s - %s' % (task, status))

		# update downstream
		stepTask = '%s-%s' % (stepName, task)
		print stepTask
		print statusMap2.keys()

		if stepTask in statusMap2.keys() : 
			targetTasks = statusMap2[stepTask]

			filters = [['entity','is', entity]]
			fields = ['content', 'id', 'project', 'step']
			taskEntities = sg.find('Task', filters, fields)

			if taskEntities : 
				sgTaskDict = getTaskEntityInfo(taskEntities)
				projectEntity = taskEntities[0]['project']

				for targetTask in targetTasks : 
					if targetTask in sgTaskDict.keys() : 
						# update 
						data = {'sg_workfile' : {'local_path': path, 'name': os.path.basename(path)}}
						taskID = sgTaskDict[targetTask]['id']
						result = sg.update('Task', taskID, data)
						logger.debug('Update dependency %s -> %s' % (targetTask, path))

					else : 
						taskName = targetTask.split('-')[-1]
						step = setting.steps[targetTask.split('-')[0]]
						data = {'project': projectEntity, 'content': taskName, 'entity': entity, 'step': step, 
								'sg_workfile' : {'local_path': path, 'name': os.path.basename(path)}, 'sg_status_list': 'aprv'}

						result = sg.create('Task', data)
						logger.debug('Create task dependency %s -> %s' % (taskName, path))
			
			if stepTask in outputMap2.keys() : 
				targetHeroTasks = outputMap2[stepTask]

				for targetHeroTask in targetHeroTasks : 
					publish = True
					# check if this asset type need to export output 
					if targetHeroTask in setting.checkExportSetting.keys() : 
						exportType = setting.checkExportSetting[targetHeroTask]

						if not asset.type() in exportType : 
							publish = False

					if publish : 
						data = dict()
						heroStatus = 'udt'

						# check output file exists 
						outputFile = getOutputFile(asset, targetHeroTask)
						if outputFile : 	
							if os.path.exists(outputFile) : 
								heroStatus = 'aprv'
								
								if asset.department() in setting.shotgunStatusOverride : 
									heroStatus = setting.overrideStatus

							data.update({'sg_hero_2' : {'local_path': outputFile, 'name': os.path.basename(outputFile)}})
							logger.debug('Add output path %s' % outputFile)

						else : 
							logger.debug('Output not found %s - %s' % (targetHeroTask, outputFile))

						if targetHeroTask in sgTaskDict.keys() : 
							# update 		
							data.update({'sg_status_list': heroStatus})
							taskID = sgTaskDict[targetHeroTask]['id']
							result = sg.update('Task', taskID, data)
							logger.debug('Update dependency %s -> %s' % (targetHeroTask, outputFile))

						else : 
							# create 
							taskName = targetHeroTask.split('-')[-1]
							step = setting.steps[targetHeroTask.split('-')[0]]
							data.update({'project': projectEntity, 'content': taskName, 'entity': entity, 'step': step, 'sg_status_list': 'aprv'})

							result = sg.create('Task', data)
							logger.debug('Create output task dependency %s -> %s' % (taskName, outputFile))



		return True 

	except Exception as e : 
		logger.debug('Error update task!! %s' % e)
		return False 




def getAssetID(project, assetType, assetSubType, assetName) : 
	filters = [['project.Project.name', 'is', str(project)], 
				['code', 'is', str(assetName)], 
				['sg_asset_type', 'is', str(assetType)], 
				['sg_subtype', 'is', str(assetSubType)]]

	asset = sg.find_one('Asset', filters = filters, fields = ['id', 'code', 'project'])
	return asset


def getTaskID(entity, stepName, taskName) : 
	# check if step is in setting 
	stepEntity = getStepEntity(stepName)
	if stepEntity : 

		fields = ['id', 'code', 'content', 'sg_hero_2', 'sg_client', 'sg_status_list', 'step.Step.code']
		filters = [['step', 'is', stepEntity], 
					['entity','is', entity],
					['content', 'is', taskName]]

		task = sg.find_one('Task', filters, fields)
		return task


def getOutputFile(asset, stepTask) : 
	if stepTask in setting.outputFileMap.keys() : 
		outputKey = setting.outputFileMap[stepTask]
		refPath = asset.getPath('ref')
		refFile = asset.getRefNaming(outputKey, showExt = True)

		path = '%s/%s' % (refPath, refFile)

		logger.debug('Output file %s' % path)
		if os.path.exists(path) : 
			return path.replace('/', '\\') 

		# else : 
		# 	logger.debug('Path not exists %s' % path)


def getUser(localUser) : 
	filters = [['sg_localuser','is', localUser]]
	fields = ['name', 'id']
	userEntity = sg.find_one('HumanUser', filters, fields)

	return userEntity


def getStepEntity(stepName) : 
	if stepName in setting.steps.keys() : 
		stepEntity = setting.steps[stepName]
		return stepEntity


def getTaskEntityInfo(taskEntities) : 
	sgTaskDict = dict()

	for each in taskEntities : 
		task = each['content']
		stepID = each['step']['id']
		step = setting.stepSgPipeMap[stepID]
		key = '%s-%s' % (step, task)
		sgTaskDict[key] = each
		
	return sgTaskDict


def createVersion(projectEntity, entity, taskEntity, versionName, status, userEntity, description, revisionLink='') : 
	data = { 'project': projectEntity,
			 'code': versionName,
			 'entity': entity,
			 'sg_task': taskEntity,
			 'sg_status_list': status, 
			 'description' : description}

	if revisionLink: 
		data.update
		data.update({'sg_revision_dir': {'local_path': revisionLink, 'name': os.path.split(revisionLink)[-1]}})

	if userEntity : 
		data.update({'user': userEntity})

	
	# create version 
	versionEntity = sg.create('Version', data)
	logger.debug('Version %s' % versionEntity)

	return versionEntity


def uploadMedia(versionEntity, media) : 
	# upload media 
	media = media.replace('/', '\\')
	mediaResult = sg.upload('Version', versionEntity['id'], media, 'sg_uploaded_movie')
	# logger.debug('Upload media %s' % mediaResult)

	return mediaResult

def uploadThumbnail(versionEntity, thumbnail) : 
	# upload thumbnail 
	thumbnail = thumbnail.replace('/', '\\')
	if os.path.exists(thumbnail) : 
		thumbnailResult = sg.upload_thumbnail('Version', versionEntity['id'], thumbnail)
		# logger.debug('Upload thumbnail %s' % thumbnailResult)

		return thumbnailResult

	else : 
		logger.debug('thumbnail %s not exists' % thumbnail)