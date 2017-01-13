''' uv '''
import os,sys,traceback,string,subprocess,shutil
import maya.cmds as mc 

from tool.utils import pipelineTools, fileUtils
from tools import getMayaPathFile
reload(fileUtils)
reload(getMayaPathFile)
reload(pipelineTools)
from tool.utils.batch import rigPublish
reload(rigPublish)
from tool.ptAlembic import exportShade
reload(exportShade)
from tool.utils import abcUtils
reload(abcUtils)

import setting
reload(setting)

# from tools import pipelineTools
# reload(pipelineTools)

def publish(asset, mainUI=None) : 
    # path 
    dataPath = '%s/data' % asset.getPath(asset.department(), asset.task())
    edlUVPath = '%s/%s' % (dataPath, 'edl')
    shadeFilePath = '%s/%s' % (dataPath, 'shadeFile')
    publishVer = os.path.basename(asset.publishFile().split('.')[0])
    convertTexture = True
    if mainUI: 
        convertTexture = mainUI.ui.texture_checkBox.isChecked()

    if asset.project() not in setting.uvShadeOverride : 
        # result1 = exportShdEdl(edlUVPath, shadeFilePath, publishVer)
        result1 = exportShadeYml(asset)

        if convertTexture: 
            result2 = doConvertTexture(asset)
        else: 
            result2 = [False, '']

        result = {'Export Edl': {'status': result1[0], 'message': result1[1]}, 
                    'Texture Resolution': {'status': result2[0], 'message': result2[1]}}

    else : 
        # result1 = exportShdEdl2(asset, edlUVPath, shadeFilePath, publishVer)
        result1 = exportShadeYml(asset)

        if convertTexture: 
            result2 = doConvertTexture(asset)
        else: 
            result2 = [False, '']

        result = {'Export Edl': {'status': result1[0], 'message': result1[1]}, 
                    'Texture Resolution': {'status': result2[0], 'message': result2[1]}}

    result4 = exportABC(asset)
    result.update(result4)

    return result

def exportShdEdl(edlUVPath, shadeFilePath, publishVer) : 
    # by Nook
    try : 
        shadeGrp  = [n for n in mc.ls(type='shadingEngine')if not n == 'initialParticleSE' and not n =='initialShadingGroup' and not mc.referenceQuery(n,inr=1)]
        shadeFile = os.path.join(shadeFilePath,'%s.ma' % publishVer.replace('uv','uv_shadeFile'))
        edlDict = ''
        shadeGrpExport = []

        # this line will check facial texture and disconnect it from rig
        print 'check facial'
        pipelineTools.facialShaderDisconnect()

        materials = []
        for grp in shadeGrp:
            if  mc.listConnections('%s.surfaceShader' % grp):
                material = mc.listConnections('%s.surfaceShader' % grp)[0]
                # TA add this, check first if shader has rig
                if checkValidShader(material) : 
                    if not 'noExport' in material :
                        shadeGrpExport.append(grp)
                        edlDict += '%s' % material # get materail
                        materials.append('%s' % material)
                        mc.hyperShade(o= material)
                        for sl in mc.ls(sl=True):
                            edlDict += ' %s' % sl # get object
                        edlDict += '\r\n'

        print edlDict

        if not os.path.exists(edlUVPath.replace('\\','/')):
            os.makedirs(edlUVPath.replace('\\','/'))

        f = open(os.path.join(edlUVPath,"%s_edl.txt" % publishVer.replace('uv','uv_shadeFile')),'w')
        f.write(edlDict)
        f.close

        if shadeGrpExport:
            mc.select(shadeGrpExport,noExpand=True)

        if not os.path.exists(shadeFilePath):
            os.makedirs(shadeFilePath)

        mc.file(shadeFile,op='v=0',typ='mayaAscii',pr=True,es=True, f = True)
        print 'Exported shade.'
        print os.path.join(edlUVPath,"%s_edl.txt" % publishVer.replace('uv','uv_shadeFile'))

        return [True, '']

    except Exception as e : 
        return [False, e]


def exportShdEdl2(asset, edlUVPath, shadeFilePath, publishVer) : 
    current = asset.thisScene()
    mc.delete()
    grp = 'SuperRoot_Grp'
    mc.delete(grp)
    exportShdEdl(edlUVPath, shadeFilePath, publishVer)
    mc.file(current, o=True, f=True)

    # pipelineTools.writeTextureInfoToFile(os.path.join(uvDataTexturePath,"%s.txt" % publishVer.replace('uv','uv_texture')))

def exportShadeYml(asset) : 
    publishFile = os.path.splitext(os.path.basename(asset.publishFile()))[0]
    publishVersion = asset.getPublishVersion(padding=True)
    exportGrp = 'Geo_Grp'
    dataPath = asset.dataPath('uv', data='mtl')

    if mc.objExists(exportGrp): 
        maFile = '%s/%s.ma' % (asset.dataPath('uv', data='mtl'), publishFile.replace('_%s' % publishVersion, '_mtl_%s' % publishVersion))
        dataFile = '%s/%s.yml' % (asset.dataPath('uv', data='yml'), publishFile.replace('_%s' % publishVersion, '_yml_%s' % publishVersion))

        if not os.path.exists(os.path.dirname(maFile)): 
            os.makedirs(os.path.dirname(maFile))
        if not os.path.exists(os.path.dirname(dataFile)): 
            os.makedirs(os.path.dirname(dataFile))

        fileResult = exportShade.exportUvShadeNode(maFile, exportGrp)
        dataResult = exportShade.exportData(dataFile, exportGrp)

        return [True, '']

    else: 
        return [False, '']

def doConvertTexture(asset) : 
    convertTextureCmd(asset)
    return [True, '']

def convertTextureCmd(asset):
    print 'Convert texture'
    assetPath = asset.texturePath()
    allFiles = getFileNodes(assetPath)

    channel = {'0': '', '1':'-outchannelmap all','3':'-outrgb','4':''}
    type = {'8192':'8K','4096':'4K','2048':'2K','1024':'1K','512':'5H','256':'2H'}
    stepScale = {'8192':6,'4096':5,'2048':4,'1024':3,'512':2,'256':1}

    for file in allFiles:
        filePath = mc.getAttr('%s.fileTextureName' % file)
        print filePath
        if os.path.exists(filePath.replace('\\','/')):
            imageName = os.path.basename(filePath).split('.')[0]

            # vray tile exr
            output = os.path.join(assetPath,('\\').join([asset.taskLOD(),'exr']))
            if not os.path.exists(output.replace('\\','/')):
                os.makedirs(output.replace('\\','/')) 

            version = mc.about(v = True)
            cmd = '"C:/Program Files/Chaos Group/V-Ray/Maya 2012 for x64/bin/img2tiledexr.exe" '

            if '2015' in version : 
                cmd = '"C:/Program Files/Chaos Group/V-Ray/Maya 2015 for x64/bin/img2tiledexr.exe" '

            if '2016' in version : 
                cmd = '"C:/Program Files/Chaos Group/V-Ray/Maya 2016 for x64/bin/img2tiledexr.exe" '

            cmd += '%s ' % filePath.replace('\\','/')
            cmd += '%s.exr -32bit -compression none -tileSize 64x64 -linear off' % os.path.join(output,imageName).replace('\\','/')
            subprocess.Popen(cmd,stdout=subprocess.PIPE).communicate()[0]
            

            rvReport = subprocess.Popen('"O:/systemTool/convertor/Tweak/RV-3.12.20-32/bin/rvls.exe" -l "%s"' % filePath,stdout=subprocess.PIPE).communicate()[0]
            rvReport = rvReport.split('\r\n')
            rec = {}
            print rvReport
            name = string.rsplit(rvReport[0])
            field = string.rsplit(rvReport[1])
            for i in range(len(name)):
                rec[name[i]] = field[i]
            print rec
            orgSize = rec['h']
            orgTyp = rec['typ']
            orgChannel = rec['#ch']
            

            if imageName[-1] == 'K' or imageName[-1] == 'H':
                imageName = imageName[0:-3]
            imageTyp = os.path.basename(filePath).split('.')[-1]
            scale = 1.00
            newSize = orgSize
            if not orgSize in stepScale.keys():
                newSize = checkSize(int(orgSize))
            for i in range(stepScale[newSize]):
                output = os.path.join(assetPath,('\\').join([asset.taskLOD(),type['%s'% int(int(newSize)*scale)]]))

                newFile = "%s/%s_%s.%s" % (output,imageName,type['%s'% int(int(newSize)*scale)],imageTyp)
                if not os.path.exists(output.replace('\\','/')):
                    print output.replace('\\','/')
                    os.makedirs(output.replace('\\','/')) 

                if not scale == 1.00 or not newSize == orgSize:
                    #print scale,orgTyp.split('i')[0],channel[orgChannel]
                    cmd = '"O:/systemTool/convertor/Tweak/RV-3.12.20-32/bin/rvio.exe" '
                    cmd += '"%s" ' % filePath
                    cmd += '-scale %s -codec "NONE" -outformat %s bit %s ' % (scale,
                                                                            orgTyp.split('i')[0],
                                                                            channel[orgChannel])
                    cmd += '-quality 1.0  -o "%s"' % newFile

                    subprocess.Popen(cmd,stdout=subprocess.PIPE)
                    print 'see here ============================='
                    print orgTyp.split('i')[0]
                    print channel[orgChannel]
                    print cmd 
                else:
                    if not os.path.exists(newFile.replace('\\','/')):
                        fileUtils.copy(filePath.replace('\\','/'),newFile)
                    mc.setAttr('%s.fileTextureName' % file,newFile.replace('/','\\'),type='string')

                scale *= 0.5

def checkSize(pix):
    offset = 100

    if pix >= (8192-offset) and pix > 8192:
        pix = 8192
    elif pix >= (4096-offset) and pix < (8192-offset):
        pix = 4096
    elif pix >= (2048-offset) and pix < (4096-offset):
        pix = 2048
    elif pix >= (1024-offset) and pix < (2048-offset):
        pix = 1024
    elif pix >= (512-offset) and pix < (1024-offset):
        pix = 512
    else:
        pix = 256

    return ('%s' % pix)


# ta add this 
def getFileNodes(assetPath) : 
    from tools import fileUtils,getMayaPathFile
    reload(getMayaPathFile)
    exceptions = ['Lego_FRD360']
    project = getMayaPathFile.searchProjectName(assetPath)
    exceptLayerTextureNode = 'facialRender_lt'

    if not project in exceptions : 
        fileNodes = mc.ls(type="file")
        validNodes = []
        if fileNodes: 
            for node in fileNodes: 
                connections = mc.listConnections('%s.outColor' % node, s=False, d=True)
                if connections: 
                    if not exceptLayerTextureNode in connections: 
                        validNodes.append(node)
                else: 
                    validNodes.append(node)

            return validNodes

        else: 
            return []

    else : 
        nodes = mc.ls(type = 'file')
        validNodes = [a for a in nodes if not 'aFile' in a and not 'rFile' in a]

        return validNodes 


def checkValidShader(shader) : 
    """ check for shader that does not contain rig """ 
    invalidNodes = ['plusMinusAverage', 'multiplyDivide', 'locator', 'curve']
    nodeType = mc.objectType(shader)

    # if invalid node
    if nodeType in invalidNodes : 
        return False

    # node is valid
    else : 
        # list all connections
        shaders = mc.listConnections(shader, s = True, d = False)
        # shaders = list(set(shaders))

        if shaders : 
            # filter out 
            if shader in shaders : 
                shaders.remove(shader)
                
            # loop through each node
            trueCount = 0 
            for each in shaders : 
                value = checkValidShader(each)

                if not value : 
                    return value

                else : 
                    trueCount += 1 

            if trueCount == len(shaders) : 
                return True

        # if no connection and valid node, True 
        else : 
            return True

def checkValidShader2(shader) : 
    """ check for shader that does not contain rig """ 
    invalidNodes = ['plusMinusAverage', 'multiplyDivide', 'locator', 'curve']
    nodeType = mc.objectType(shader)

    # if invalid node
    if nodeType in invalidNodes : 
        return False

    # node is valid
    else : 
        # list all connections
        shaders = mc.listConnections(shader, s = True, d = False)
        # shaders = list(set(shaders))

        if shaders : 
            # filter out 
            if shader in shaders : 
                shaders.remove(shader)

            # loop through each node
            trueCount = 0 
            for each in shaders : 
                value = checkValidShader2(each)

                if not value : 
                    return value

                else : 
                    trueCount += 1 

            if trueCount == len(shaders) : 
                return True

        # if no connection and valid node, True 
        else : 
            return True

def exportABC(asset): 
    publishFile = asset.publishFile(abc=True)
    start = mc.currentTime(q=True)
    end = mc.currentTime(q=True)
    result = abcUtils.exportABC([setting.exportGrp], publishFile, start, end)
    status = 'failed'
    if result: 
        status = 'success'

    return {'ABC Export': {'status': status, 'message': result}}