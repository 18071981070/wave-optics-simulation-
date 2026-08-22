"""
增强版智能体模块 - 整合物理实验智能助手
支持实验上下文感知、结构化知识库、物理计算工具
支持阿里云DashScope和本地Ollama两种API方式
"""
import re
import math
import os
import requests
from typing import List, Dict, Optional, Any


class EnhancedPhysicsAgent:
    """
    增强版物理实验智能体 - 支持实验上下文感知和高级功能
    """

    def __init__(self):
        self.conversation_history = []
        self.api_type = "dashscope"
        self.api_url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        self.model_name = "qwen3-max"
        self.dashscope_api_key = ""
        self._environment_api_key = ""
        self.api_source = "未配置"
        self.api_key_env_name = ""
        self._load_environment_config()
        self.current_mode = "physics"
        self.current_experiment = None
        self.current_parameters = {}
        self.api_status = "unknown"
        self.api_error_message = ""
        if self._environment_api_key:
            self.api_status = "ready"

        self.physics_system_prompt = r"""你是一个波动光学领域的专业AI助手，名为"小光"。

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

    def _load_environment_config(self):
        """Load API settings from environment variables without exposing secrets."""
        api_type = os.getenv("PHYSICS_AGENT_API_TYPE", "").strip().lower()
        if api_type in {"ollama", "dashscope"}:
            self.api_type = api_type

        if self.api_type == "ollama":
            self.api_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1/chat/completions").strip()
            self.model_name = os.getenv("OLLAMA_MODEL", "qwen2.5:7b").strip()
            self.api_source = "系统环境变量" if os.getenv("OLLAMA_BASE_URL") or os.getenv("OLLAMA_MODEL") else "默认配置"
            return

        self.api_url = os.getenv(
            "DASHSCOPE_API_URL",
            os.getenv("OPENAI_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"),
        ).strip()
        self.model_name = os.getenv("DASHSCOPE_MODEL", os.getenv("OPENAI_MODEL", "qwen3-max")).strip()

        key_names = ("DASHSCOPE_API_KEY", "DASHSCOPE_KEY", "QWEN_API_KEY")
        for name in key_names:
            value = os.getenv(name, "").strip()
            if value:
                self._environment_api_key = value
                self.dashscope_api_key = value
                self.api_key_env_name = name
                self.api_source = "系统环境变量"
                break
        if not self._environment_api_key:
            # OPENAI_API_KEY is accepted only when a compatible custom endpoint is configured.
            if os.getenv("OPENAI_BASE_URL") and os.getenv("OPENAI_API_KEY"):
                self._environment_api_key = os.getenv("OPENAI_API_KEY").strip()
                self.dashscope_api_key = self._environment_api_key
                self.api_key_env_name = "OPENAI_API_KEY"
                self.api_source = "系统环境变量"
            else:
                self.api_source = "默认配置"

    def refresh_environment_config(self):
        """Re-read environment configuration while preserving the conversation."""
        self.api_type = "dashscope"
        self.api_url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        self.model_name = "qwen3-max"
        self.dashscope_api_key = ""
        self._environment_api_key = ""
        self.api_source = "未配置"
        self.api_key_env_name = ""
        self._load_environment_config()
        if self._environment_api_key and self.api_status in {"unknown", "ready"}:
            self.api_status = "ready"

    def switch_mode(self, mode: str):
        self.current_mode = mode

    def set_experiment_context(self, experiment_name: str, parameters: Dict[str, Any] = None):
        self.current_experiment = experiment_name
        self.current_parameters = parameters or {}

    def set_api_type(self, api_type: str):
        self.api_type = api_type
        if api_type == "dashscope":
            self.api_url = os.getenv("DASHSCOPE_API_URL", os.getenv("OPENAI_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions")).strip()
            self.model_name = os.getenv("DASHSCOPE_MODEL", os.getenv("OPENAI_MODEL", "qwen3-max")).strip()
        elif api_type == "ollama":
            self.api_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1/chat/completions").strip()
            self.model_name = os.getenv("OLLAMA_MODEL", "qwen2.5:7b").strip()

    def set_api_key(self, api_key: str):
        manual_key = (api_key or "").strip()
        if manual_key:
            self.dashscope_api_key = manual_key
            self.api_source = "手动输入"
        else:
            self.dashscope_api_key = self._environment_api_key
            self.api_source = "系统环境变量" if self._environment_api_key else "未配置"

    def set_api_config(self, api_url: str, model_name: str):
        self.api_url = (api_url or self.api_url).strip()
        self.model_name = (model_name or self.model_name).strip()

    def get_system_prompt(self) -> str:
        if self.current_mode == "physics":
            experiment_info = self.current_experiment or "未指定"
            params_info = "\n".join([f"- {k}: {v}" for k, v in self.current_parameters.items()]) if self.current_parameters else "无"
            # Do not use str.format here: the prompt contains many LaTeX
            # braces (for example \frac{...}{...}) that are not placeholders.
            prompt = self.physics_system_prompt.replace(
                "{experiment_name}", experiment_info
            ).replace("{parameters}", params_info)
            formula_hints = {
                "双缝干涉": "优先检查 Δx = λD/d，并说明波长、屏距增大时条纹变疏，缝距增大时条纹变密。",
                "单缝衍射": "优先检查 Δx₀ = 2λD/a，并区分中央明纹宽度与旁瓣强度。",
                "多缝光栅": "优先使用 d·sinθ = kλ，并结合缝数 N 说明主峰变窄、分辨率 R = kN。",
                "迈克耳孙干涉": "优先使用 ΔN = 2Δd/λ，解释反射臂位移为何对应两倍光程变化。",
                "薄膜干涉": "先判断反射相位是否发生半波损失，再使用 2nd·cosθ 的光程差表达式。",
                "偏振干涉": "优先使用 I = I₀·cos²θ，并根据波片相位延迟判断线偏振、圆偏振或椭圆偏振。",
            }
            prompt += "\n## 当前实验回答重点\n" + formula_hints.get(experiment_info, "先识别实验模型，再代入当前参数给出可检验的结论。")
            return prompt
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
                self.api_url,
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
                self.api_url,
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
        """Generate a reply without allowing an API failure to crash the UI."""
        question = (user_input or "").strip()
        if not question:
            return "请输入问题后再发送。"

        self.add_message("user", question)

        try:
            messages = [{"role": "system", "content": self.get_system_prompt()}]
            # Include the current user question. The previous implementation
            # sliced it off, so the first shortcut sent only a system prompt.
            for msg in self.conversation_history[-12:]:
                if msg.get("role") in {"user", "assistant"} and msg.get("content"):
                    messages.append({"role": msg["role"], "content": str(msg["content"])})
            response = self.call_api(messages)
        except Exception as exc:
            self.api_status = "error"
            self.api_error_message = f"智能助手处理失败：{exc}"
            response = None

        if response:
            self.add_message("assistant", response)
            return response

        local_response = self.get_local_response(question)
        self.add_message("assistant", local_response)
        return local_response

    def get_local_response(self, question: str) -> str:
        """本地知识回复（API不可用时的降级方案）"""
        if self.current_mode == "physics":
            return self._get_physics_response(question)
        else:
            return self._get_general_response(question)

    def _get_physics_response(self, question: str) -> str:
        """Physics-aware fallback used when the remote model is unavailable."""
        question_lower = question.lower()
        experiment_info = self.current_experiment or "物理实验"

        principle_answers = {
            "双缝干涉": (
                r"双缝同时受到同一相干光源照明时，两缝可看作频率相同、相位差稳定的次波源。"
                r"屏上某点的光程差为 $\delta=d\sin\theta$；当 $\delta=k\lambda$ 时相长干涉形成亮纹，"
                r"当 $\delta=(k+1/2)\lambda$ 时相消干涉形成暗纹。小角度下相邻亮纹间距为 "
                r"$\Delta x\approx\lambda D/d$。"
            ),
            "单缝衍射": (
                r"单缝内各点都可看作次波源，它们在观测方向上相干叠加。当 $a\sin\theta=k\lambda$ "
                r"时成对次波相互抵消，形成暗纹。中央亮纹宽度约为 $2\lambda D/a$，因此缝越窄，"
                r"衍射展开得越明显。"
            ),
            "多缝光栅": (
                r"光栅是多个相干窄缝的多光束干涉。满足 $d\sin\theta=k\lambda$ 的方向上，"
                r"所有缝的振幅同相相加，形成尖锐主极大；缝数 $N$ 越多，主峰越窄，分辨本领 $R=kN$ 越高。"
            ),
            "迈克耳孙干涉": (
                r"分束镜将入射光分到两条光臂，反射后再次合束。两束光的光程差决定明暗；"
                r"反射镜移动 $\Delta d$ 会使往返光程改变 $2\Delta d$，所以条纹移动数为 $\Delta N=2\Delta d/\lambda$。"
            ),
            "薄膜干涉": (
                r"薄膜上、下表面的反射光相互叠加，几何光程差为 $2nd\cos\theta$。"
                r"判断亮暗时还要检查两次反射是否只有一次发生半波损失，若是，需额外加上 $\pi$ 的相位差。"
            ),
            "偏振干涉": (
                r"起偏器先选出线偏振光，波片使两个正交分量产生相位延迟，检偏器再把它们投影到同一方向并叠加。"
                r"无波片时理想线偏振光遵循马吕斯定律 $I=I_0\cos^2\theta$。"
            ),
        }

        def number_from(*names):
            for name in names:
                value = self.current_parameters.get(name)
                if value is None:
                    continue
                match = re.search(r"[-+]?\d+(?:\.\d+)?", str(value))
                if match:
                    return float(match.group())
            return None

        # Provide a useful calculation even when the remote model is unavailable.
        if any(word in question_lower for word in ["公式", "计算", "怎么算", "间距", "宽度", "结果"]):
            wavelength_nm = number_from("波长")
            screen_m = number_from("屏距")
            slit_mm = number_from("缝距", "缝宽")
            if wavelength_nm is not None and screen_m is not None and slit_mm:
                if experiment_info == "双缝干涉":
                    fringe_mm = wavelength_nm * screen_m / slit_mm * 1e-3
                    return (
                        f"根据当前参数：λ={wavelength_nm:g} nm，D={screen_m:g} m，d={slit_mm:g} mm。\n\n"
                        "双缝条纹间距为 $\\Delta x=\\frac{\\lambda D}{d}$，代入得：\n\n"
                        f"$\\Delta x=\\frac{{{wavelength_nm:g}\\times10^{{-9}}\\times{screen_m:g}}}{{{slit_mm:g}\\times10^{{-3}}}}$"
                        f"$\\approx {fringe_mm:.3f}$ mm。调大 λ 或 D 会使条纹变疏，调大 d 会使条纹变密。"
                    )
                if experiment_info == "单缝衍射":
                    width_mm = 2 * wavelength_nm * screen_m / slit_mm * 1e-3
                    return (
                        f"当前中央明纹宽度按 $\\Delta x_0=2\\lambda D/a$ 计算。代入 λ={wavelength_nm:g} nm、"
                        f"D={screen_m:g} m、a={slit_mm:g} mm，得到 $\\Delta x_0\\approx {width_mm:.3f}$ mm。"
                        "缝宽减小或屏距增大时，中央明纹会明显变宽。"
                    )

        if any(word in question_lower for word in ["你好", "hi", "hello", "嗨", "在吗"]):
            return f"你好！我是波动光学助手小光！🔬 我看到你正在做【{experiment_info}】实验，有什么问题我可以帮你解答吗？"

        if "原理" in question or "为什么" in question:
            return principle_answers.get(
                experiment_info,
                "光学图样来自光波的相干叠加。请先确认实验类型，再根据光程差判断亮暗条件。",
            )

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
