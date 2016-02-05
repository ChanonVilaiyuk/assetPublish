''' shotgun '''

statusMap = {
			'model-model_md': ['uv-uv_md', 'rig-rig_md'], 'uv-uv_md': ['surface-shade_md'], 'rig-rig_md': [], 'surface-shade_md': [], 
			'model-model_hi': ['uv-uv_hi', 'rig-rig_hi'], 'uv-uv_hi': ['surface-shade_hi'], 'rig-rig_hi': [], 'surface-shade_hi': [], 
			'model-model_lo': ['uv-uv_lo', 'rig-rig_lo'], 'uv-uv_lo': ['surface-shade_lo'], 'rig-rig_lo': [], 'surface-shade_lo': [], 
			'model-model_master': ['uv-uv_master'], 'uv-uv_master': ['rig-rig_master'], 'rig-rig_master': [], 
			}

outputMap = {
			'model-model_md': ['hero-gpu', 'hero-ad', 'hero-geo'], 'rig-rig_md': ['hero-anim_md'], 'surface-shade_md': ['hero-render_md', 'hero-cache_md', 'hero-vrayProxy_md', 'hero-vPrxoy_md'], 
			'model-model_hi': ['hero-gpu', 'hero-ad', 'hero-geo'], 'rig-rig_hi': ['hero-anim_hi'], 'surface-shade_hi': ['hero-render_hi', 'hero-cache_hi', 'hero-vrayProxy_hi', 'hero-vPrxoy_hi'], 
			'rig-rig_lo': ['hero-anim_lo'], 'surface-shade_lo': ['hero-render_lo', 'hero-cahce_lo', 'vrayProxy_lo', 'hero-vPrxoy_lo']
			}


statusMap2 = {
			'model-model_md': ['uv-uv_md', 'rig-rig_md'], 'uv-uv_md': ['rig-rigUV_md'], 'rig-rig_md': [], 'rig-rigUV_md': ['surface-shade_md'], 'surface-shade_md': [], 
			'model-model_hi': ['uv-uv_hi', 'rig-rig_hi'], 'uv-uv_hi': ['rig-rigUV_hi'], 'rig-rig_hi': [], 'rig-rigUV_hi': ['surface-shade_hi'], 'surface-shade_hi': [], 
			'model-model_lo': ['uv-uv_lo', 'rig-rig_lo'], 'uv-uv_lo': ['rig-rigUV_lo'], 'rig-rig_lo': [], 'rig-rigUV_lo': ['surface-shade_lo'], 'surface-shade_lo': [], 
			'model-model_master': ['uv-uv_master'], 'uv-uv_master': ['rig-rig_master'], 'rig-rig_master': [], 
			}


outputMap2 = {
			'model-model_md': ['hero-gpu', 'hero-ad', 'hero-geo'], 'rig-rig_md': ['hero-anim_md'], 'rig-rigUV_md': ['hero-anim_md'], 'surface-shade_md': ['hero-render_md', 'hero-cache_md', 'hero-vrayProxy_md', 'hero-vPrxoy_md'], 
			'model-model_hi': ['hero-gpu', 'hero-ad', 'hero-geo'], 'rig-rig_hi': ['hero-anim_hi'], 'rig-rigUV_hi': ['hero-anim_hi'], 'surface-shade_hi': ['hero-render_hi', 'hero-cache_hi', 'hero-vrayProxy_hi', 'hero-vPrxoy_hi'], 
			'rig-rig_lo': ['hero-anim_lo'], 'rig-rigUV_lo': ['hero-anim_lo'], 'surface-shade_lo': ['hero-render_lo', 'hero-cahce_lo', 'vrayProxy_lo', 'hero-vPrxoy_lo']
			}

outputFileMap = {'hero-gpu': 'gpu', 'hero-ad': 'ad', 'hero-anim_md': 'anim', 'hero-render_md': 'render', 'hero-cache_md': 'cache', 'hero-vrayProxy_md': 'vrayProxy', 'hero-vPrxoy_md': 'vProxy', 'hero-geo': 'geo',
				'hero-anim_hi': 'anim', 'hero-render_hi': 'render', 'hero-cache_hi': 'cache', 'hero-vrayProxy_hi': 'vrayProxy', 'hero-vPrxoy_hi': 'vProxy', 
				'hero-anim_lo': 'anim', 'hero-render_lo': 'render', 'hero-cache_lo': 'cache', 'hero-vrayProxy_lo': 'vrayProxy', 'hero-vPrxoy_lo': 'vProxy'}


settingMap = {	1: {'statusMap': statusMap, 'outputMap': outputMap}, 
				2: {'statusMap': statusMap2, 'outputMap': outputMap2}
			}

projectSetting = {'all': 1, 
					'Lego_Frozen': 2}


steps = {
'anim': {'code': 'Animation', 'type': 'Step', 'id': 5, 'entity_type': 'Shot'}, 
'light': {'code': 'Lighting', 'type': 'Step', 'id': 7, 'entity_type': 'Shot'}, 
'comp': {'code': 'Compositing', 'type': 'Step', 'id': 8, 'entity_type': 'Shot'}, 
'art': {'code': 'Art', 'type': 'Step', 'id': 9, 'entity_type': 'Asset'}, 
'model': {'code': 'Model', 'type': 'Step', 'id': 10, 'entity_type': 'Asset'}, 
'rig': {'code': 'Rig', 'type': 'Step', 'id': 11, 'entity_type': 'Asset'}, 
'surface': {'code': 'Surface', 'type': 'Step', 'id': 12, 'entity_type': 'Asset'}, 
'lighting': {'code': 'lighting', 'type': 'Step', 'id': 44, 'entity_type': 'Asset'},
'layout': {'code': 'Layout', 'type': 'Step', 'id': 13, 'entity_type': 'Shot'}, 
# {'code': 'Layout', 'type': 'Step', 'id': 17, 'entity_type': 'Sequence'}, 
# {'code': 'Animation', 'type': 'Step', 'id': 18, 'entity_type': 'Sequence'}, 
'render': {'code': 'Render', 'type': 'Step', 'id': 43, 'entity_type': 'Shot'}, 
'uv': {'code': 'texture', 'type': 'Step', 'id': 49, 'entity_type': 'Asset'}, 
'animClean': {'code': 'TechAnim', 'type': 'Step', 'id': 54, 'entity_type': 'Shot'}, 
'fx': {'code': 'FX', 'type': 'Step', 'id': 55, 'entity_type': 'Shot'}, 
'setdress': {'code': 'SetDress', 'type': 'Step', 'id': 57, 'entity_type': 'Asset'}, 
'hero': {'code': 'Hero', 'type': 'Step', 'id': 70, 'entity_type': 'Asset'}
}

stepSgPipeMap = {
					5: 'anim',
					7: 'light',
					8: 'comp',
					9: 'art',
					10: 'model',
					11: 'rig',
					12: 'surface',
					13: 'layout',
					43: 'render',
					44: 'lighting',
					49: 'uv',
					54: 'animClean',
					55: 'fx',
					57: 'setdress',
					70: 'hero'
				}

checkExportSetting = {'hero-ad': ['prop', 'setDress', 'vehicle'], 'hero-gpu': ['prop', 'setDress', 'vehicle'], 'hero-geo': ['prop', 'setDress', 'vehicle']}

exportGrp = 'Geo_Grp'
rigGrp = 'Rig_Grp'
superRootCtrl = 'SuperRoot_Ctrl'
vrayProxyGrp = 'vproxy_grp'

rigCmd = {'importRef': 'rigCmd.importRef()', 'clean': 'rigCmd.clean()', 'tmpShd': 'rigCmd.assignTmpShd()', 'removeSet': 'rigCmd.removeSets()', 'removeRig': 'rigCmd.removeRig()',
			'keepVrayProxy': 'rigCmd.addRemoveVrayProxy(keep = True)', 'removeVrayProxy': 'rigCmd.addRemoveVrayProxy(keep = False)', 'vProxy': 'rigCmd.vProxy()', 'removeVrayNode': 'rigCmd.removeVrayNode()', 
			'combineGeo': 'rigCmd.combineGeo()', 'cleanAllSet': 'rigCmd.cleanAllSets()'}