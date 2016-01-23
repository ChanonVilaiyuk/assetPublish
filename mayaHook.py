import maya.cmds as mc 
from tool.utils import mayaTools
reload(mayaTools)

def snapShotCmd(dst, w, h) : 
	format = 'png'
	st = 1
	sequencer = False
	result = mayaTools.captureScreen2(dst, format, st, sequencer, w, h)

	return result


def getUser() : 
	return mc.optionVar(q = 'PTuser')


def save(fileName) : 
	mc.file(rename = fileName)
	result = mc.file(save = True, type = 'mayaAscii')

	return result

def addUser(fileName, user) : 
	return '%s_%s.%s' % (fileName.split('.')[0], user, fileName.split('.')[-1])