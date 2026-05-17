import random

class ExerciseModule:
    """
    练习模块
    提供波动光学相关的习题和答案
    """
    
    QUESTIONS = {
        "双缝干涉": {
            "基础题": [
                {
                    "question": "已知波长λ=500nm，缝距d=0.5mm，屏距D=1m，求条纹间距Δx。",
                    "answer": "Δx = λD/d = 500×10^-9 × 1 / 0.5×10^-3 = 1mm",
                    "solution": "使用公式Δx = λD/d，代入数值计算",
                    "difficulty": "基础"
                },
                {
                    "question": "双缝干涉中，若波长变为原来的2倍，条纹间距如何变化？",
                    "answer": "条纹间距变为原来的2倍",
                    "solution": "由Δx = λD/d，Δx ∝ λ，波长加倍则间距加倍",
                    "difficulty": "基础"
                },
                {
                    "question": "双缝干涉的亮纹条件是什么？",
                    "answer": "光程差Δ = d·sinθ = kλ (k=0,±1,±2,...)",
                    "solution": "当光程差为波长的整数倍时，两束光相干加强",
                    "difficulty": "基础"
                },
                {
                    "question": "若缝距d增大，干涉条纹会变密还是变疏？",
                    "answer": "条纹会变密",
                    "solution": "由Δx = λD/d，d增大则Δx减小，条纹变密",
                    "difficulty": "基础"
                },
                {
                    "question": "双缝干涉中，中央亮纹的光程差是多少？",
                    "answer": "中央亮纹的光程差为0",
                    "solution": "中央位置θ=0，Δ = d·sin0 = 0",
                    "difficulty": "基础"
                }
            ],
            "进阶题": [
                {
                    "question": "双缝干涉中，缝宽不均匀会对干涉条纹产生什么影响？",
                    "answer": "缝宽不均匀会导致衍射包络发生畸变，条纹对比度下降",
                    "solution": "缝宽不均匀会使单缝衍射的包络不再是理想的sinc²函数，导致各干涉级次的强度分布不均匀",
                    "difficulty": "进阶"
                },
                {
                    "question": "如果光源的相干性变差，干涉条纹会有什么变化？",
                    "answer": "条纹对比度下降，甚至完全消失",
                    "solution": "相干性差意味着两束光的相位差不稳定，导致干涉图样模糊",
                    "difficulty": "进阶"
                },
                {
                    "question": "双缝干涉实验中，如何测量光波长？",
                    "answer": "测量条纹间距Δx，缝距d，屏距D，利用λ = Δx·d/D计算",
                    "solution": "由Δx = λD/d变形得λ = Δx·d/D",
                    "difficulty": "进阶"
                },
                {
                    "question": "若双缝之一被宽度相同的不透明条覆盖，屏幕上会出现什么现象？",
                    "answer": "变成单缝衍射图样",
                    "solution": "只剩一个缝透光，发生单缝衍射",
                    "difficulty": "进阶"
                },
                {
                    "question": "双缝干涉中，相邻亮纹之间的相位差是多少？",
                    "answer": "相邻亮纹之间的相位差为2π",
                    "solution": "亮纹条件为相位差δ = 2kπ，相邻亮纹k相差1，故相位差相差2π",
                    "difficulty": "进阶"
                }
            ],
            "创新题": [
                {
                    "question": "设计一个实验方案，利用双缝干涉测量透明薄膜的折射率。",
                    "answer": "将薄膜放在其中一条光路中，测量条纹移动数，利用光程差变化计算折射率",
                    "solution": "设薄膜厚度为t，折射率为n，则光程差变化为(n-1)t。每移动一个条纹，光程差变化为λ。测量条纹移动数N，则(n-1)t = Nλ，可解出n",
                    "difficulty": "创新"
                },
                {
                    "question": "如何利用双缝干涉验证光的横波特性？",
                    "answer": "在双缝前加入偏振片，旋转偏振片观察条纹变化",
                    "solution": "若光为横波，旋转偏振片会改变光的偏振方向，影响干涉条纹的强度分布。如果光为纵波，则不会有明显变化",
                    "difficulty": "创新"
                },
                {
                    "question": "设计一个实验，区分相干光源和非相干光源。",
                    "answer": "利用双缝干涉装置，能产生稳定干涉条纹的是相干光源",
                    "solution": "相干光源产生的干涉条纹稳定清晰，非相干光源产生的条纹模糊或不出现",
                    "difficulty": "创新"
                }
            ]
        },
        "单缝衍射": {
            "基础题": [
                {
                    "question": "单缝衍射的暗纹条件是什么？",
                    "answer": "a·sinθ = kλ (k=±1,±2,±3,...)",
                    "solution": "菲涅耳半波带法：相邻半波带的光干涉相消",
                    "difficulty": "基础"
                },
                {
                    "question": "单缝衍射中央明纹的宽度是多少？",
                    "answer": "Δx₀ = 2λD/a",
                    "solution": "中央明纹宽度为两侧第一暗纹之间的距离",
                    "difficulty": "基础"
                },
                {
                    "question": "若缝宽a增大，衍射条纹会变密还是变疏？",
                    "answer": "条纹会变密（中央明纹变窄）",
                    "solution": "由Δx₀ = 2λD/a，a增大则Δx₀减小",
                    "difficulty": "基础"
                },
                {
                    "question": "单缝衍射的强度分布公式是什么？",
                    "answer": "I = I₀·(sinβ/β)²，其中β = πa·sinθ/λ",
                    "solution": "基于惠更斯-菲涅耳原理的积分结果",
                    "difficulty": "基础"
                }
            ],
            "进阶题": [
                {
                    "question": "单缝衍射中，次级明纹的强度为什么远小于中央明纹？",
                    "answer": "次级明纹是菲涅耳半波带部分抵消的结果",
                    "solution": "中央明纹对应所有半波带相长干涉，次级明纹对应奇数个半波带中，大部分相互抵消，只剩一个半波带的贡献",
                    "difficulty": "进阶"
                },
                {
                    "question": "如果单缝宽度与波长相当，会发生什么现象？",
                    "answer": "衍射效应非常明显，中央明纹会非常宽",
                    "solution": "当a≈λ时，sinθ≈1，衍射角很大，几乎整个屏幕都被中央明纹覆盖",
                    "difficulty": "进阶"
                },
                {
                    "question": "如何区分单缝衍射和双缝干涉的图样？",
                    "answer": "单缝衍射中央明纹宽，两侧条纹强度递减；双缝干涉条纹等间距，强度相近",
                    "solution": "单缝衍射是sinc²包络，双缝干涉是cos²分布叠加单缝包络",
                    "difficulty": "进阶"
                }
            ],
            "创新题": [
                {
                    "question": "设计一个利用单缝衍射测量细丝直径的实验方案。",
                    "answer": "利用互补原理，细丝衍射与单缝衍射图样相同，测量条纹间距计算直径",
                    "solution": "根据巴比涅原理，细丝和宽度相同的单缝产生的衍射图样互补。测量中央明纹宽度Δx₀，利用a = 2λD/Δx₀计算细丝直径",
                    "difficulty": "创新"
                },
                {
                    "question": "如何利用单缝衍射验证惠更斯原理？",
                    "answer": "通过改变缝宽，观察衍射图样变化，验证理论预测",
                    "solution": "根据惠更斯原理，缝上每一点都是次波源。改变缝宽，观察中央明纹宽度与缝宽的反比关系，验证理论",
                    "difficulty": "创新"
                }
            ]
        },
        "多缝光栅": {
            "基础题": [
                {
                    "question": "光栅方程是什么？",
                    "answer": "d·sinθ = kλ (k=0,±1,±2,...)",
                    "solution": "多光束干涉主极大条件",
                    "difficulty": "基础"
                },
                {
                    "question": "光栅常数d与缝宽a、缝间距b的关系是什么？",
                    "answer": "d = a + b",
                    "solution": "光栅常数等于缝宽与缝间距之和",
                    "difficulty": "基础"
                },
                {
                    "question": "光栅光谱中，同一级次的光谱，波长越长，衍射角如何变化？",
                    "answer": "波长越长，衍射角越大",
                    "solution": "由d·sinθ = kλ，sinθ ∝ λ",
                    "difficulty": "基础"
                }
            ],
            "进阶题": [
                {
                    "question": "光栅的缺级条件是什么？",
                    "answer": "当d/a为整数时，对应级次缺级",
                    "solution": "当单缝衍射极小与多缝干涉极大重合时，该级次消失",
                    "difficulty": "进阶"
                },
                {
                    "question": "为什么光栅缝数越多，谱线越细锐？",
                    "answer": "缝数越多，主极大之间的角距离越小，且主极大宽度与缝数成反比",
                    "solution": "主极大宽度Δθ ≈ λ/(Nd·cosθ)，N越大，Δθ越小",
                    "difficulty": "进阶"
                },
                {
                    "question": "光栅的分辨本领是多少？",
                    "answer": "R = λ/Δλ = kN",
                    "solution": "分辨本领与光谱级次k和缝数N成正比",
                    "difficulty": "进阶"
                }
            ],
            "创新题": [
                {
                    "question": "设计一个利用光栅测量未知波长的实验方案。",
                    "answer": "用已知波长校准光栅常数，再测量未知波长的衍射角",
                    "solution": "先用已知波长λ₁测量衍射角θ₁，计算光栅常数d = kλ₁/sinθ₁。再测量未知波长的衍射角θ₂，计算λ₂ = d·sinθ₂/k",
                    "difficulty": "创新"
                },
                {
                    "question": "如何设计一个光栅，使某一级次的光谱不重叠？",
                    "answer": "选择合适的光栅常数，使相邻级次的光谱范围不重叠",
                    "solution": "要求k₁λ_max < k₂λ_min，例如第一级和第二级不重叠要求λ_max < 2λ_min",
                    "difficulty": "创新"
                }
            ]
        },
        "迈克耳孙干涉": {
            "基础题": [
                {
                    "question": "迈克耳孙干涉仪中，平面镜移动Δd，条纹移动数ΔN与波长λ的关系是什么？",
                    "answer": "ΔN = 2Δd/λ",
                    "solution": "光往返两次经过这段距离，光程差变化为2Δd",
                    "difficulty": "基础"
                },
                {
                    "question": "迈克耳孙干涉仪的等倾干涉条纹是什么形状？",
                    "answer": "同心圆环",
                    "solution": "等倾干涉中，相同入射角的光线形成同一级条纹",
                    "difficulty": "基础"
                },
                {
                    "question": "迈克耳孙干涉仪的主要应用有哪些？",
                    "answer": "测量微小位移、测量折射率、光谱分析",
                    "solution": "利用条纹移动测量微小位移，精度可达λ/2",
                    "difficulty": "基础"
                }
            ],
            "进阶题": [
                {
                    "question": "迈克耳孙干涉仪中，为什么要考虑半波损失？",
                    "answer": "光从光疏介质到光密介质反射时有半波损失",
                    "solution": "两束光中有一束在平面镜上反射时有半波损失，另一束没有，需考虑此相位差",
                    "difficulty": "进阶"
                },
                {
                    "question": "如何区分迈克耳孙干涉的等倾条纹和等厚条纹？",
                    "answer": "等倾条纹是同心圆，等厚条纹是平行直线",
                    "solution": "等倾干涉：入射角相同形成同一圆环；等厚干涉：厚度相同形成同一直线",
                    "difficulty": "进阶"
                },
                {
                    "question": "迈克耳孙干涉仪测量长度的精度为什么很高？",
                    "answer": "可以精确到波长量级",
                    "solution": "通过计数条纹移动数，Δd = ΔN·λ/2，波长可达几百纳米",
                    "difficulty": "进阶"
                }
            ],
            "创新题": [
                {
                    "question": "如何利用迈克耳孙干涉仪测量空气折射率？",
                    "answer": "在一条光路中插入气室，改变气压测量条纹移动数",
                    "solution": "设气室长度为L，折射率变化Δn，则光程差变化为2LΔn = ΔNλ，可得Δn = ΔNλ/(2L)",
                    "difficulty": "创新"
                },
                {
                    "question": "设计一个利用迈克耳孙干涉仪检测光学元件表面平整度的方案。",
                    "answer": "将待测元件与标准元件比较，观察干涉条纹的弯曲情况",
                    "solution": "若条纹弯曲，说明表面不平整，根据弯曲程度计算平整度误差",
                    "difficulty": "创新"
                }
            ]
        },
        "薄膜干涉": {
            "基础题": [
                {
                    "question": "薄膜干涉的光程差公式是什么（考虑半波损失）？",
                    "answer": "Δ = 2nd·cosθ + λ/2",
                    "solution": "2nd·cosθ是几何路程差，λ/2是半波损失",
                    "difficulty": "基础"
                },
                {
                    "question": "等厚干涉的条纹是什么形状？",
                    "answer": "平行直线（劈尖）或同心圆（牛顿环）",
                    "solution": "厚度相同的地方形成同一级条纹",
                    "difficulty": "基础"
                },
                {
                    "question": "增透膜的原理是什么？",
                    "answer": "利用薄膜干涉使反射光相消，透射光增强",
                    "solution": "选择合适的膜厚，使两束反射光的光程差为λ/2，产生相消干涉",
                    "difficulty": "基础"
                }
            ],
            "进阶题": [
                {
                    "question": "如何判断是否存在半波损失？",
                    "answer": "当光从光疏介质入射到光密介质表面反射时，存在半波损失",
                    "solution": "折射率较小的介质为光疏介质，较大的为光密介质",
                    "difficulty": "进阶"
                },
                {
                    "question": "牛顿环的中心为什么是暗斑？",
                    "answer": "中心处空气膜厚度为0，但存在半波损失，两束光相位差为π",
                    "solution": "中心接触点，几何路程差为0，但反射光有半波损失，故为暗斑",
                    "difficulty": "进阶"
                },
                {
                    "question": "为什么肥皂水膜会呈现彩色？",
                    "answer": "白光干涉的结果，不同波长的光在不同厚度处产生相长干涉",
                    "solution": "薄膜厚度不均匀，不同位置对不同波长的光满足相长干涉条件",
                    "difficulty": "进阶"
                }
            ],
            "创新题": [
                {
                    "question": "设计一个利用薄膜干涉测量薄膜厚度的实验方案。",
                    "answer": "利用劈尖干涉，测量条纹间距计算厚度",
                    "solution": "相邻条纹对应厚度差为λ/(2n)，测量N条条纹的间距L，则厚度h = NλL/(2nl)",
                    "difficulty": "创新"
                },
                {
                    "question": "如何设计一个反射式干涉滤光片？",
                    "answer": "利用多层薄膜的干涉效应，只允许特定波长通过",
                    "solution": "选择合适的膜系结构，使目标波长产生相长干涉，其他波长相消",
                    "difficulty": "创新"
                }
            ]
        },
        "偏振干涉": {
            "基础题": [
                {
                    "question": "线偏振光通过1/4波片后，偏振态如何变化？",
                    "answer": "当线偏振方向与波片光轴成45°时，变为圆偏振光",
                    "solution": "1/4波片使o光和e光产生π/2的相位差",
                    "difficulty": "基础"
                },
                {
                    "question": "马吕斯定律的内容是什么？",
                    "answer": "I = I₀·cos²θ，其中θ是起偏器和检偏器的夹角",
                    "solution": "线偏振光通过检偏器后的强度与偏振方向夹角的余弦平方成正比",
                    "difficulty": "基础"
                },
                {
                    "question": "如何区分自然光和圆偏振光？",
                    "answer": "用1/4波片和检偏器组合检测",
                    "solution": "圆偏振光通过1/4波片后变为线偏振光，可被检偏器消光",
                    "difficulty": "基础"
                }
            ],
            "进阶题": [
                {
                    "question": "偏振光干涉的强度分布公式是什么？",
                    "answer": "I = I₀·sin²(δ/2)·sin²(2θ)",
                    "solution": "δ是相位延迟，θ是偏振方向与波片光轴的夹角",
                    "difficulty": "进阶"
                },
                {
                    "question": "1/2波片的作用是什么？",
                    "answer": "使o光和e光产生π的相位差，改变线偏振光的偏振方向",
                    "solution": "线偏振光通过1/2波片后，偏振方向转过2θ",
                    "difficulty": "进阶"
                },
                {
                    "question": "为什么正交偏振器之间插入波片会产生彩色干涉？",
                    "answer": "不同波长的光通过波片后的相位延迟不同，干涉结果不同",
                    "solution": "白光包含不同波长，波片对不同波长产生不同相位延迟，导致不同颜色的光干涉结果不同",
                    "difficulty": "进阶"
                }
            ],
            "创新题": [
                {
                    "question": "设计一个产生圆偏振光的实验方案。",
                    "answer": "线偏振光通过1/4波片，波片光轴与偏振方向成45°",
                    "solution": "此时o光和e光振幅相等，相位差π/2，合成圆偏振光",
                    "difficulty": "创新"
                },
                {
                    "question": "如何区分线偏振光、圆偏振光和自然光？",
                    "answer": "使用检偏器和1/4波片组合检测",
                    "solution": "先用检偏器：有消光位置的是线偏振光；再用1/4波片+检偏器：能消光的是圆偏振光，不能消光的是自然光",
                    "difficulty": "创新"
                }
            ]
        }
    }
    
    @staticmethod
    def get_questions(experiment_name: str, level: str) -> list:
        """
        获取指定实验和难度级别的题目
        
        参数:
            experiment_name: 实验名称
            level: 难度级别（基础题/进阶题/创新题）
        
        返回:
            题目列表
        """
        if experiment_name not in ExerciseModule.QUESTIONS:
            return []
        return ExerciseModule.QUESTIONS[experiment_name].get(level, [])
    
    @staticmethod
    def get_random_question(experiment_name: str, level: str) -> dict:
        """
        获取随机题目
        
        参数:
            experiment_name: 实验名称
            level: 难度级别
        
        返回:
            随机题目
        """
        questions = ExerciseModule.get_questions(experiment_name, level)
        if questions:
            return random.choice(questions)
        return None
    
    @staticmethod
    def get_all_experiments() -> list:
        """
        获取所有实验名称
        
        返回:
            实验名称列表
        """
        return list(ExerciseModule.QUESTIONS.keys())