import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.font_manager import fontManager
import os

font_path = os.path.join(os.path.dirname(__file__), 'simhei.ttf')
if os.path.exists(font_path):
    fontManager.addfont(font_path)
    matplotlib.rcParams['font.sans-serif'] = ['SimHei']
else:
    matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
matplotlib.rcParams['axes.unicode_minus'] = False

class WaveOpticsVisualizer:
    """
    波动光学可视化模块
    提供各种光学现象的绘图功能
    """
    
    @staticmethod
    def plot_intensity_2d(x, intensity, title='光强分布', xlabel='位置 (mm)', ylabel='相对强度', 
                          color_scheme='viridis', show_grid=True, figsize=(12, 6)):
        """
        绘制2D光强分布图
        
        参数:
            x: 位置坐标
            intensity: 强度分布
            title: 图表标题
            xlabel: x轴标签
            ylabel: y轴标签
            color_scheme: 配色方案
            show_grid: 是否显示网格
            figsize: 图大小
        """
        fig, ax = plt.subplots(figsize=figsize)
        ax.fill_between(x * 1000, intensity, alpha=0.4)
        ax.plot(x * 1000, intensity, linewidth=2, color='#1565c0')
        ax.set_xlabel(xlabel, fontsize=11, fontweight='bold')
        ax.set_ylabel(ylabel, fontsize=11, fontweight='bold')
        ax.set_title(title, fontsize=13, fontweight='bold')
        if show_grid:
            ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_ylim(0, 1.1)
        
        return fig
    
    @staticmethod
    def plot_intensity_image(x, intensity, title='强度分布图', xlabel='位置 (mm)', 
                             color_scheme='viridis', figsize=(12, 4)):
        """
        绘制强度分布图像
        
        参数:
            x: 位置坐标
            intensity: 强度分布
            title: 图表标题
            xlabel: x轴标签
            color_scheme: 配色方案
            figsize: 图大小
        """
        fig, ax = plt.subplots(figsize=figsize)
        y_img = np.linspace(0, 1, 150)
        Z = np.tile(intensity, (150, 1))
        im = ax.imshow(Z, extent=[x[0]*1000, x[-1]*1000, 0, 1], 
                       aspect='auto', cmap=color_scheme, interpolation='bilinear')
        ax.set_xlabel(xlabel, fontsize=11, fontweight='bold')
        ax.set_ylabel('强度分布', fontsize=11, fontweight='bold')
        ax.set_title(title, fontsize=13, fontweight='bold')
        cbar = plt.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label('强度', fontsize=10)
        
        return fig
    
    @staticmethod
    def plot_3d_surface(x, intensity, title='3D强度分布', color_scheme='viridis', figsize=(14, 10)):
        """
        绘制3D强度分布图
        
        参数:
            x: 位置坐标
            intensity: 强度分布
            title: 图表标题
            color_scheme: 配色方案
            figsize: 图大小
        """
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111, projection='3d')
        
        x_3d = x * 1000
        y_3d = np.linspace(-5, 5, 30)
        X_3d, Y_3d = np.meshgrid(x_3d, y_3d)
        Z_3d = np.tile(intensity, (30, 1))
        
        surf = ax.plot_surface(X_3d, Y_3d, Z_3d, cmap=color_scheme,
                               edgecolor='none', alpha=0.9,
                               rstride=8, cstride=1, antialiased=False)
        
        ax.view_init(elev=30, azim=60)
        ax.set_xlabel('位置 (mm)', fontsize=12, fontweight='bold', labelpad=8)
        ax.set_ylabel('Y方向 (mm)', fontsize=12, fontweight='bold', labelpad=8)
        ax.set_zlabel('相对强度', fontsize=12, fontweight='bold', labelpad=8)
        ax.set_zlim(0, 1.1)
        ax.set_title(title, fontsize=13, fontweight='bold')
        
        cbar = fig.colorbar(surf, ax=ax, shrink=0.6, aspect=15, pad=0.1)
        cbar.set_label('相对强度', fontsize=11)
        
        return fig
    
    @staticmethod
    def plot_phase_difference(x, phase_diff, title='相位差分布', figsize=(12, 4)):
        """
        绘制相位差分布图
        
        参数:
            x: 位置坐标
            phase_diff: 相位差分布
            title: 图表标题
            figsize: 图大小
        """
        fig, ax = plt.subplots(figsize=figsize)
        ax.plot(x * 1000, phase_diff, linewidth=2, color='#d32f2f')
        ax.set_xlabel('位置 (mm)', fontsize=11, fontweight='bold')
        ax.set_ylabel('相位差 (rad)', fontsize=11, fontweight='bold')
        ax.set_title(title, fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle='--')
        
        return fig
    
    @staticmethod
    def plot_multi_panel(x, intensity, phase_diff=None, show_phase=True, 
                         title1='光强分布', title2='强度图像', title3='相位差分布',
                         color_scheme='viridis', figsize=(12, 9)):
        """
        绘制多面板组合图
        
        参数:
            x: 位置坐标
            intensity: 强度分布
            phase_diff: 相位差分布
            show_phase: 是否显示相位图
            title1: 光强曲线图标题
            title2: 强度图像标题
            title3: 相位图标题
            color_scheme: 配色方案
            figsize: 图大小
        """
        fig = plt.figure(figsize=figsize)
        
        if show_phase and phase_diff is not None:
            ax1 = fig.add_subplot(3, 1, 1)
            ax1.fill_between(x * 1000, intensity, alpha=0.4)
            ax1.plot(x * 1000, intensity, linewidth=2, color='#1565c0')
            ax1.set_xlabel('位置 (mm)', fontsize=11, fontweight='bold')
            ax1.set_ylabel('相对强度', fontsize=11, fontweight='bold')
            ax1.set_title(title1, fontsize=12, fontweight='bold')
            ax1.grid(True, alpha=0.3, linestyle='--')
            ax1.set_ylim(0, 1.1)
            
            ax2 = fig.add_subplot(3, 1, 2)
            ax2.plot(x * 1000, phase_diff, linewidth=2, color='#d32f2f')
            ax2.set_xlabel('位置 (mm)', fontsize=11, fontweight='bold')
            ax2.set_ylabel('相位差 (rad)', fontsize=11, fontweight='bold')
            ax2.set_title(title3, fontsize=12, fontweight='bold')
            ax2.grid(True, alpha=0.3, linestyle='--')
            
            ax3 = fig.add_subplot(3, 1, 3)
            y_img = np.linspace(0, 1, 150)
            Z = np.tile(intensity, (150, 1))
            im = ax3.imshow(Z, extent=[x[0]*1000, x[-1]*1000, 0, 1], 
                           aspect='auto', cmap=color_scheme, interpolation='bilinear')
            ax3.set_xlabel('位置 (mm)', fontsize=11, fontweight='bold')
            ax3.set_ylabel('强度分布', fontsize=11, fontweight='bold')
            ax3.set_title(title2, fontsize=12, fontweight='bold')
            cbar = plt.colorbar(im, ax=ax3, shrink=0.8)
            cbar.set_label('强度', fontsize=10)
        else:
            ax1 = fig.add_subplot(2, 1, 1)
            ax1.fill_between(x * 1000, intensity, alpha=0.4)
            ax1.plot(x * 1000, intensity, linewidth=2, color='#1565c0')
            ax1.set_xlabel('位置 (mm)', fontsize=11, fontweight='bold')
            ax1.set_ylabel('相对强度', fontsize=11, fontweight='bold')
            ax1.set_title(title1, fontsize=12, fontweight='bold')
            ax1.grid(True, alpha=0.3, linestyle='--')
            ax1.set_ylim(0, 1.1)
            
            ax2 = fig.add_subplot(2, 1, 2)
            y_img = np.linspace(0, 1, 150)
            Z = np.tile(intensity, (150, 1))
            im = ax2.imshow(Z, extent=[x[0]*1000, x[-1]*1000, 0, 1], 
                           aspect='auto', cmap=color_scheme, interpolation='bilinear')
            ax2.set_xlabel('位置 (mm)', fontsize=11, fontweight='bold')
            ax2.set_ylabel('强度分布', fontsize=11, fontweight='bold')
            ax2.set_title(title2, fontsize=12, fontweight='bold')
            cbar = plt.colorbar(im, ax=ax2, shrink=0.8)
            cbar.set_label('强度', fontsize=10)
        
        plt.tight_layout(pad=1.5)
        return fig
    
    @staticmethod
    def plot_comparison(x, intensity1, intensity2, label1='理论值', label2='仿真值',
                        title='理论与仿真对比', figsize=(12, 6)):
        """
        绘制理论值与仿真值的对比图
        
        参数:
            x: 位置坐标
            intensity1: 第一组强度数据
            intensity2: 第二组强度数据
            label1: 第一组数据标签
            label2: 第二组数据标签
            title: 图表标题
            figsize: 图大小
        """
        fig, ax = plt.subplots(figsize=figsize)
        ax.plot(x * 1000, intensity1, linewidth=2, label=label1, color='#1565c0')
        ax.plot(x * 1000, intensity2, linewidth=2, label=label2, color='#d32f2f', linestyle='--')
        ax.set_xlabel('位置 (mm)', fontsize=11, fontweight='bold')
        ax.set_ylabel('相对强度', fontsize=11, fontweight='bold')
        ax.set_title(title, fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.legend(fontsize=11)
        ax.set_ylim(0, 1.1)
        
        return fig