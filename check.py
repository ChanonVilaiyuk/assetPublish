''' pipeline check '''
from tool.publish.asset import pipeline
reload(pipeline)

import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def pipelineCheck(asset) : 
	pipeline.cleanNamespace()
	group = pipeline.group()
	name = pipeline.name()
	cleanPlugin = pipeline.removeUnknownPlugin()

	if name : 
		clean1 = pipeline.cleanDefaultRenderLayer()
		clean2 = pipeline.cleanTurtleRender()
		clean3 = pipeline.cleanUnknownNode()
		clean4 = pipeline.cleanDisplayLayer()
		clean = False
		cleanTitles = ['Clean DefaultRenderLayer', 'Clean TurtleRender', 'Clean Unknown nodes', 'Clean DisplayLayer']

		if clean1[0] and clean2[0] and clean3[0] and clean4[0]: 
			clean = True

		nameStatus = False
		nameMessage = ''

		if name == True : 
			nameStatus = True

		else : 
			nameMessage = name

		texturePathCheck = pipeline.texturePath()
		
		result = {'1. Check Geo_Grp': {'status': group, 'message': ''}, 
					'2. No Duplicated name': {'status': nameStatus, 'message': nameMessage}, 
					'3. Clean file': {'status': clean, 'message': '%s:%s %s:%s %s:%s %s:%s' % (cleanTitles[0], clean1[1], cleanTitles[1], clean2[1], cleanTitles[2], clean3[1], cleanTitles[3], clean4[1])}, 
					'Clean unknown plugins': {'status': cleanPlugin, 'message': cleanPlugin[1]}, 
					'screenShot': {'status': False, 'message': 'No Screen Shot'}, 
					'TexturePath': {'status': texturePathCheck[0], 'message': texturePathCheck[1]}
					}

		if asset.department() == 'rig' : 
			rigGrpHiddenCheck = pipeline.rigGrpHiddenCheck()
			result.update({'CheckHiddenOutliner': {'status': rigGrpHiddenCheck[0], 'message': rigGrpHiddenCheck[1]}})

	else : 
		result = {'Geo_Grp Duplicated': {'status': False, 'message': 'More than one group matched name'}}

	return result