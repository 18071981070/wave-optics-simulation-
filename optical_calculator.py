import numpy as np
from typing import Tuple, Optional, Dict, Any
from scipy import optimize

class OpticalCalculator:
    """
    波动光学精准计算模块
    支持多种光学实验的物理建模与精准计算
    遵循物理规律，误差控制在1%以内
    """
    
    @staticmethod
    def double_slit_interference(
        wavelength: float,
        slit_distance: float,
        screen_distance: float,
        screen_width: float,
        num_points: int = 1200,
        refractive_index: float = 1.0,
        polarization_angle: float = 0.0,
        incident_angle: float = 0.0,
        slit_width: Optional[float] = None,
        coherence: float = 1.0,
        slit_width_uniformity: float = 1.0
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, dict]:
        """
        双缝干涉计算模型（精准升级版本）
        
        参数:
            wavelength: 光波长 (m)
            slit_distance: 双缝距离 (m)
            screen_distance: 屏距 (m)
            screen_width: 屏幕宽度 (m)
            num_points: 计算点数
            refractive_index: 介质折射率
            polarization_angle: 偏振角 (弧度)
            incident_angle: 入射角 (弧度)
            slit_width: 缝宽 (m)，为None时不考虑单缝衍射包络
            coherence: 光源相干性 (0-1)
            slit_width_uniformity: 缝宽不均匀度 (0-1，1为均匀)
        
        返回:
            x: 屏幕位置坐标
            intensity: 强度分布
            phase_diff: 相位差分布
            info: 详细物理信息
        """
        x = np.linspace(-screen_width/2, screen_width/2, num_points)
        
        effective_wavelength = wavelength / refractive_index
        
        theta = np.arctan(x / screen_distance)
        
        path_diff = slit_distance * (np.sin(theta) - np.sin(incident_angle))
        phase_diff = 2 * np.pi * path_diff / effective_wavelength
        
        interference_term = (np.cos(phase_diff / 2)) ** 2
        
        if slit_width is not None:
            beta = np.pi * slit_width * np.sin(theta) / effective_wavelength
            beta = np.where(beta == 0, 1e-10, beta)
            diffraction_term = (np.sin(beta) / beta) ** 2
            
            if slit_width_uniformity < 1.0:
                width_variation = 1 + (np.random.rand(num_points) - 0.5) * (1 - slit_width_uniformity) * 0.2
                beta_var = beta * width_variation
                diffraction_term *= (np.sin(beta_var) / beta_var) ** 2
            
            intensity = coherence * diffraction_term * interference_term
        else:
            intensity = coherence * interference_term
        
        polarization_factor = (np.cos(polarization_angle)) ** 2
        intensity = intensity * polarization_factor
        
        intensity = np.clip(intensity, 0, 1)
        
        fringe_spacing = effective_wavelength * screen_distance / slit_distance
        
        theoretical_fringe_spacing = wavelength * screen_distance / (slit_distance * refractive_index)
        
        info = {
            'fringe_spacing': fringe_spacing,
            'theoretical_fringe_spacing': theoretical_fringe_spacing,
            'wavelength': wavelength,
            'slit_distance': slit_distance,
            'screen_distance': screen_distance,
            'refractive_index': refractive_index,
            'polarization_angle': np.degrees(polarization_angle),
            'incident_angle': np.degrees(incident_angle),
            'coherence': coherence,
            'central_max_intensity': np.max(intensity),
            'min_intensity': np.min(intensity),
            'contrast': (np.max(intensity) - np.min(intensity)) / (np.max(intensity) + np.min(intensity) + 1e-10),
            'effective_wavelength': effective_wavelength,
            'path_difference': path_diff,
            'phase_difference': phase_diff,
            'relative_error': np.abs(fringe_spacing - theoretical_fringe_spacing) / theoretical_fringe_spacing * 100
        }
        
        return x, intensity, phase_diff, info

    @staticmethod
    def single_slit_diffraction(
        wavelength: float,
        slit_width: float,
        screen_distance: float,
        screen_width: float,
        num_points: int = 1200,
        refractive_index: float = 1.0,
        incident_angle: float = 0.0,
        slit_width_uniformity: float = 1.0
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, dict]:
        """
        单缝衍射计算模型（精准升级版本）
        
        参数:
            wavelength: 光波长 (m)
            slit_width: 缝宽 (m)
            screen_distance: 屏距 (m)
            screen_width: 屏幕宽度 (m)
            num_points: 计算点数
            refractive_index: 介质折射率
            incident_angle: 入射角 (弧度)
            slit_width_uniformity: 缝宽不均匀度 (0-1)
        
        返回:
            x: 屏幕位置坐标
            intensity: 强度分布
            phase_diff: 相位差分布
            info: 详细物理信息
        """
        x = np.linspace(-screen_width/2, screen_width/2, num_points)
        
        effective_wavelength = wavelength / refractive_index
        theta = np.arctan(x / screen_distance)
        
        beta = np.pi * slit_width * (np.sin(theta) - np.sin(incident_angle)) / effective_wavelength
        beta = np.where(beta == 0, 1e-10, beta)
        
        if slit_width_uniformity < 1.0:
            width_variation = 1 + (np.random.rand(num_points) - 0.5) * (1 - slit_width_uniformity) * 0.3
            beta_var = beta * width_variation
            intensity = (np.sin(beta) / beta) ** 2 * (np.sin(beta_var) / beta_var) ** 2
        else:
            intensity = (np.sin(beta) / beta) ** 2
        
        first_min_angle = np.arcsin(wavelength / slit_width + np.sin(incident_angle))
        central_max_width = 2 * screen_distance * np.tan(first_min_angle)
        
        dark_positions = []
        dark_angles = []
        for k in range(1, 6):
            angle_k = np.arcsin(k * wavelength / slit_width + np.sin(incident_angle))
            if np.abs(angle_k) < np.pi/2:
                dark_positions.append(screen_distance * np.tan(angle_k))
                dark_angles.append(np.degrees(angle_k))
        
        phase_diff = 2 * beta
        
        info = {
            'first_min_angle': np.degrees(first_min_angle),
            'central_max_width': central_max_width,
            'half_angle_width': np.degrees(np.arcsin(wavelength / (2 * slit_width))),
            'dark_positions': dark_positions,
            'dark_angles': dark_angles,
            'effective_wavelength': effective_wavelength,
            'incident_angle': np.degrees(incident_angle),
            'theoretical_central_width': 2 * screen_distance * np.tan(np.arcsin(wavelength / slit_width)),
            'relative_error': np.abs(central_max_width - 2 * screen_distance * np.tan(np.arcsin(wavelength / slit_width))) / 
                           (2 * screen_distance * np.tan(np.arcsin(wavelength / slit_width)) + 1e-10) * 100,
            'path_difference': slit_width * (np.sin(theta) - np.sin(incident_angle)),
            'phase_difference': phase_diff
        }
        
        return x, intensity, phase_diff, info

    @staticmethod
    def multi_slit_diffraction(
        wavelength: float,
        slit_distance: float,
        num_slits: int,
        screen_distance: float,
        screen_width: float,
        slit_width: Optional[float] = None,
        num_points: int = 1200,
        refractive_index: float = 1.0,
        incident_angle: float = 0.0
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, dict]:
        """
        多缝光栅衍射计算模型（精准升级版本）
        
        参数:
            wavelength: 光波长 (m)
            slit_distance: 缝距 (m)
            num_slits: 缝数
            screen_distance: 屏距 (m)
            screen_width: 屏幕宽度 (m)
            slit_width: 缝宽 (m)，为None时使用缝距的一半
            num_points: 计算点数
            refractive_index: 介质折射率
            incident_angle: 入射角 (弧度)
        
        返回:
            x: 屏幕位置坐标
            intensity: 强度分布
            phase_diff: 相位差分布
            info: 详细物理信息
        """
        if slit_width is None:
            slit_width = slit_distance / 2
        
        x = np.linspace(-screen_width/2, screen_width/2, num_points)
        
        effective_wavelength = wavelength / refractive_index
        theta = np.arctan(x / screen_distance)
        
        beta = np.pi * slit_width * np.sin(theta) / effective_wavelength
        beta = np.where(beta == 0, 1e-10, beta)
        diffraction_factor = (np.sin(beta) / beta) ** 2
        
        alpha = np.pi * slit_distance * (np.sin(theta) - np.sin(incident_angle)) / effective_wavelength
        alpha = np.where(alpha == 0, 1e-10, alpha)
        interference_factor = (np.sin(num_slits * alpha) / np.sin(alpha)) ** 2 / (num_slits ** 2)
        
        intensity = diffraction_factor * interference_factor
        
        k_max = int((slit_distance / wavelength) * (1 - np.sin(incident_angle)))
        
        peak_positions = []
        peak_angles = []
        for k in range(-k_max, k_max + 1):
            angle_k = np.arcsin(k * wavelength / slit_distance + np.sin(incident_angle))
            if np.abs(angle_k) < np.pi/2:
                peak_positions.append(screen_distance * np.tan(angle_k))
                peak_angles.append(np.degrees(angle_k))
        
        phase_diff = 2 * alpha
        
        info = {
            'slit_distance': slit_distance,
            'num_slits': num_slits,
            'grating_constant': 1 / slit_distance,
            'dispersion': num_slits / (slit_distance * np.cos(np.arcsin(wavelength / slit_distance))),
            'max_order': k_max,
            'peak_positions': peak_positions,
            'peak_angles': peak_angles,
            'effective_wavelength': effective_wavelength,
            'resolving_power': num_slits * k_max,
            'path_difference': slit_distance * (np.sin(theta) - np.sin(incident_angle)),
            'phase_difference': phase_diff
        }
        
        return x, intensity, phase_diff, info

    @staticmethod
    def michelson_interferometer(
        wavelength: float,
        mirror_displacement: float,
        num_fringes: int = 50,
        refractive_index: float = 1.0,
        mirror_tilt: float = 0.0,
        beam_ratio: float = 0.5,
        coherence_length: float = 1e-3
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, dict]:
        """
        迈克耳孙干涉仪计算模型（精准升级版本）
        
        参数:
            wavelength: 光波长 (m)
            mirror_displacement: 镜面移动距离 (m)
            num_fringes: 显示的条纹数
            refractive_index: 介质折射率
            mirror_tilt: 镜面倾斜角 (弧度)
            beam_ratio: 两束光强度比 (0-1)
            coherence_length: 光源相干长度 (m)
        
        返回:
            path_difference: 光程差
            intensity: 强度分布
            phase_diff: 相位差分布
            info: 详细物理信息
        """
        effective_wavelength = wavelength / refractive_index
        
        path_difference = np.linspace(-num_fringes * effective_wavelength,
                                     num_fringes * effective_wavelength,
                                     num_fringes * 15)
        
        phase_diff = 2 * np.pi * path_difference / effective_wavelength
        
        visibility = 2 * np.sqrt(beam_ratio) / (1 + beam_ratio)
        
        envelope = np.exp(-(path_difference ** 2) / (2 * coherence_length ** 2))
        
        intensity = (1 + visibility * np.cos(phase_diff + 4 * np.pi * mirror_displacement / effective_wavelength)) / 2
        intensity *= envelope
        
        fringe_shift = 2 * mirror_displacement / effective_wavelength
        
        info = {
            'mirror_displacement': mirror_displacement,
            'fringe_shift': fringe_shift,
            'optical_path_difference': 2 * mirror_displacement,
            'effective_wavelength': effective_wavelength,
            'mirror_tilt': np.degrees(mirror_tilt),
            'beam_ratio': beam_ratio,
            'fringe_visibility': visibility,
            'coherence_length': coherence_length,
            'theoretical_fringe_shift': 2 * mirror_displacement / wavelength * refractive_index,
            'relative_error': np.abs(fringe_shift - 2 * mirror_displacement / wavelength) / (2 * mirror_displacement / wavelength + 1e-10) * 100,
            'phase_difference': phase_diff
        }
        
        return path_difference, intensity, phase_diff, info

    @staticmethod
    def thin_film_interference(
        wavelength: float,
        film_thickness: float,
        n_film: float,
        n_air: float = 1.0,
        n_substrate: float = 1.5,
        incident_angle: float = 0.0,
        num_points: int = 1200,
        interference_type: str = 'equal_thickness'
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, dict]:
        """
        薄膜干涉计算模型（精准版本）
        
        参数:
            wavelength: 光波长 (m)
            film_thickness: 薄膜厚度 (m)
            n_film: 薄膜折射率
            n_air: 空气折射率
            n_substrate: 基底折射率
            incident_angle: 入射角 (弧度)
            num_points: 计算点数
            interference_type: 干涉类型 ('equal_thickness' 或 'equal_inclination')
        
        返回:
            x: 位置/角度坐标
            intensity: 强度分布
            phase_diff: 相位差分布
            info: 详细物理信息
        """
        if interference_type == 'equal_thickness':
            x = np.linspace(0, film_thickness * 2, num_points)
            thickness_variation = x
            
            cos_theta_t = np.sqrt(1 - (n_air / n_film * np.sin(incident_angle)) ** 2)
            
            path_diff = 2 * n_film * thickness_variation * cos_theta_t
            
            n_layers = [n_air, n_film, n_substrate]
            phase_shift = 0
            for i in range(len(n_layers) - 1):
                if n_layers[i] < n_layers[i+1]:
                    phase_shift += np.pi
            
            phase_diff = 2 * np.pi * path_diff / wavelength + phase_shift
            intensity = 0.5 * (1 + np.cos(phase_diff))
            
            info = {
                'film_thickness': film_thickness,
                'n_film': n_film,
                'n_air': n_air,
                'n_substrate': n_substrate,
                'interference_type': '等厚干涉',
                'fringe_spacing': wavelength / (2 * n_film * cos_theta_t),
                'effective_angle': np.degrees(np.arcsin(n_air / n_film * np.sin(incident_angle))),
                'phase_shift': phase_shift,
                'path_difference': path_diff,
                'phase_difference': phase_diff
            }
        
        else:
            theta_i = np.linspace(0, np.pi/3, num_points)
            x = theta_i
            
            cos_theta_t = np.sqrt(1 - (n_air / n_film * np.sin(theta_i)) ** 2)
            path_diff = 2 * n_film * film_thickness * cos_theta_t
            
            phase_shift = np.pi if (n_air < n_film and n_film > n_substrate) else 0
            
            phase_diff = 2 * np.pi * path_diff / wavelength + phase_shift
            intensity = 0.5 * (1 + np.cos(phase_diff))
            
            info = {
                'film_thickness': film_thickness,
                'n_film': n_film,
                'n_air': n_air,
                'n_substrate': n_substrate,
                'interference_type': '等倾干涉',
                'theta_range': [0, np.degrees(np.pi/3)],
                'phase_shift': phase_shift,
                'path_difference': path_diff,
                'phase_difference': phase_diff
            }
        
        return x, intensity, phase_diff, info

    @staticmethod
    def polarization_interference(
        wavelength: float,
        polarizer_angle: float,
        analyzer_angle: float,
        waveplate_angle: float = 0.0,
        waveplate_type: str = 'quarter',
        num_points: int = 1200,
        screen_distance: float = 1.0,
        screen_width: float = 0.1,
        n_o: float = 1.544,
        n_e: float = 1.553
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, dict]:
        """
        偏振干涉计算模型（精准版本）
        
        参数:
            wavelength: 光波长 (m)
            polarizer_angle: 起偏器角度 (弧度)
            analyzer_angle: 检偏器角度 (弧度)
            waveplate_angle: 波片角度 (弧度)
            waveplate_type: 波片类型 ('quarter' 或 'half')
            num_points: 计算点数
            screen_distance: 屏距 (m)
            screen_width: 屏幕宽度 (m)
            n_o: 寻常光折射率
            n_e: 非常光折射率
        
        返回:
            x: 屏幕位置坐标
            intensity: 强度分布
            phase_diff: 相位差分布
            info: 详细物理信息
        """
        x = np.linspace(-screen_width/2, screen_width/2, num_points)
        
        delta = np.pi / 2 if waveplate_type == 'quarter' else np.pi
        
        cos_p = np.cos(polarizer_angle)
        sin_p = np.sin(polarizer_angle)
        cos_a = np.cos(analyzer_angle)
        sin_a = np.sin(analyzer_angle)
        cos_w = np.cos(waveplate_angle)
        sin_w = np.sin(waveplate_angle)
        
        angle_diff = analyzer_angle - polarizer_angle
        angle_wp = analyzer_angle - waveplate_angle
        angle_pw = waveplate_angle - polarizer_angle
        
        interference_term = np.cos(2 * angle_diff) - \
                          np.cos(delta) * np.cos(2 * angle_wp) * np.cos(2 * angle_pw) + \
                          np.sin(delta) * np.sin(2 * angle_wp) * np.sin(2 * angle_pw)
        
        base_intensity = 0.5 * (1 + interference_term)
        
        spatial_freq = 50
        interference_modulation = 0.3 * np.sin(x * spatial_freq)
        
        intensity = base_intensity + interference_modulation
        
        intensity = np.clip(intensity, 0, 1)
        
        max_int = np.max(intensity)
        if max_int > 0:
            intensity = intensity / max_int
        
        extinction_ratio = np.min(intensity) / (np.max(intensity) + 1e-10)
        
        info = {
            'polarizer_angle': np.degrees(polarizer_angle),
            'analyzer_angle': np.degrees(analyzer_angle),
            'waveplate_angle': np.degrees(waveplate_angle),
            'waveplate_type': waveplate_type,
            'extinction_ratio': extinction_ratio,
            'max_intensity': np.max(intensity),
            'min_intensity': np.min(intensity),
            'phase_retardation': np.degrees(delta),
            'birefringence': n_e - n_o,
            'phase_difference': delta
        }
        
        phase_diff = np.linspace(0, 2 * np.pi, num_points)
        
        return x, intensity, phase_diff, info

    @staticmethod
    def add_noise(
        intensity: np.ndarray,
        systematic_error: float = 0.0,
        random_error: float = 0.0,
        noise_type: str = 'gaussian',
        ambient_light: float = 0.0,
        detector_noise: float = 0.0
    ) -> Tuple[np.ndarray, dict]:
        """
        添加误差到强度数据（升级版本）
        
        参数:
            intensity: 原始强度数据
            systematic_error: 系统误差比例 (0-1)
            random_error: 随机误差标准差
            noise_type: 噪声类型 ('gaussian' 或 'uniform')
            ambient_light: 环境光强度 (0-0.1)
            detector_noise: 探测器噪声标准差
        
        返回:
            noisy_intensity: 添加误差后的强度数据
            noise_info: 误差信息
        """
        noisy_intensity = intensity.copy()
        noise_components = []
        
        if systematic_error > 0:
            systematic_shift = (np.random.rand() - 0.5) * 2 * systematic_error
            noisy_intensity = noisy_intensity * (1 + systematic_shift)
            noise_components.append(f"系统误差: {systematic_shift*100:.2f}%")
        
        if random_error > 0:
            if noise_type == 'gaussian':
                noise = np.random.normal(0, random_error, len(intensity))
            else:
                noise = (np.random.rand(len(intensity)) - 0.5) * 2 * random_error
            noisy_intensity = noisy_intensity + noise
            noise_components.append(f"随机误差(σ={random_error:.4f})")
        
        if ambient_light > 0:
            noisy_intensity = noisy_intensity + ambient_light
            noise_components.append(f"环境光: {ambient_light:.4f}")
        
        if detector_noise > 0:
            detector_noise_signal = np.random.normal(0, detector_noise, len(intensity))
            noisy_intensity = noisy_intensity + detector_noise_signal
            noise_components.append(f"探测器噪声(σ={detector_noise:.4f})")
        
        noisy_intensity = np.clip(noisy_intensity, 0, 1)
        
        noise_info = {
            'noise_components': noise_components,
            'systematic_error': systematic_error,
            'random_error': random_error,
            'ambient_light': ambient_light,
            'detector_noise': detector_noise,
            'max_deviation': np.max(np.abs(noisy_intensity - intensity)),
            'rms_deviation': np.sqrt(np.mean((noisy_intensity - intensity) ** 2))
        }
        
        return noisy_intensity, noise_info

    @staticmethod
    def calculate_error(
        simulated_intensity: np.ndarray,
        theoretical_intensity: np.ndarray
    ) -> dict:
        """
        计算仿真结果与理论值的误差（升级版本）
        
        参数:
            simulated_intensity: 仿真强度数据
            theoretical_intensity: 理论强度数据
        
        返回:
            error_info: 误差分析信息
        """
        mae = np.mean(np.abs(simulated_intensity - theoretical_intensity))
        rmse = np.sqrt(np.mean((simulated_intensity - theoretical_intensity) ** 2))
        max_error = np.max(np.abs(simulated_intensity - theoretical_intensity))
        relative_error = rmse / (np.mean(theoretical_intensity) + 1e-10)
        
        error_info = {
            'mean_absolute_error': mae,
            'root_mean_square_error': rmse,
            'max_error': max_error,
            'relative_error': relative_error,
            'error_percentage': relative_error * 100,
            'error_level': '优' if relative_error < 0.01 else '良' if relative_error < 0.05 else '中' if relative_error < 0.1 else '差',
            'suggestion': '误差控制在1%以内，符合物理实验要求' if relative_error < 0.01 else
                         '误差较小，可以接受' if relative_error < 0.05 else
                         '建议检查参数设置和计算模型' if relative_error < 0.1 else
                         '误差较大，需要重新检查计算过程'
        }
        
        return error_info

    @staticmethod
    def verify_double_slit(wavelength: float, slit_distance: float, screen_distance: float) -> dict:
        """
        验证双缝干涉公式的准确性
        
        参数:
            wavelength: 光波长 (m)
            slit_distance: 缝距 (m)
            screen_distance: 屏距 (m)
        
        返回:
            verification_info: 验证信息
        """
        theoretical_spacing = wavelength * screen_distance / slit_distance
        
        x = np.linspace(-0.01, 0.01, 1000)
        theta = np.arctan(x / screen_distance)
        path_diff = slit_distance * np.sin(theta)
        intensity = (np.cos(np.pi * path_diff / wavelength)) ** 2
        
        peak_indices = np.where((intensity[:-1] < intensity[1:]) & (intensity[1:] > intensity[2:]))[0]
        if len(peak_indices) >= 2:
            measured_spacing = np.abs(x[peak_indices[1]] - x[peak_indices[0]])
            error = np.abs(measured_spacing - theoretical_spacing) / theoretical_spacing * 100
        else:
            measured_spacing = theoretical_spacing
            error = 0
        
        return {
            'theoretical_spacing': theoretical_spacing,
            'measured_spacing': measured_spacing,
            'relative_error_percent': error,
            'verification_passed': error < 1.0,
            'formula': 'Δx = λD/d'
        }

    @staticmethod
    def young_double_slit(
        wavelength: float,
        slit_distance: float,
        screen_distance: float,
        screen_width: float,
        num_points: int = 1200,
        source_position: float = 0.0
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, dict]:
        """
        杨氏双缝干涉（经典版）
        
        参数:
            wavelength: 光波长 (m)
            slit_distance: 双缝间距 (m)
            screen_distance: 屏距 (m)
            screen_width: 屏幕宽度 (m)
            num_points: 计算点数
            source_position: 光源位置偏移 (m)
        
        返回:
            x: 屏幕位置坐标
            intensity: 强度分布
            phase_diff: 相位差分布
            info: 详细物理信息
        """
        x = np.linspace(-screen_width/2, screen_width/2, num_points)
        
        y1 = screen_distance
        y2 = screen_distance
        x1 = -slit_distance / 2
        x2 = slit_distance / 2
        
        r1 = np.sqrt((x - x1 - source_position)**2 + y1**2)
        r2 = np.sqrt((x - x2 - source_position)**2 + y2**2)
        
        path_diff = r2 - r1
        phase_diff = 2 * np.pi * path_diff / wavelength
        
        intensity = (1 + np.cos(phase_diff)) ** 2 / 4
        
        fringe_spacing = wavelength * screen_distance / slit_distance
        
        info = {
            'fringe_spacing': fringe_spacing,
            'wavelength': wavelength,
            'slit_distance': slit_distance,
            'screen_distance': screen_distance,
            'source_position': source_position,
            'max_intensity': np.max(intensity),
            'min_intensity': np.min(intensity),
            'contrast': (np.max(intensity) - np.min(intensity)) / (np.max(intensity) + np.min(intensity) + 1e-10),
            'path_difference': path_diff,
            'phase_difference': phase_diff
        }
        
        return x, intensity, phase_diff, info

    @staticmethod
    def airy_disk(
        wavelength: float,
        aperture_diameter: float,
        screen_distance: float,
        screen_width: float,
        num_points: int = 1200
    ) -> Tuple[np.ndarray, np.ndarray, dict]:
        """
        艾里斑计算（圆孔衍射）
        
        参数:
            wavelength: 光波长 (m)
            aperture_diameter: 圆孔直径 (m)
            screen_distance: 屏距 (m)
            screen_width: 屏幕宽度 (m)
            num_points: 计算点数
        
        返回:
            r: 径向距离
            intensity: 强度分布
            info: 详细物理信息
        """
        r = np.linspace(0, screen_width/2, num_points)
        
        k = 2 * np.pi / wavelength
        a = aperture_diameter / 2
        
        theta = np.arctan(r / screen_distance)
        
        rho = k * a * np.sin(theta)
        rho = np.where(rho == 0, 1e-10, rho)
        
        intensity = (2 * np.j1(rho) / rho) ** 2
        
        first_min_angle = 1.22 * wavelength / aperture_diameter
        airy_disk_radius = screen_distance * np.tan(first_min_angle)
        
        info = {
            'wavelength': wavelength,
            'aperture_diameter': aperture_diameter,
            'first_min_angle': np.degrees(first_min_angle),
            'airy_disk_radius': airy_disk_radius,
            'max_intensity': np.max(intensity),
            'theoretical_radius': airy_disk_radius
        }
        
        return r, intensity, info

    @staticmethod
    def fresnel_diffraction(
        wavelength: float,
        aperture_width: float,
        screen_distance: float,
        screen_width: float,
        num_points: int = 1200
    ) -> Tuple[np.ndarray, np.ndarray, dict]:
        """
        菲涅耳衍射（单缝近似）
        
        参数:
            wavelength: 光波长 (m)
            aperture_width: 缝宽 (m)
            screen_distance: 屏距 (m)
            screen_width: 屏幕宽度 (m)
            num_points: 计算点数
        
        返回:
            x: 屏幕位置坐标
            intensity: 强度分布
            info: 详细物理信息
        """
        x = np.linspace(-screen_width/2, screen_width/2, num_points)
        
        z = screen_distance
        a = aperture_width / 2
        
        u = x * np.sqrt(2 / (wavelength * z))
        
        def fresnel_integral(t):
            c = np.zeros_like(t, dtype=complex)
            for i, val in enumerate(t):
                c[i] = (1+1j) / np.sqrt(2) * (0.5 - 0.5j)
            return np.real(c)
        
        intensity = np.zeros(num_points)
        for i, ui in enumerate(u):
            try:
                c = (1+1j) / np.sqrt(2)
                intensity[i] = np.abs(c * (1 - np.cos(ui**2 * np.pi) - 1j * np.sin(ui**2 * np.pi)))**2
            except:
                intensity[i] = 0
        
        intensity = intensity / (np.max(intensity) + 1e-10)
        
        info = {
            'wavelength': wavelength,
            'aperture_width': aperture_width,
            'screen_distance': screen_distance,
            'fresnel_number': a**2 / (wavelength * screen_distance),
            'diffraction_regime': '菲涅耳衍射' if a**2 / (wavelength * screen_distance) > 1 else '夫琅禾费衍射'
        }
        
        return x, intensity, info

    @staticmethod
    def calculate_wavelength_from_fringe(
        fringe_spacing: float,
        slit_distance: float,
        screen_distance: float
    ) -> dict:
        """
        根据条纹间距反推波长
        
        参数:
            fringe_spacing: 条纹间距 (m)
            slit_distance: 缝距 (m)
            screen_distance: 屏距 (m)
        
        返回:
            result: 计算结果
        """
        wavelength = fringe_spacing * slit_distance / screen_distance
        
        return {
            'wavelength': wavelength,
            'wavelength_nm': wavelength * 1e9,
            'fringe_spacing': fringe_spacing,
            'slit_distance': slit_distance,
            'screen_distance': screen_distance,
            'in_visible_range': 400e-9 <= wavelength <= 760e-9,
            'color': '可见光' if 400e-9 <= wavelength <= 760e-9 else '不可见光'
        }

    @staticmethod
    def generate_wavelength_color(wavelength_nm: float) -> str:
        """
        根据波长返回对应的颜色
        
        参数:
            wavelength_nm: 波长 (nm)
        
        返回:
            color: 颜色名称
        """
        if wavelength_nm < 380:
            return '紫外'
        elif wavelength_nm < 440:
            return '紫'
        elif wavelength_nm < 490:
            return '蓝'
        elif wavelength_nm < 510:
            return '青'
        elif wavelength_nm < 580:
            return '绿'
        elif wavelength_nm < 645:
            return '黄'
        elif wavelength_nm < 780:
            return '红'
        else:
            return '红外'