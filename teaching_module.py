class TeachingModule:
    """
    教学模块
    提供波动光学实验的教学指导和学习资源
    """
    
    EXPERIMENT_INFO = {
        "双缝干涉": {
            "principle": """
            **双缝干涉原理**
            
            双缝干涉是波动光学的经典实验，证明了光的波动性。
            
            **核心公式：**
            - 光程差：Δ = d·sinθ
            - 相位差：δ = 2πΔ/λ = 2πd·sinθ/λ
            - 强度分布：I = I₀·cos²(πd·sinθ/λ)
            
            **干涉条件：**
            - 亮纹：d·sinθ = kλ (k=0,±1,±2,...)
            - 暗纹：d·sinθ = (k+1/2)λ (k=0,±1,±2,...)
            
            **条纹间距：**
            Δx = λD/d
            
            其中：
            - λ：光波长
            - d：双缝间距
            - D：屏距
            - θ：衍射角
            """,
            "steps": [
                {"step": "1. 设置光源", "description": "选择单色光源，波长建议在可见光范围(400-760nm)"},
                {"step": "2. 调整缝距", "description": "设置双缝间距，建议范围0.1-1mm"},
                {"step": "3. 调整屏距", "description": "设置屏幕与双缝的距离，建议范围1-5m"},
                {"step": "4. 观察现象", "description": "观察屏幕上的明暗条纹分布"},
                {"step": "5. 测量间距", "description": "测量相邻亮纹或暗纹之间的距离"},
                {"step": "6. 验证公式", "description": "利用公式Δx = λD/d验证实验结果"}
            ],
            "key_params": [
                {"name": "波长", "effect": "波长越长，条纹间距越大", "formula": "Δx ∝ λ"},
                {"name": "缝距", "effect": "缝距越大，条纹间距越小", "formula": "Δx ∝ 1/d"},
                {"name": "屏距", "effect": "屏距越大，条纹间距越大", "formula": "Δx ∝ D"}
            ],
            "tips": [
                "使用单色光可以获得清晰的干涉条纹",
                "双缝必须足够窄以产生明显的衍射",
                "光源的相干性会影响条纹对比度"
            ]
        },
        "单缝衍射": {
            "principle": """
            **单缝衍射原理**
            
            单缝衍射是光通过单缝时产生的衍射现象。
            
            **核心公式：**
            - 强度分布：I = I₀·(sinβ/β)²
            - 其中：β = πa·sinθ/λ
            
            **暗纹条件：**
            a·sinθ = kλ (k=±1,±2,±3,...)
            
            **中央明纹宽度：**
            Δx₀ = 2λD/a
            
            其中：
            - λ：光波长
            - a：缝宽
            - D：屏距
            - θ：衍射角
            """,
            "steps": [
                {"step": "1. 设置光源", "description": "选择单色光源"},
                {"step": "2. 调整缝宽", "description": "设置单缝宽度，建议范围0.1-1mm"},
                {"step": "3. 调整屏距", "description": "设置屏幕与单缝的距离"},
                {"step": "4. 观察现象", "description": "观察中央宽亮条纹和两侧的明暗条纹"},
                {"step": "5. 测量宽度", "description": "测量中央明纹的宽度"},
                {"step": "6. 分析次级", "description": "观察次级明纹的强度分布"}
            ],
            "key_params": [
                {"name": "波长", "effect": "波长越长，衍射条纹越宽", "formula": "Δx ∝ λ"},
                {"name": "缝宽", "effect": "缝宽越小，衍射条纹越宽", "formula": "Δx ∝ 1/a"},
                {"name": "屏距", "effect": "屏距越大，衍射条纹越宽", "formula": "Δx ∝ D"}
            ],
            "tips": [
                "单缝宽度越小，衍射现象越明显",
                "中央明纹宽度是次级明纹的2倍",
                "次级明纹强度约为中央明纹的1/20"
            ]
        },
        "多缝光栅": {
            "principle": """
            **多缝光栅原理**
            
            多缝光栅由大量等宽等间距的平行狭缝组成。
            
            **核心公式：**
            - 光栅方程：d·sinθ = kλ (k=0,±1,±2,...)
            - 强度分布：I = I₀·(sinβ/β)²·(sin(Nγ)/sin(γ))²
            - 其中：β = πa·sinθ/λ, γ = πd·sinθ/λ
            
            **缺级条件：**
            当 d/a = 整数时，对应级次的主极大消失
            
            其中：
            - λ：光波长
            - d：光栅常数
            - a：缝宽
            - N：缝数
            - θ：衍射角
            """,
            "steps": [
                {"step": "1. 选择光栅", "description": "选择合适的光栅常数和缝数"},
                {"step": "2. 设置光源", "description": "使用单色光或白光"},
                {"step": "3. 调整角度", "description": "调整光栅与入射光的角度"},
                {"step": "4. 观察光谱", "description": "观察光栅光谱"},
                {"step": "5. 测量角度", "description": "测量各主极大的衍射角"},
                {"step": "6. 计算波长", "description": "利用光栅方程计算波长"}
            ],
            "key_params": [
                {"name": "光栅常数", "effect": "光栅常数越小，衍射角越大", "formula": "sinθ ∝ 1/d"},
                {"name": "缝数", "effect": "缝数越多，主极大越细锐", "formula": "锐度 ∝ N"},
                {"name": "波长", "effect": "波长越长，同一级次衍射角越大", "formula": "sinθ ∝ λ"}
            ],
            "tips": [
                "光栅常数越小，光谱展开越明显",
                "缝数越多，谱线越细锐",
                "白光入射会产生色散光谱"
            ]
        },
        "迈克耳孙干涉": {
            "principle": """
            **迈克耳孙干涉原理**
            
            迈克耳孙干涉仪利用分振幅法产生双光束干涉。
            
            **核心公式：**
            - 光程差：Δ = 2d·cosθ
            - 条纹移动数：ΔN = 2Δd/λ
            
            **等倾干涉条件：**
            2d·cosθ = kλ (k=0,1,2,...)
            
            **等厚干涉条件：**
            2d + λ/2 = kλ (考虑半波损失)
            
            其中：
            - λ：光波长
            - d：两虚光源间距
            - θ：入射角
            """,
            "steps": [
                {"step": "1. 调节光路", "description": "调整平面镜使两束光光程相等"},
                {"step": "2. 观察条纹", "description": "观察等倾或等厚干涉条纹"},
                {"step": "3. 移动镜台", "description": "缓慢移动其中一个平面镜"},
                {"step": "4. 计数条纹", "description": "记录条纹移动的数量"},
                {"step": "5. 计算位移", "description": "利用Δd = ΔN·λ/2计算镜位移"},
                {"step": "6. 分析误差", "description": "分析测量误差来源"}
            ],
            "key_params": [
                {"name": "波长", "effect": "波长越长，同样位移产生的条纹移动数越少", "formula": "ΔN ∝ 1/λ"},
                {"name": "镜位移", "effect": "位移越大，条纹移动数越多", "formula": "ΔN ∝ Δd"},
                {"name": "入射角", "effect": "入射角越大，光程差越小", "formula": "Δ ∝ cosθ"}
            ],
            "tips": [
                "保持光路稳定是获得清晰条纹的关键",
                "使用扩展光源观察等倾干涉",
                "使用点光源观察等厚干涉"
            ]
        },
        "薄膜干涉": {
            "principle": """
            **薄膜干涉原理**
            
            薄膜干涉是光在薄膜上下表面反射后产生的干涉现象。
            
            **核心公式：**
            - 光程差：Δ = 2nd·cosθ
            - 考虑半波损失时：Δ = 2nd·cosθ + λ/2
            
            **等倾干涉（平行薄膜）：**
            2nd·cosθ = kλ (亮纹)
            2nd·cosθ = (k+1/2)λ (暗纹)
            
            **等厚干涉（劈尖）：**
            2nd + λ/2 = kλ (亮纹)
            
            其中：
            - λ：光波长
            - n：薄膜折射率
            - d：薄膜厚度
            - θ：折射角
            """,
            "steps": [
                {"step": "1. 准备薄膜", "description": "准备均匀薄膜或劈尖薄膜"},
                {"step": "2. 设置光源", "description": "使用单色光或白光"},
                {"step": "3. 调整角度", "description": "调整观察角度"},
                {"step": "4. 观察条纹", "description": "观察等倾或等厚干涉条纹"},
                {"step": "5. 测量间距", "description": "测量条纹间距"},
                {"step": "6. 计算参数", "description": "计算薄膜厚度或折射率"}
            ],
            "key_params": [
                {"name": "折射率", "effect": "折射率越大，光程差越大", "formula": "Δ ∝ n"},
                {"name": "薄膜厚度", "effect": "厚度变化影响条纹间距", "formula": "Δx ∝ 1/d"},
                {"name": "波长", "effect": "波长越长，条纹间距越大", "formula": "Δx ∝ λ"}
            ],
            "tips": [
                "注意半波损失的判断",
                "等倾干涉条纹是同心圆",
                "等厚干涉条纹是平行直线"
            ]
        },
        "偏振干涉": {
            "principle": """
            **偏振干涉原理**
            
            偏振干涉是偏振光通过各向异性介质后产生的干涉现象。
            
            **核心公式：**
            - 相位延迟：δ = 2π(ne-no)d/λ
            - 强度分布：I = I₀·sin²(δ/2)·sin²(2θ)
            
            **偏振光通过波片：**
            - 线偏振光 → 椭圆偏振光（通过1/4波片）
            - 线偏振光 → 线偏振光（通过1/2波片）
            
            其中：
            - λ：光波长
            - ne, no：寻常光和非常光折射率
            - d：波片厚度
            - θ：偏振方向与波片光轴夹角
            """,
            "steps": [
                {"step": "1. 设置偏振器", "description": "调整起偏器和检偏器正交"},
                {"step": "2. 插入波片", "description": "在两偏振器之间插入波片"},
                {"step": "3. 调整角度", "description": "调整波片光轴角度"},
                {"step": "4. 观察现象", "description": "观察干涉颜色变化"},
                {"step": "5. 分析偏振态", "description": "分析出射光的偏振态"},
                {"step": "6. 计算相位差", "description": "计算波片产生的相位延迟"}
            ],
            "key_params": [
                {"name": "偏振角", "effect": "影响干涉强度", "formula": "I ∝ sin²(2θ)"},
                {"name": "波片厚度", "effect": "影响相位延迟", "formula": "δ ∝ d"},
                {"name": "折射率差", "effect": "影响相位延迟", "formula": "δ ∝ (ne-no)"}
            ],
            "tips": [
                "正交偏振器之间插入波片会产生彩色干涉",
                "1/4波片可将线偏振光变为圆偏振光",
                "偏振干涉在应力分析中有重要应用"
            ]
        }
    }
    
    @staticmethod
    def get_experiment_info(experiment_name: str) -> dict:
        """
        获取实验的教学信息
        
        参数:
            experiment_name: 实验名称
        
        返回:
            实验信息字典
        """
        return TeachingModule.EXPERIMENT_INFO.get(experiment_name, {})
    
    @staticmethod
    def get_principle(experiment_name: str) -> str:
        """
        获取实验原理说明
        
        参数:
            experiment_name: 实验名称
        
        返回:
            原理说明字符串
        """
        info = TeachingModule.get_experiment_info(experiment_name)
        return info.get("principle", "暂无原理说明")
    
    @staticmethod
    def get_steps(experiment_name: str) -> list:
        """
        获取实验步骤
        
        参数:
            experiment_name: 实验名称
        
        返回:
            步骤列表
        """
        info = TeachingModule.get_experiment_info(experiment_name)
        return info.get("steps", [])
    
    @staticmethod
    def get_key_params(experiment_name: str) -> list:
        """
        获取关键参数说明
        
        参数:
            experiment_name: 实验名称
        
        返回:
            参数说明列表
        """
        info = TeachingModule.get_experiment_info(experiment_name)
        return info.get("key_params", [])
    
    @staticmethod
    def get_tips(experiment_name: str) -> list:
        """
        获取实验提示
        
        参数:
            experiment_name: 实验名称
        
        返回:
            提示列表
        """
        info = TeachingModule.get_experiment_info(experiment_name)
        return info.get("tips", [])