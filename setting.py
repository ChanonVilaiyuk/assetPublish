''' shotgun '''

statusMap = {
			'model_md': ['uv_md', 'rig_md'], 'uv_md': ['shade_md'], 'rig_md': ['anim_md'], 'shade_md': ['render_md'], 
			'model_hi': ['uv_hi', 'rig_hi'], 'uv_hi': ['shade_hi'], 'rig_hi': ['anim_hi'], 'shade_hi': ['render_hi'], 
			'model_lo': ['uv_lo', 'rig_lo'], 'uv_lo': ['shade_lo'], 'rig_lo': ['anim_lo'], 'shade_lo': ['render_lo']
			}

statusMap2 = {
			'model_md': ['uv_md', 'rig_md'], 'uv_md': ['rigUv_md'], 'rig_md': ['shade_md', 'anim_md'], 'shade_md': ['render_md'], 
			'model_hi': ['uv_hi', 'rig_hi'], 'uv_hi': ['rigUv_hi'], 'rig_hi': ['shade_md', 'anim_hi'], 'shade_hi': ['render_hi'], 
			'model_lo': ['uv_lo', 'rig_lo'], 'uv_lo': ['rigUv_lo'], 'rig_lo': ['shade_md', 'anim_lo'], 'shade_lo': ['render_lo']
			}