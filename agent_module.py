import re
import requests
from typing import List, Dict, Optional

class PhysicsAgent:
    """
    波动光学智能体 - 基于千问大模型
    """

    def __init__(self):
        self.conversation_history = []
        self.api_url = "http://localhost:8000/v1/chat/completions"
        self.model_name = "Qwen"
        self.system_prompt = """你是一个波动光学领域的专业AI助手，名为"小光"。

专业领域：波动光学、干涉、衍射、偏振等物理实验

你可以帮助用户：
1. 解释双缝干涉、单缝衍射、多缝光栅、迈克耳孙干涉、薄膜干涉、偏振干涉等实验原理
2. 推导波动光学公式，如条纹间距、光程差、衍射角等
3. 根据给定参数计算物理量
4. 解答波动光学相关问题
5. 提供实验设计建议

回答要求：
- 语言亲切自然，像朋友聊天一样
- 适当使用markdown格式展示公式
- 计算题要展示步骤
- 可以适当举例子帮助理解
- 如果不确定，诚实说明

当前对话上下文会包含历史消息。"""

    def add_message(self, role: str, content: str):
        self.conversation_history.append({
            "role": role,
            "content": content
        })

    def call_qwen_api(self, messages: List[Dict]) -> Optional[str]:
        """调用千问API"""
        try:
            headers = {"Content-Type": "application/json"}
            payload = {
                "model": self.model_name,
                "messages": messages,
                "temperature": 0.8,
                "max_tokens": 1500
            }

            response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)

            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"]
            return None
        except Exception as e:
            print(f"API调用错误: {e}")
            return None

    def generate_response(self, user_input: str) -> str:
        """生成回复"""
        self.add_message("user", user_input)

        messages = [
            {"role": "system", "content": self.system_prompt}
        ]

        for msg in self.conversation_history[:-1]:
            messages.append({"role": msg["role"], "content": msg["content"]})

        response = self.call_qwen_api(messages)

        if response:
            self.add_message("assistant", response)
            return response

        local_response = self.get_local_response(user_input)
        self.add_message("assistant", local_response)
        return local_response

    def get_local_response(self, question: str) -> str:
        """本地知识回复"""
        question_lower = question.lower()

        if any(word in question_lower for word in ["你好", "hi", "hello", "嗨"]):
            return """你好！我是波动光学智能助手小光！🔬

很高兴认识你！我可以帮你：

• 解答波动光学的各种问题
• 解释干涉、衍射等实验原理
• 计算条纹间距、衍射角等参数
• 提供实验设计建议

有什么想问的尽管问我哦！"""

        if "原理" in question or "为什么" in question:
            if "双缝" in question:
                return """**双缝干涉原理** 🌟

双缝干涉是波动光学的经典实验，证明了光的波动性。

**核心思想：**
当光通过两条非常靠近的狭缝时，每个缝都相当于一个波源。根据惠更斯原理，这两个波源发出的光波在空间某点相遇时，会发生叠加——这就是干涉。

**关键公式：**
条纹间距公式：Δx = λD/d

其中：
- λ 是光的波长
- D 是缝到屏幕的距离
- d 是两条缝之间的距离

**生活实例：**
想象一下两个人同时扔石子到湖里，水波相遇时会形成漂亮的干涉图案，这就和双缝干涉类似！

有什么不明白的地方可以继续问我~"""
            elif "单缝" in question:
                return """**单缝衍射原理** 🌟

单缝衍射是光通过单个狭缝时发生的衍射现象。

**核心思想：**
根据惠更斯原理，狭缝上每一个点都可以看作一个新的波源。这些无数个波源发出的光相互干涉，在屏幕上形成明暗相间的条纹。

**中央明纹最亮的原因：**
在中央位置，所有波源的光程差最小，它们几乎同相叠加，所以最亮。

**暗纹条件：**
a·sinθ = kλ （k = ±1, ±2, ±3...）

**特点：**
中央明纹宽度是其他明纹的约2倍，亮度也是其他明纹的很多倍。

有什么问题尽管问！"""
            elif "光栅" in question:
                return """**光栅原理** 🌟

光栅是由大量等宽等间距的平行狭缝组成的光学器件。

**核心思想：**
多缝干涉 + 单缝衍射 = 光栅光谱

当复色光通过光栅时，不同波长的光会在不同角度产生主极大，形成漂亮的光谱。

**光栅方程：**
d·sinθ = kλ

d 是光栅常数（缝间距），θ 是衍射角，k 是级次

**为什么光谱很细锐？**
因为缝数越多，主极大就越细窄，分辨本领 R = kN 越高（N是缝数）。

想象一下很多人齐步走，声音会很响亮但也很集中——这就是多缝干涉的效果！"""
            elif "迈克耳孙" in question:
                return """**迈克耳孙干涉仪原理** 🌟

迈克耳孙干涉仪是测量微小位移和折射率的精密仪器！

**核心思想：**
一束光被分成两束，互相垂直传播后再合并，产生干涉。

**关键公式：**
条纹移动数 ΔN = 2Δd/λ

意思是：当镜子移动 Δd 距离时，会有 ΔN 个条纹从眼前飘过。

**趣味应用：**
探测引力波！LIGO实验站就是用迈克耳孙干涉仪的原理，探测到了极其微小的空间震动！

这个实验在精密测量领域超级重要~"""
            elif "薄膜" in question:
                return """**薄膜干涉原理** 🌟

当你看到肥皂泡或水面上油膜的彩色花纹时，就是薄膜干涉！

**核心思想：**
光在薄膜的上下两个表面分别反射，这两束反射光相遇时发生干涉。

**关键公式：**
光程差 Δ = 2nd·cosθ + λ/2

- n 是薄膜折射率
- d 是薄膜厚度
- θ 是折射角
- λ/2 是因为半波损失

**两种类型：**
1. **等厚干涉**：厚度变化的地方条纹平行（如劈尖）
2. **等倾干涉**：入射角不同干涉情况不同（如油膜）

肥皂泡的五彩斑斓就是薄膜干涉的杰作！"""
            elif "偏振" in question:
                return """**偏振原理** 🌟

偏振是光是横波的直接证据！

**核心概念：**
普通光源发出的光在各个方向振动，是"非偏振光"。通过偏振片后，只剩下一个方向振动的光，就是"线偏振光"。

**马吕斯定律：**
I = I₀·cos²θ

θ是两个偏振片透振方向夹角。当夹角为0°时光最强，为90°时完全消光！

**生活应用：**
• 3D电影的原理
• 相机偏振镜头减少反光
• 液晶显示屏

有趣吧？有什么问题尽管问我！"""

        if "计算" in question or any(word in question for word in ["算", "多少", "求"]):
            nums = re.findall(r'\d+(?:\.\d+)?', question)
            if "双缝" in question and len(nums) >= 2:
                try:
                    λ = float(nums[0]) * 1e-9
                    d = float(nums[1]) * 1e-3
                    D = float(nums[2]) if len(nums) > 2 else 1.0
                    Δx = λ * D / d
                    return f"""**双缝干涉计算** 🧮

让我来帮你算一下：

已知：
• 波长 λ = {nums[0]} nm = {λ:.2e} m
• 缝距 d = {nums[1]} mm = {d:.2e} m
• 屏距 D = {D} m

**计算步骤：**

条纹间距公式：Δx = λD/d

代入数值：
Δx = ({λ:.2e}) × {D} / ({d:.2e})

**结果：Δx = {Δx*1000:.3f} mm**

这意味着在屏幕上，相邻两条亮纹之间的距离大约是 {Δx*1000:.1f} 毫米。

如果实验测得的结果和这个接近，说明你的实验做得很准哦！还有什么想算的？"""
                except:
                    pass

        if "影响" in question or "变化" in question:
            if "双缝" in question:
                return """**双缝干涉参数影响** 📊

让我给你分析一下各参数的影响：

**条纹间距 Δx = λD/d**

| 参数 | 增大时 | 物理原因 |
|------|--------|----------|
| 波长 λ ↑ | 条纹变疏 | 波长越大，波的"拐弯能力"越强 |
| 缝距 d ↑ | 条纹变密 | 两缝距离越远，相干光夹角越大 |
| 屏距 D ↑ | 条纹变疏 | 相当于把屏幕往后拉，条纹放大了 |

**趣味理解：**
想象你站在两条小巷中间往外看：
- 波长就像风的大小，风越大（λ↑），声音拐弯越厉害
- 缝距就像两条小巷的距离，距离越远，交叉范围越大
- 屏距就像你往后站多远，往后站得越远，看到的范围越大

还有什么疑问吗？"""
            elif "单缝" in question:
                return """**单缝衍射参数影响** 📊

**中央明纹宽度 Δx₀ = 2λD/a**

| 参数 | 增大时 | 效果 |
|------|--------|------|
| 波长 λ ↑ | 中央纹变宽 | 长波衍射更明显 |
| 缝宽 a ↑ | 中央纹变窄 | 缝越宽，越像"小孔"，衍射越不明显 |
| 屏距 D ↑ | 中央纹变宽 | 距离越远，衍射图样越大 |

**关键结论：**
• 衍射是波动的固有属性，障碍物尺寸与波长越接近，衍射越明显
• 当缝宽远大于波长时，衍射几乎消失，光沿直线传播

这就像声音能绕过窗户传播，但光却不能（因为光波长太短了）！"""

        if "帮助" in question or "功能" in question:
            return """**小光能帮你的事情** 💡

嗨！我是波动光学助手小光，很高兴为你服务！

**我能帮你：**

📚 **知识解答**
- 解释各种波动光学实验原理
- 推导物理公式

🔢 **计算题**
- 输入参数，我帮你算结果
- 验证你的计算是否正确

🔬 **实验指导**
- 设计实验方案
- 分析实验误差

💬 **自由讨论**
- 任何波动光学相关的问题都可以问我！

**试试这样问我：**
- "双缝干涉的原理是什么？"
- "波长600nm，缝距0.5mm，屏距1.5m，条纹间距是多少？"
- "为什么单缝衍射中央明纹最亮？"
- "帮我设计测波长的方案"

有什么想问的尽管说~"""

        return f"""这个问题有点意思，让我想想... 🤔

关于"{question}"

说实话，我可能需要更了解你的具体问题才能给出好的回答。

**你可以这样问我：**

🔹 "双缝干涉的原理是什么？" → 了解原理
🔹 "波长540nm，缝距0.5mm，屏距1m，算条纹间距" → 计算
🔹 "单缝衍射中缝宽的影响" → 分析影响
🔹 "帮我设计测波长的方案" → 实验设计

或者直接说你想了解什么方面的内容？小光随时为你解答！😊"""

    def clear_history(self):
        self.conversation_history = []

    def get_history(self) -> List[Dict]:
        return self.conversation_history

    def set_api_config(self, api_url: str, model_name: str):
        self.api_url = api_url
        self.model_name = model_name