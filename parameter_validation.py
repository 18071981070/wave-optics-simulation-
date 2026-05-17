class ParameterValidator:
    """
    参数验证模块
    确保输入参数符合物理规律和实验约束
    """
    
    # 参数范围定义
    PARAM_RANGES = {
        'wavelength': {'min': 380e-9, 'max': 780e-9, 'unit': 'm', 'name': '波长'},
        'slit_distance': {'min': 0.05e-3, 'max': 2e-3, 'unit': 'm', 'name': '缝距'},
        'slit_width': {'min': 0.01e-3, 'max': 1e-3, 'unit': 'm', 'name': '缝宽'},
        'screen_distance': {'min': 0.5, 'max': 10.0, 'unit': 'm', 'name': '屏距'},
        'refractive_index': {'min': 1.0, 'max': 2.5, 'unit': '', 'name': '折射率'},
        'polarization_angle': {'min': 0, 'max': 180, 'unit': 'deg', 'name': '偏振角'},
        'incident_angle': {'min': -45, 'max': 45, 'unit': 'deg', 'name': '入射角'},
        'coherence': {'min': 0, 'max': 1, 'unit': '', 'name': '相干性'},
        'film_thickness': {'min': 10e-9, 'max': 1000e-9, 'unit': 'm', 'name': '薄膜厚度'},
        'num_slits': {'min': 2, 'max': 100, 'unit': '', 'name': '缝数'},
        'grating_constant': {'min': 0.1e-6, 'max': 10e-6, 'unit': 'm', 'name': '光栅常数'}
    }
    
    @staticmethod
    def validate_parameter(param_name: str, value: float) -> tuple:
        """
        验证单个参数是否在有效范围内
        
        参数:
            param_name: 参数名称
            value: 参数值
        
        返回:
            (is_valid, message, corrected_value)
        """
        if param_name not in ParameterValidator.PARAM_RANGES:
            return True, f"参数 {param_name} 未定义验证规则，跳过验证", value
        
        range_info = ParameterValidator.PARAM_RANGES[param_name]
        min_val = range_info['min']
        max_val = range_info['max']
        name = range_info['name']
        unit = range_info['unit']
        
        if value < min_val:
            corrected = min_val
            return False, f"{name} ({value}{unit}) 低于最小值 ({min_val}{unit})，已修正为 {corrected}{unit}", corrected
        elif value > max_val:
            corrected = max_val
            return False, f"{name} ({value}{unit}) 超过最大值 ({max_val}{unit})，已修正为 {corrected}{unit}", corrected
        else:
            return True, f"{name} ({value}{unit}) 验证通过", value
    
    @staticmethod
    def validate_all(params: dict) -> tuple:
        """
        验证所有参数
        
        参数:
            params: 参数字典
        
        返回:
            (all_valid, messages, corrected_params)
        """
        all_valid = True
        messages = []
        corrected_params = params.copy()
        
        for param_name, value in params.items():
            if param_name in ParameterValidator.PARAM_RANGES:
                valid, msg, corrected = ParameterValidator.validate_parameter(param_name, value)
                if not valid:
                    all_valid = False
                    corrected_params[param_name] = corrected
                messages.append(msg)
        
        return all_valid, messages, corrected_params
    
    @staticmethod
    def validate_double_slit_params(wavelength, slit_distance, screen_distance, slit_width=None):
        """
        验证双缝干涉参数的合理性
        
        参数:
            wavelength: 波长
            slit_distance: 缝距
            screen_distance: 屏距
            slit_width: 缝宽
        
        返回:
            (is_valid, message)
        """
        messages = []
        
        # 验证缝距与波长的关系
        if slit_distance < wavelength * 10:
            messages.append(f"警告：缝距 ({slit_distance*1e3}mm) 应远大于波长 ({wavelength*1e9}nm)")
        
        # 验证屏距与缝距的关系
        if screen_distance < slit_distance * 100:
            messages.append(f"警告：屏距 ({screen_distance}m) 应远大于缝距 ({slit_distance*1e3}mm)")
        
        # 验证缝宽（如果提供）
        if slit_width is not None:
            if slit_width > slit_distance:
                messages.append(f"警告：缝宽 ({slit_width*1e3}mm) 不应大于缝距 ({slit_distance*1e3}mm)")
        
        if messages:
            return False, "\n".join(messages)
        return True, "参数验证通过"
    
    @staticmethod
    def validate_single_slit_params(wavelength, slit_width, screen_distance):
        """
        验证单缝衍射参数的合理性
        
        参数:
            wavelength: 波长
            slit_width: 缝宽
            screen_distance: 屏距
        
        返回:
            (is_valid, message)
        """
        messages = []
        
        # 验证缝宽与波长的关系
        if slit_width < wavelength:
            messages.append(f"警告：缝宽 ({slit_width*1e6}μm) 应大于波长 ({wavelength*1e9}nm)")
        
        if messages:
            return False, "\n".join(messages)
        return True, "参数验证通过"
    
    @staticmethod
    def validate_grating_params(wavelength, grating_constant, num_slits):
        """
        验证光栅参数的合理性
        
        参数:
            wavelength: 波长
            grating_constant: 光栅常数
            num_slits: 缝数
        
        返回:
            (is_valid, message)
        """
        messages = []
        
        # 验证光栅常数与波长的关系
        if grating_constant < wavelength:
            messages.append(f"警告：光栅常数 ({grating_constant*1e6}μm) 应大于波长 ({wavelength*1e9}nm)")
        
        # 验证缝数
        if num_slits < 2:
            messages.append("警告：光栅缝数应至少为2")
        
        if messages:
            return False, "\n".join(messages)
        return True, "参数验证通过"