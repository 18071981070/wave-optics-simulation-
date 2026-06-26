"""
增强版智能体模块 - 整合物理实验智能助手
支持实验上下文感知、结构化知识库、物理计算工具
支持阿里云DashScope和本地Ollama两种API方式
"""
import re
import math
import requests
from typing import List, Dict, Optional, Any


class EnhancedPhysicsAgent:
    """
    增强版物理实验智能体 - 支持实验上下文感知和高级功能
    """

    def __init__(self):
        self.conversation_history = []
        self.api_type = "dashscope"
        self.api_url = "http://localhost:8000/v1/chat/completions"
        self.model_name = "qwen3-max"
        self.dashscope_api_key = ""
        self.current_mode = "physics"
        self.current_experiment = None
        self.current_parameters = {}
        self.api_status = "unknown"
        self.api_error_message = ""

        self.physics_system_prompt = """你是一个波动光学领域的专业AI助手，名为"小光"。

## 专业领域
波动光学、干涉、衍射、偏振等物理实验

## 当前实验信息
用户正在进行物理实验，当前实验：{experiment_name}
当前实验参数：
{parameters}

## 所有实验核心公式参考

### 1. 双缝干涉
- 条纹间距：Δx = λ·D/d
- 光程差：δ = d·sinθ ≈ d·tanθ = d·x/D
- 亮纹条件：δ = kλ (k = 0, ±1, ±2...)
- 暗纹条件：δ = (k+1/2)λ (k = 0, ±1, ±2...)

### 2. 单缝衍射
- 暗纹条件：a·sinθ = kλ (k = ±1, ±2, ±3...)
- 中央明纹宽度：Δx₀ = 2λ·D/a
- 第k级明纹宽度：Δxₖ = λ·D/a
- 光强分布：I = I₀·(sinα/α)²，α = πa·sinθ/λ

### 3. 多缝光栅
- 光栅方程：d·sinθ = kλ (k = 0, ±1, ±2...)
- 缺级条件：d/a = m（m为整数）
- 分辨本领：R = λ/Δλ = k·N
- 角色散率：D = Δθ/Δλ = k/(d·cosθ)

### 4. 迈克耳孙干涉
- 条纹移动数：ΔN = 2Δd/λ
- 光程差：Δ = 2d·cosθ
- 亮纹条件：2d·cosθ = kλ
- 暗纹条件：2d·cosθ = (k+1/2)λ

### 5. 薄膜干涉
- 等厚干涉亮纹（考虑半波损失）：2nd + λ/2 = kλ (k = 1, 2, 3...)
- 等厚干涉暗纹：2nd + λ/2 = (k+1/2)λ (k = 0, 1, 2...)
- 等倾干涉亮纹：2nd·cosθ = kλ

### 6. 偏振干涉
- 马吕斯定律：I = I₀·cos²θ
- 波片相位差：δ = 2π(nₒ - nₑ)d/λ
- 1/4波片：(nₒ - nₑ)d = λ/4
- 1/2波片：(nₒ - nₑ)d = λ/2

## 符号说明
- λ：光波长（单位：m）
- d：缝距/光栅常数/薄膜厚度（单位：m）
- D：缝到屏幕距离（单位：m）
- θ：衍射角/入射角/折射角（单位：rad）
- a：缝宽（单位：m）
- n：折射率
- k：条纹级数/干涉级数
- N：光栅总缝数/条纹移动数

## 你的任务
1. **解释原理**：用通俗易懂的语言解释波动光学实验原理
2. **公式推导**：推导相关物理公式，使用LaTeX格式
3. **数值计算**：根据用户提供的参数进行计算，展示完整步骤
4. **实验建议**：根据当前实验参数给出针对性的分析和建议
5. **问题解答**：解答波动光学相关问题

## 回答要求
1. **必须使用当前实验参数**：如果用户问的是当前实验，务必使用上面给出的参数值进行计算和分析
2. **公式必须用LaTeX**：所有物理公式使用$...$或$$...$$包裹
3. **计算必须展示步骤**：一步步展示计算过程，不要只给结果
4. **语言亲切自然**：像朋友聊天一样，使用适当的语气词和表情
5. **适当举例**：用生活中的例子帮助理解复杂概念
6. **主动建议**：根据当前参数主动给出实验建议和优化方向
7. **诚实回答**：如果不确定，明确说明

## 示例回答格式

### 示例1：解释原理
"双缝干涉是波动光学的经典实验，证明了光的波动性！当光通过两条非常靠近的狭缝时，每个缝都相当于一个新的波源。根据惠更斯原理，这两个波源发出的光波在空间相遇时会发生叠加——这就是干涉现象。

你当前的参数是：波长540nm，缝距0.5mm，屏距1m。根据公式Δx = λD/d，你的条纹间距应该是Δx = 540×10⁻⁹ × 1 / 0.5×10⁻³ = 1.08mm。"

### 示例2：计算问题
"好的，我来帮你计算！根据公式：

$$Δx = \\frac{λ \\cdot D}{d}$$

代入你的参数：
- λ = {wavelength}
- D = {screen_distance}
- d = {slit_distance}

计算过程：
$$Δx = \\frac{{wavelength} \\times {screen_distance}}{{slit_distance}}$$
$$Δx = {result}$$

所以条纹间距是 {result}！"

### 示例3：实验建议
"根据你当前的参数（波长540nm，缝距0.5mm），我有几个建议：

1. 增大缝距d → 条纹会变密，更容易分辨
2. 增大波长λ → 条纹会变疏，更清晰
3. 增大屏距D → 条纹会变疏，适合观察

推荐尝试：把缝距调到0.3mm，看看条纹间距的变化！"

现在开始回答用户的问题！
"""

        self.general_system_prompt = """你是一个全能AI助手，可以回答各种问题。

你的能力包括：
1. 解答学习和生活中的各种问题
2. 提供建议和帮助
3. 解释概念和原理
4. 帮助分析和解决问题

回答要求：
- 语言亲切自然
- 回答清晰易懂
- 如果不确定，诚实说明"""

    def switch_mode(self, mode: str):
        self.current_mode = mode

    def set_experiment_context(self, experiment_name: str, parameters: Dict[str, Any] = None):
        self.current_experiment = experiment_name
        self.current_parameters = parameters or {}

    def set_api_type(self, api_type: str):
        self.api_type = api_type
        if api_type == "dashscope":
            self.api_url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
            self.model_name = "qwen3-max"
        elif api_type == "ollama":
            self.api_url = "http://localhost:8000/v1/chat/completions"
            self.model_name = "Qwen"

    def set_api_key(self, api_key: str):
        self.dashscope_api_key = api_key

    def set_api_config(self, api_url: str, model_name: str):
        self.api_url = api_url
        self.model_name = model_name

    def get_system_prompt(self) -> str:
        if self.current_mode == "physics":
            experiment_info = self.current_experiment or "未指定"
            params_info = "\n".join([f"- {k}: {v}" for k, v in self.current_parameters.items()]) if self.current_parameters else "无"
            return self.physics_system_prompt.format(
                experiment_name=experiment_info,
                parameters=params_info
            )
        else:
            return self.general_system_prompt

    def add_message(self, role: str, content: str):
        self.conversation_history.append({
            "role": role,
            "content": content
        })

    def test_api_connection(self) -> bool:
        """测试API连接"""
        if self.api_type == "dashscope":
            return self._test_dashscope_connection()
        else:
            return self._test_ollama_connection()

    def _test_dashscope_connection(self) -> bool:
        """测试DashScope API连接"""
        if not self.dashscope_api_key:
            self.api_status = "error"
            self.api_error_message = "请输入阿里云API Key"
            return False
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.dashscope_api_key}"
            }
            payload = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": "hi"}],
                "max_tokens": 10
            }
            
            response = requests.post(
                "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if "choices" in result:
                    self.api_status = "connected"
                    self.api_error_message = ""
                    return True
                else:
                    self.api_status = "error"
                    self.api_error_message = f"API返回格式错误: {result.get('error', {}).get('message', '未知错误')}"
                    return False
            else:
                self.api_status = "error"
                self.api_error_message = f"API返回错误，状态码: {response.status_code}"
                return False
        except requests.exceptions.ConnectionError:
            self.api_status = "disconnected"
            self.api_error_message = "网络连接失败，请检查网络"
            return False
        except requests.exceptions.Timeout:
            self.api_status = "timeout"
            self.api_error_message = "连接超时"
            return False
        except Exception as e:
            self.api_status = "error"
            self.api_error_message = f"API调用异常: {str(e)}"
            return False

    def _test_ollama_connection(self) -> bool:
        """测试Ollama API连接"""
        try:
            response = requests.get(self.api_url.replace("/chat/completions", "/v1/models"), timeout=10)
            if response.status_code == 200:
                self.api_status = "connected"
                self.api_error_message = ""
                return True
            else:
                self.api_status = "error"
                self.api_error_message = f"HTTP状态码: {response.status_code}"
                return False
        except requests.exceptions.ConnectionError:
            self.api_status = "disconnected"
            self.api_error_message = "连接被拒绝，请检查Ollama服务是否启动"
            return False
        except requests.exceptions.Timeout:
            self.api_status = "timeout"
            self.api_error_message = "连接超时，请检查网络"
            return False
        except Exception as e:
            self.api_status = "error"
            self.api_error_message = str(e)
            return False

    def call_api(self, messages: List[Dict]) -> Optional[str]:
        """调用API"""
        if self.api_type == "dashscope":
            return self._call_dashscope_api(messages)
        else:
            return self._call_ollama_api(messages)

    def _call_dashscope_api(self, messages: List[Dict]) -> Optional[str]:
        """调用DashScope API"""
        if not self.dashscope_api_key:
            self.api_status = "error"
            self.api_error_message = "请输入阿里云API Key"
            return None
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.dashscope_api_key}"
            }
            payload = {
                "model": self.model_name,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 3000,
                "stream": False
            }

            response = requests.post(
                "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    self.api_status = "connected"
                    self.api_error_message = ""
                    return result["choices"][0]["message"]["content"]
                else:
                    self.api_status = "error"
                    self.api_error_message = f"API返回格式错误: {result.get('error', {}).get('message', '未知错误')}"
            else:
                self.api_status = "error"
                self.api_error_message = f"API返回错误，状态码: {response.status_code}"
            
            return None
        except requests.exceptions.ConnectionError:
            self.api_status = "disconnected"
            self.api_error_message = "网络连接失败"
            return None
        except requests.exceptions.Timeout:
            self.api_status = "timeout"
            self.api_error_message = "API请求超时"
            return None
        except Exception as e:
            self.api_status = "error"
            self.api_error_message = f"API调用异常: {str(e)}"
            return None

    def _call_ollama_api(self, messages: List[Dict]) -> Optional[str]:
        """调用Ollama API"""
        try:
            headers = {"Content-Type": "application/json"}
            payload = {
                "model": self.model_name,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 3000,
                "stream": False
            }

            response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)

            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    self.api_status = "connected"
                    self.api_error_message = ""
                    return result["choices"][0]["message"]["content"]
                else:
                    self.api_status = "error"
                    self.api_error_message = "API返回格式错误"
            else:
                self.api_status = "error"
                self.api_error_message = f"API返回错误，状态码: {response.status_code}"
            
            return None
        except requests.exceptions.ConnectionError:
            self.api_status = "disconnected"
            self.api_error_message = "无法连接到Ollama服务，请检查服务是否启动"
            return None
        except requests.exceptions.Timeout:
            self.api_status = "timeout"
            self.api_error_message = "API请求超时"
            return None
        except Exception as e:
            self.api_status = "error"
            self.api_error_message = f"API调用异常: {str(e)}"
            return None

    def generate_response(self, user_input: str) -> str:
        """生成回复"""
        self.add_message("user", user_input)

        messages = [
            {"role": "system", "content": self.get_system_prompt()}
        ]

        for msg in self.conversation_history[:-1]:
            messages.append({"role": msg["role"], "content": msg["content"]})

        response = self.call_api(messages)

        if response:
            self.add_message("assistant", response)
            return response

        local_response = self.get_local_response(user_input)
        self.add_message("assistant", local_response)
        return local_response

    def get_local_response(self, question: str) -> str:
        """本地知识回复（API不可用时的降级方案）"""
        if self.current_mode == "physics":
            return self._get_physics_response(question)
        else:
            return self._get_general_response(question)

    def _get_physics_response(self, question: str) -> str:
        """物理模式本地回复（简洁版本）"""
        question_lower = question.lower()
        experiment_info = self.current_experiment or "物理实验"
        
        if any(word in question_lower for word in ["你好", "hi", "hello", "嗨", "在吗"]):
            return f"你好！我是波动光学助手小光！🔬 我看到你正在做【{experiment_info}】实验，有什么问题我可以帮你解答吗？"

        if "原理" in question or "为什么" in question:
            return f"""关于【{experiment_info}】的原理，简单来说就是光的干涉/衍射现象。由于AI服务暂时不可用，我没法详细解释，建议你检查一下API服务是否正常启动，或者参考页面上的"物理原理"部分！😊"""

        if "公式" in question or "计算" in question or "算" in question:
            params_str = ", ".join([f"{k}={v}" for k, v in self.current_parameters.items()]) if self.current_parameters else "暂无参数"
            return f"""我可以帮你计算！但是AI服务暂时不可用，没法进行详细计算。当前参数：{params_str}。建议检查API服务状态，或者使用页面上的"波长计算器"功能！📐"""

        if "帮助" in question or "help" in question or "怎么用" in question:
            return """你可以问我：实验原理、公式计算、实验设计建议等。不过目前AI服务暂时不可用，建议检查API连接！💡"""

        return f"""AI服务暂时不可用，没法详细回答你的问题。关于【{experiment_info}】实验，你可以查看页面上的"物理原理"部分，或者检查一下API服务是否正常启动！😊"""

    def _get_general_response(self, question: str) -> str:
        """通用模式本地回复（简洁版本）"""
        question_lower = question.lower()

        if any(word in question_lower for word in ["你好", "hi", "hello", "嗨", "在吗"]):
            return "你好！AI服务暂时不可用，建议检查API连接。你可以稍后再试！😊"

        if "帮助" in question or "help" in question or "你能做什么" in question:
            return "我可以帮你解答各种问题，但目前AI服务不可用。请检查API连接后再试！💡"

        return "AI服务暂时不可用，没法回答你的问题。请检查API服务是否正常启动！😊"

    def get_quick_questions(self) -> List[str]:
        if self.current_mode != "physics":
            return [
                "今天天气怎么样？",
                "推荐一些学习资源",
                "如何提高学习效率？",
                "有什么有趣的物理现象？"
            ]

        if self.current_experiment:
            experiment_questions = {
                "双缝干涉": [
                    "双缝干涉的原理是什么？",
                    "如何计算条纹间距？",
                    "影响条纹间距的因素有哪些？",
                    "为什么中央条纹最亮？",
                ],
                "单缝衍射": [
                    "单缝衍射的原理是什么？",
                    "中央明纹宽度怎么计算？",
                    "单缝衍射和双缝干涉有什么区别？",
                    "缝宽变化对条纹有什么影响？",
                ],
                "多缝光栅": [
                    "光栅的原理是什么？",
                    "什么是光栅方程？",
                    "为什么会出现缺级？",
                    "光栅如何分光？",
                ],
                "迈克耳孙干涉": [
                    "迈克耳孙干涉仪的原理是什么？",
                    "如何测量微小位移？",
                    "等倾干涉和等厚干涉有什么区别？",
                    "条纹为什么会吞吐？",
                ],
                "薄膜干涉": [
                    "薄膜干涉的原理是什么？",
                    "什么是增透膜？",
                    "半波损失是什么？",
                    "肥皂泡为什么有彩色？",
                ],
                "偏振干涉": [
                    "偏振光的种类有哪些？",
                    "马吕斯定律是什么？",
                    "波片有什么作用？",
                    "如何产生圆偏振光？",
                ],
            }
            return experiment_questions.get(self.current_experiment, [
                "这个实验的原理是什么？",
                "相关公式有哪些？",
                "实验中有什么注意事项？",
                "如何分析实验结果？",
            ])

        return [
            "双缝干涉的原理是什么？",
            "如何计算条纹间距？",
            "单缝衍射有什么特点？",
            "什么是相干性？",
        ]

    def suggest_parameters(self) -> str:
        if not self.current_experiment:
            return ""

        suggestions = {
            "双缝干涉": """💡 **实验建议**

当前参数：{params}

建议尝试：
- 增大缝距d → 条纹变密
- 增大波长λ → 条纹变疏
- 增大缝屏距离D → 条纹变疏

推荐参数组合：
- 波长：540nm（绿光）
- 缝距：0.1-1mm
- 缝屏距离：0.5-2m""",
            "单缝衍射": """💡 **实验建议**

当前参数：{params}

建议尝试：
- 减小缝宽a → 中央明纹变宽
- 增大波长λ → 中央明纹变宽

推荐参数组合：
- 缝宽：0.1-1mm
- 缝屏距离：0.5-2m""",
            "多缝光栅": """💡 **实验建议**

当前参数：{params}

建议尝试：
- 使用不同光栅常数d的光栅
- 观察不同级数的光谱
- 注意缺级现象

推荐参数组合：
- 光栅常数：100-1000线/mm""",
            "迈克耳孙干涉": """💡 **实验建议**

当前参数：{params}

建议尝试：
- 缓慢移动动镜，观察条纹变化
- 调整成等厚干涉，观察直条纹
- 用白光观察彩色条纹

注意事项：
- 动作要缓慢，避免震动
- 保持环境稳定""",
            "薄膜干涉": """💡 **实验建议**

当前参数：{params}

建议尝试：
- 观察不同厚度的薄膜
- 用白光和单色光分别照射
- 观察透射光和反射光的干涉

注意事项：
- 薄膜要均匀
- 避免污染薄膜表面""",
            "偏振干涉": """💡 **实验建议**

当前参数：{params}

建议尝试：
- 旋转检偏器，观察光强变化
- 插入不同厚度的波片
- 观察圆偏振光和椭圆偏振光

注意事项：
- 偏振片和波片要对准光轴
- 保持光路共轴""",
        }

        params_str = ", ".join([f"{k}={v}" for k, v in self.current_parameters.items()]) if self.current_parameters else "未设置"
        return suggestions.get(self.current_experiment, "").format(params=params_str)


def get_agent():
    return EnhancedPhysicsAgent()


EnhancedPhysicsAgent.clear_history = lambda self: self.conversation_history.clear()
EnhancedPhysicsAgent.get_history = lambda self: self.conversation_history
