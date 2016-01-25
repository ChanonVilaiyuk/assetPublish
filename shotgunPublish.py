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


def publishVersion(project, assetType, assetSubType, assetName, taskName, publishFile, status, user) : 
	# create version 
	assetEntity = getAssetID(project, assetType, assetSubType, assetName)
	userEntity = getUser(user)

	if assetEntity : 
		assetID = assetEntity['id']
		projectEntity = assetEntity['project']
		taskEntity = getTaskID(assetEntity, taskName)

		if taskEntity : 
			versionEntity = createVersion(projectEntity, assetEntity, taskEntity, publishFile, status, userEntity, description = '')

			return versionEntity, assetEntity, taskEntity


def publishTask(entity, taskEntity, status, path, outputPath) : 
	taskID = taskEntity['id']
	task = taskEntity['content']
	path = path.replace('/', '\\')
	heroStatus = 'aprv'

	# update this task
	data = { 'sg_status_list': status, 
			'sg_hero_2' : {'local_path': path, 'name': os.path.basename(path)}
			}
	result = sg.update('Task', taskID, data) 
	logger.debug('Update task %s - %s' % (task, status))

	# update downstream
	if task in statusMap2.keys() : 
		targetTasks = statusMap2[task]
		targetHeroTasks = []

		filters = [['entity','is', entity]]
		fields = ['content', 'id']
		taskEntities = sg.find('Task', filters, fields)

		if task in outputMap2.keys() : 
			targetHeroTasks = outputMap2[task]

		for each in taskEntities : 
			taskName = each['content']
			taskID = each['id']

			if taskName in targetTasks : 
				data = {'sg_workfile' : {'local_path': path, 'name': os.path.basename(path)}}
				result = sg.update('Task', taskID, data)
				targetTasks.remove(taskName)
				logger.debug('Update dependency task %s %s' % (taskName, status))

			if taskName in targetHeroTasks : 
				data = {'sg_hero_2' : {'local_path': path, 'name': os.path.basename(path)}, 
						'sg_status_list': heroStatus}
				result = sg.update('Task', taskID, data)
				targetHeroTasks.remove(taskName)
				logger.debug('Update output task %s %s' % (taskName, heroStatus))

		if not targetTasks and not targetHeroTasks : 
			return True

		else : 
			logger.error('%s %s not found' % (targetTasks, targetHeroTasks), '')


def getAssetID(project, assetType, assetSubType, assetName) : 
	filters = [['project.Project.name', 'is', str(project)], 
				['code', 'is', str(assetName)], 
				['sg_asset_type', 'is', str(assetType)], 
				['sg_subtype', 'is', str(assetSubType)]]

	asset = sg.find_one('Asset', filters = filters, fields = ['id', 'code', 'project'])
	return asset


def getTaskID(entity, taskName) : 
	fields = ['id', 'code', 'content', 'sg_hero_2', 'sg_client', 'sg_status_list', 'step.Step.code']
	filters = [
				['entity','is', entity],
				['content', 'is', taskName]
				]

	task = sg.find_one('Task', filters, fields)
	return task


def getUser(localUser) : 
	filters = [['sg_localuser','is', localUser]]
	fields = ['name', 'id']
	userEntity = sg.find_one('HumanUser', filters, fields)

	return userEntity


def createVersion(projectEntity, entity, taskEntity, versionName, status, userEntity, description) : 
	data = { 'project': projectEntity,
			 'code': versionName,
			 'entity': entity,
			 'sg_task': taskEntity,
			 'sg_status_list': status, 
			 'description' : description}

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
	thumbnailResult = sg.upload_thumbnail('Version', versionEntity['id'], thumbnail)
	# logger.debug('Upload thumbnail %s' % thumbnailResult)

	return thumbnailResult