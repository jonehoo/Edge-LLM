"""
大模型服务模块
支持本地模型（llama-cpp-python）和OpenAI API
"""

import os
from pathlib import Path
from typing import Optional, Dict, List, Iterator, Callable
import logging

# 尝试导入llama-cpp-python，如果失败则使用模拟模式
try:
    from llama_cpp import Llama
    LLAMA_AVAILABLE = True
except ImportError:
    LLAMA_AVAILABLE = False
    logging.warning("llama-cpp-python未安装，本地模型将不可用")

# 尝试导入OpenAI，如果失败则OpenAI模式不可用
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("openai库未安装，OpenAI模式将不可用")

logger = logging.getLogger(__name__)


class LLMService:
    """大模型服务 - 支持本地模型和OpenAI"""
    
    def __init__(self, 
                 model_type: str = "local",
                 model_path: str = "models/qwen-0.6b.gguf", 
                 n_ctx: int = 2048, 
                 n_threads: int = 4,
                 openai_api_key: Optional[str] = None,
                 openai_model: str = "gpt-3.5-turbo",
                 openai_base_url: Optional[str] = None,
                 openai_no_think: bool = False):
        """
        初始化LLM服务
        
        Args:
            model_type: 模型类型，"local" 或 "openai"
            model_path: 本地模型文件路径（当model_type="local"时使用）
            n_ctx: 上下文窗口大小（本地模型）
            n_threads: 线程数（本地模型）
            openai_api_key: OpenAI API密钥（当model_type="openai"时使用）
            openai_model: OpenAI模型名称，如 "gpt-3.5-turbo", "gpt-4" 等
            openai_base_url: OpenAI API基础URL（可选，用于兼容OpenAI API的代理）
            openai_no_think: 是否启用非思考模式（性能优化），响应时间可从10秒降至1秒左右
        """
        self.model_type = model_type.lower()
        self.model_path = Path(model_path) if model_path else None
        self.n_ctx = n_ctx
        self.n_threads = n_threads
        self.openai_api_key = openai_api_key
        self.openai_model = openai_model
        self.openai_base_url = openai_base_url
        self.openai_no_think = openai_no_think
        
        # 本地模型相关
        self.llm = None
        self.model_loaded = False
        
        # OpenAI客户端
        self.openai_client = None
        self.openai_available = False
        
        # 根据模型类型初始化
        if self.model_type == "openai":
            self._init_openai()
        else:
            self._init_local()
    
    def _init_local(self):
        """初始化本地模型"""
        if not LLAMA_AVAILABLE:
            logger.warning("llama-cpp-python未安装，本地模型将不可用")
            return
        
        if not self.model_path or not self.model_path.exists():
            logger.warning(f"模型文件不存在: {self.model_path}，将使用模拟模式")
            return
        
        self._load_model()
    
    def _init_openai(self):
        """初始化OpenAI客户端"""
        if not OPENAI_AVAILABLE:
            logger.error("openai库未安装，请运行: pip install openai")
            return
        
        if not self.openai_api_key:
            logger.error("OpenAI API密钥未提供，请在配置文件中设置 openai.api_key")
            return
        
        try:
            client_kwargs = {
                "api_key": self.openai_api_key
            }
            if self.openai_base_url:
                client_kwargs["base_url"] = self.openai_base_url
            
            self.openai_client = OpenAI(**client_kwargs)
            self.openai_available = True
            logger.info(f"OpenAI客户端初始化成功，使用模型: {self.openai_model}")
        except Exception as e:
            logger.error(f"OpenAI客户端初始化失败: {e}")
            self.openai_available = False
    
    def _load_model(self):
        """加载模型"""
        if not self.model_path or not self.model_path.exists():
            logger.warning(f"模型文件不存在: {self.model_path}，将使用模拟模式")
            return
        
        try:
            logger.info(f"正在加载模型: {self.model_path}")
            self.llm = Llama(
                model_path=str(self.model_path),
                n_ctx=self.n_ctx,
                n_threads=self.n_threads,
                verbose=False
            )
            self.model_loaded = True
            logger.info("模型加载成功")
        except Exception as e:
            logger.error(f"模型加载失败: {e}，将使用模拟模式")
            self.model_loaded = False
    
    def generate(self, prompt: str, max_tokens: int = 512, 
                 temperature: float = 0.7, top_p: float = 0.9,
                 stop: Optional[List[str]] = None,
                 repeat_penalty: float = 1.1, top_k: int = 40) -> str:
        """
        生成文本
        
        Args:
            prompt: 输入提示词
            max_tokens: 最大生成token数
            temperature: 温度参数（降低可减少重复）
            top_p: top_p采样参数
            stop: 停止词列表
            repeat_penalty: 重复惩罚系数（>1.0会减少重复）
            top_k: top_k采样参数
            
        Returns:
            生成的文本
        """
        # 如果是OpenAI模式，使用OpenAI生成
        if self.model_type == "openai":
            return self._generate_openai(prompt, max_tokens, temperature, stop)
        
        # 本地模型模式
        if not self.model_loaded or self.llm is None:
            return self._mock_generate(prompt)
        
        # 默认停止词（防止重复和无限生成）
        if stop is None:
            stop = ["\n\n\n", "###", "---", "<|endoftext|>", "<|end|>", 
                   "用户:", "User:", "问题:", "Question:"]
        
        try:
            response = self.llm(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                repeat_penalty=repeat_penalty,  # 添加重复惩罚
                stop=stop,
                echo=False
            )
            
            generated_text = response['choices'][0]['text'].strip()
            
            # 后处理：移除明显的重复模式
            generated_text = self._remove_repetition(generated_text)
            
            # 移除提示词残留
            generated_text = self._clean_prompt_artifacts(generated_text)
            
            return generated_text
        except Exception as e:
            logger.error(f"生成文本时出错: {e}")
            return self._mock_generate(prompt)
    
    def _generate_openai(self, prompt: str, max_tokens: int,
                        temperature: float, stop: Optional[List[str]]) -> str:
        """使用OpenAI API生成文本（非流式）"""
        if not self.openai_available or self.openai_client is None:
            logger.error("OpenAI客户端未初始化，将使用模拟模式")
            return self._mock_generate(prompt)
        
        try:
            # 如果启用了非思考模式，在提示词前添加 /no_think 参数
            user_content = prompt
            if self.openai_no_think:
                user_content = "/no_think\n\n" + prompt
                logger.debug("已启用非思考模式（/no_think），响应速度将提升")
            
            response = self.openai_client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "你是一个专业的数据分析助手，擅长分析温度传感器数据并提供专业的建议。"},
                    {"role": "user", "content": user_content}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                stop=stop if stop else None
            )
            
            generated_text = response.choices[0].message.content.strip()
            
            # 后处理：移除明显的重复模式
            generated_text = self._remove_repetition(generated_text)
            
            # 移除提示词残留
            generated_text = self._clean_prompt_artifacts(generated_text)
            
            return generated_text
        except Exception as e:
            logger.error(f"OpenAI生成文本时出错: {e}")
            return self._mock_generate(prompt)
    
    def generate_stream(self, prompt: str, max_tokens: int = 512,
                       temperature: float = 0.7, top_p: float = 0.9,
                       stop: Optional[List[str]] = None,
                       repeat_penalty: float = 1.1, top_k: int = 40,
                       callback: Optional[Callable[[str], None]] = None) -> Iterator[str]:
        """
        流式生成文本（生成器）
        
        Args:
            prompt: 输入提示词
            max_tokens: 最大生成token数
            temperature: 温度参数
            top_p: top_p采样参数
            stop: 停止词列表
            repeat_penalty: 重复惩罚系数（仅本地模型）
            top_k: top_k采样参数（仅本地模型）
            callback: 可选的回调函数，每次生成新token时调用
            
        Yields:
            生成的文本片段
        """
        if self.model_type == "openai":
            yield from self._generate_stream_openai(prompt, max_tokens, temperature, stop, callback)
        else:
            yield from self._generate_stream_local(prompt, max_tokens, temperature, top_p, stop, repeat_penalty, top_k, callback)
    
    def _generate_stream_local(self, prompt: str, max_tokens: int,
                               temperature: float, top_p: float,
                               stop: Optional[List[str]], repeat_penalty: float, top_k: int,
                               callback: Optional[Callable[[str], None]]) -> Iterator[str]:
        """使用本地模型流式生成文本"""
        if not self.model_loaded or self.llm is None:
            # 模拟流式输出
            mock_text = self._mock_generate(prompt)
            for char in mock_text:
                if callback:
                    callback(char)
                yield char
            return
        
        # 默认停止词
        if stop is None:
            stop = ["\n\n\n", "###", "---", "<|endoftext|>", "<|end|>", 
                   "用户:", "User:", "问题:", "Question:"]
        
        try:
            # 使用流式生成
            stream = self.llm(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                repeat_penalty=repeat_penalty,
                stop=stop,
                echo=False,
                stream=True  # 启用流式输出
            )
            
            accumulated_text = ""
            buffer = ""
            
            for output in stream:
                if 'choices' in output and len(output['choices']) > 0:
                    delta = output['choices'][0].get('text', '')
                    if delta:
                        accumulated_text += delta
                        buffer += delta
                        
                        # 当缓冲区积累到一定长度或遇到换行时，yield一次
                        if '\n' in buffer or len(buffer) >= 10:
                            if callback:
                                callback(buffer)
                            yield buffer
                            buffer = ""
            
            # 输出剩余的缓冲区内容
            if buffer:
                if callback:
                    callback(buffer)
                yield buffer
            
        except Exception as e:
            logger.error(f"本地模型流式生成文本时出错: {e}")
            # 出错时返回模拟结果
            mock_text = self._mock_generate(prompt)
            for char in mock_text:
                if callback:
                    callback(char)
                yield char
    
    def _generate_stream_openai(self, prompt: str, max_tokens: int,
                               temperature: float, stop: Optional[List[str]],
                               callback: Optional[Callable[[str], None]]) -> Iterator[str]:
        """使用OpenAI API流式生成文本"""
        if not self.openai_available or self.openai_client is None:
            logger.error("OpenAI客户端未初始化，将使用模拟模式")
            mock_text = self._mock_generate(prompt)
            for char in mock_text:
                if callback:
                    callback(char)
                yield char
            return
        
        try:
            # 如果启用了非思考模式，在提示词前添加 /no_think 参数
            user_content = prompt
            if self.openai_no_think:
                user_content = "/no_think\n\n" + prompt
                logger.debug("已启用非思考模式（/no_think），响应速度将提升")
            
            stream = self.openai_client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "你是一个专业的数据分析助手，擅长分析温度传感器数据并提供专业的建议。"},
                    {"role": "user", "content": user_content}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                stop=stop if stop else None,
                stream=True
            )
            
            buffer = ""
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    buffer += content
                    
                    # 当缓冲区积累到一定长度或遇到换行时，yield一次
                    if '\n' in buffer or len(buffer) >= 10:
                        if callback:
                            callback(buffer)
                        yield buffer
                        buffer = ""
            
            # 输出剩余的缓冲区内容
            if buffer:
                if callback:
                    callback(buffer)
                yield buffer
                
        except Exception as e:
            logger.error(f"OpenAI流式生成文本时出错: {e}")
            # 出错时返回模拟结果
            mock_text = self._mock_generate(prompt)
            for char in mock_text:
                if callback:
                    callback(char)
                yield char
    
    def _remove_repetition(self, text: str, max_repeat: int = 2) -> str:
        """
        移除文本中的重复内容
        
        Args:
            text: 输入文本
            max_repeat: 允许的最大重复次数
            
        Returns:
            清理后的文本
        """
        if not text:
            return text
        
        # 移除明显的重复段落（通过查找重复的句子序列）
        # 先按段落分割
        paragraphs = text.split('\n\n')
        unique_paragraphs = []
        seen_paragraphs = set()
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # 使用段落的前50个字符作为唯一性标识
            para_key = para[:50].strip() if len(para) > 50 else para.strip()
            # 归一化：移除数字和特殊字符进行比较
            para_normalized = ''.join(c for c in para_key if c.isalnum() or c in '，。、')
            
            if para_normalized and para_normalized not in seen_paragraphs:
                seen_paragraphs.add(para_normalized)
                unique_paragraphs.append(para)
        
        text = '\n\n'.join(unique_paragraphs)
        
        # 移除行级别的重复
        lines = text.split('\n')
        cleaned_lines = []
        last_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                if cleaned_lines and cleaned_lines[-1]:  # 只保留一个空行
                    cleaned_lines.append('')
                continue
            
            # 检查是否与最近的行重复
            is_repeat = False
            for prev_line in last_lines:
                # 如果当前行与之前的行完全相同，或者是之前行的子串，则跳过
                if line == prev_line:
                    is_repeat = True
                    break
                # 如果当前行是之前行的重复（超过80%相似）
                if len(line) > 10 and len(prev_line) > 10:
                    similarity = len(set(line) & set(prev_line)) / max(len(set(line)), len(set(prev_line)))
                    if similarity > 0.8:
                        is_repeat = True
                        break
            
            if not is_repeat:
                cleaned_lines.append(line)
                # 维护最近的行历史（最多10行）
                last_lines.append(line)
                if len(last_lines) > 10:
                    last_lines.pop(0)
        
        result = '\n'.join(cleaned_lines)
        
        # 移除句子级别的重复
        sentences = result.split('。')
        unique_sentences = []
        seen_sentences = set()
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence or len(sentence) < 5:
                continue
            
            # 使用前30个字符作为唯一性标识
            key = sentence[:30] if len(sentence) > 30 else sentence
            # 归一化键
            key_normalized = ''.join(c for c in key if c.isalnum() or c in '，。、')
            
            if key_normalized and key_normalized not in seen_sentences:
                seen_sentences.add(key_normalized)
                unique_sentences.append(sentence)
        
        result = '。'.join(unique_sentences) if unique_sentences else result
        
        # 移除明显的重复短语（如"好的，我现在为您整理了"等）
        common_repeats = [
            "好的，我现在为您整理了",
            "好的，我已根据要求",
            "好的!以下是",
            "好的!以下是基于",
            "希望您能理解并接受",
            "如果还有其他问题",
            "以下是最终回答",
            "请结合上述分析结果"
        ]
        
        for repeat_phrase in common_repeats:
            if repeat_phrase in result:
                # 找到并移除包含重复短语的句子
                parts = result.split(repeat_phrase)
                if len(parts) > 1:
                    # 保留第一部分，移除后续重复部分
                    result = parts[0].strip()
                    break
        
        return result.strip()
    
    def _clean_prompt_artifacts(self, text: str) -> str:
        """
        清理提示词残留和格式问题
        
        Args:
            text: 输入文本
            
        Returns:
            清理后的文本
        """
        if not text:
            return text
        
        import re
        
        # 移除常见的提示词残留和格式标记
        artifacts = [
            "请根据要求",
            "请根据分析结果",
            "请检查是否有遗漏",
            "答案是：",
            "答案：",
            "答案正确无误",
            "以下是最终回答",
            "以下是数据分析结果：",
            "使用正式、专业的语气",
            "请用中文回答",
            "简洁明了",
            "避免重复",
            "回答采用",
            "修改说明：",
            "问题分析：",
            "问题均已正确回答",
            "好的，以下是根据",
            "好的!以下是",
            "好的!以下是基于",
            "好的!以下是基于温度数据",
            "好的，我现在",
            "所有信息均符合要求",
            "所有信息均符合",
            "问题用编号标注",
            "每句不超过",
            "每个建议不超过",
            "每个方面用",
            "每个要点用",
            "每个问题用",
            "分点明确",
            "要求：",
            "要求:",
            "请直接",
            "请直接回答",
            "请直接提供"
        ]
        
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检查是否包含提示词残留
            is_artifact = False
            for artifact in artifacts:
                if artifact in line:
                    is_artifact = True
                    break
            
            # 检查是否是纯格式行（如"修改说明："、"问题分析："等）
            if line.endswith('：') and len(line) < 10:
                is_artifact = True
            
            # 检查是否是问题描述行（如"每个建议不超过3句话，分点明确。"）
            if re.search(r'每个[^。！？]*不超过\d+句话', line) or \
               re.search(r'每个[^。！？]*用\d+[-\s]*\d*句话', line) or \
               re.search(r'分点明确', line) and len(line) < 20:
                is_artifact = True
            
            # 检查是否是"好的!以下是..."开头的行（但不包括Markdown标题）
            if re.match(r'好的[！!]?以下[是是基于于]*', line) and not line.strip().startswith('#'):
                is_artifact = True
            
            if not is_artifact:
                cleaned_lines.append(line)
        
        result = '\n'.join(cleaned_lines)
        
        # 移除开头的格式标记
        if result.startswith('- '):
            result = result[2:].strip()
        
        # 移除包含问题描述的句子（如"每个建议不超过3句话，分点明确。"）
        result = re.sub(r'每个[^。！？\n]+不超过\d+句话[^。！？\n]*[。！？]?', '', result)
        result = re.sub(r'每个[^。！？\n]+用\d+[-\s]*\d*句话[^。！？\n]*[。！？]?', '', result)
        result = re.sub(r'分点明确[。！？]?', '', result)
        result = re.sub(r'要求[：:][^。！？\n]*[。！？]?', '', result)
        
        # 移除"好的!以下是..."开头的句子（但要保留Markdown标题）
        result = re.sub(r'好的[！!]?以下[是是基于于]*[^。！？\n#]*[：:：][^。！？\n#]*[。！？]?', '', result)
        
        # 移除重复的"问题X已回答"等标记
        result = re.sub(r'[（(]问题\d+已回答[）)]', '', result)
        result = re.sub(r'问题\d+[：:]', '', result)
        
        # 移除"正确"、"无误"等验证性标记
        result = re.sub(r'[，,]\s*正确[。.]?', '', result)
        result = re.sub(r'[，,]\s*无误[。.]?', '', result)
        result = re.sub(r'[，,]\s*准确[。.]?', '', result)
        result = re.sub(r'[，,]\s*合理[。.]?', '', result)
        
        # 移除重复的编号和内容（相同编号只保留第一个）
        lines = result.split('\n')
        seen_numbers = set()  # 已出现的编号
        final_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                if final_lines and final_lines[-1]:  # 只保留一个空行
                    continue
                continue
            
            # 检查是否是编号行
            match = re.match(r'^(\d+)[\.、]\s*(.+)', line)
            if match:
                num = match.group(1)
                # 如果这个编号已经出现过，跳过（只保留第一个）
                if num in seen_numbers:
                    continue
                seen_numbers.add(num)
                final_lines.append(line)
            else:
                # 非编号行，检查是否与最近的行完全相同
                if not final_lines or line != final_lines[-1]:
                    final_lines.append(line)
        
        result = '\n'.join(final_lines)
        
        return result.strip()
    
    def _mock_generate(self, prompt: str) -> str:
        """
        模拟生成（当模型未加载时使用）
        
        Args:
            prompt: 输入提示词
            
        Returns:
            模拟的生成文本
        """
        # 简单的规则基础回复
        if "温度" in prompt and "异常" in prompt:
            return """
根据数据分析，检测到以下温度异常情况：

1. **异常检测结果**：
   - 在08:20-08:30时间段，温度持续超过29°C，达到告警级别
   - 温度波动较大，从25.3°C快速上升到30.2°C

2. **建议措施**：
   - 立即检查设备散热系统
   - 考虑降低设备负载或增加通风
   - 持续监控温度变化趋势

3. **风险评估**：
   - 高温可能导致设备性能下降
   - 建议在温度超过28°C时采取预防措施
"""
        elif "趋势" in prompt or "预测" in prompt:
            return """
温度趋势分析：

1. **当前趋势**：温度呈下降趋势，从峰值30.2°C降至26.8°C
2. **预测**：如果当前趋势持续，预计未来1小时内温度将稳定在26-27°C
3. **建议**：继续保持当前状态，但需警惕温度再次上升
"""
        else:
            return """
根据提供的温度数据分析：

- 设备运行状态总体正常
- 存在部分时间段温度偏高的情况
- 建议持续监控并采取适当的温度控制措施
"""
    
    def analyze_temperature_data_stream(self, data_summary: str,
                                        analysis_type: str = "comprehensive",
                                        callback: Optional[Callable[[str], None]] = None) -> Iterator[str]:
        """
        流式分析温度数据
        
        Args:
            data_summary: 数据摘要
            analysis_type: 分析类型 (comprehensive, anomaly, trend, recommendation)
            callback: 可选的回调函数
            
        Yields:
            分析文本片段
        """
        prompt = self._build_analysis_prompt(data_summary, analysis_type)
        
        # 使用流式生成
        for chunk in self.generate_stream(
            prompt,
            max_tokens=600,
            temperature=0.75,
            top_p=0.9,
            top_k=40,
            repeat_penalty=1.2,
            stop=["\n\n\n", "###", "---", "分析完成", "报告结束", "希望您能理解", 
                  "如果还有其他问题", "好的，我现在", "以下是最终回答"],
            callback=callback
        ):
            yield chunk
    
    def _build_analysis_prompt(self, data_summary: str, analysis_type: str) -> str:
        """
        构建分析提示词
        
        Args:
            data_summary: 数据摘要
            analysis_type: 分析类型
            
        Returns:
            提示词字符串
        """
        if analysis_type == "comprehensive":
            return f"""分析以下温度传感器数据，并提供详细的分析报告：

{data_summary}

请使用Markdown格式输出，从以下方面进行分析，每个方面用2-3句话概括：

## 1. 数据概览和关键指标

## 2. 异常检测和风险评估

## 3. 温度趋势分析

## 4. 设备健康状态评估

## 5. 改进建议和预防措施

重要要求：
- 使用Markdown格式：使用 ## 作为二级标题，使用 **粗体** 强调关键数据，使用列表展示要点
- 用中文回答，语言专业但易懂
- 每个方面只说一次，不要重复
- 不要重复前面的内容
- 直接给出分析结果，不要添加"好的"、"接下来"、"以下是"等过渡语
- 不要输出问题描述或要求（如"每个方面用X句话"等）
- 分析完成后立即结束"""
        
        elif analysis_type == "anomaly":
            return f"""分析以下温度数据中的异常情况：

{data_summary}

请使用Markdown格式输出，直接回答以下问题，每个问题用2-3句话：

## 1. 异常温度点的识别

## 2. 异常原因分析

## 3. 异常对设备的影响

## 4. 处理建议

要求：
- 使用Markdown格式：使用 ## 作为二级标题，使用 **粗体** 强调关键信息，使用列表展示要点
- 用中文回答，简洁明了，不要重复
- 不要添加"请"、"以下是"、"好的"等过渡语
- 不要输出问题描述或要求"""
        
        elif analysis_type == "trend":
            return f"""分析以下温度数据的趋势：

{data_summary}

请使用Markdown格式输出，直接回答，每个要点用2-3句话：

## 1. 温度变化趋势

## 2. 未来趋势预测

## 3. 可能的风险点

## 4. 建议的监控策略

要求：
- 使用Markdown格式：使用 ## 作为二级标题，使用 **粗体** 强调关键数据，使用列表展示要点
- 用中文回答，简洁概括，不要重复
- 直接给出分析结果，不要输出问题描述或要求"""
        
        elif analysis_type == "recommendation":
            return f"""基于以下温度数据分析，提供专业的改进建议：

{data_summary}

请使用Markdown格式输出，直接提供建议，每个方面用2-3句话：

## 1. 设备维护建议

## 2. 温度控制优化方案

## 3. 预防措施

## 4. 长期监控策略

重要要求：
- 使用Markdown格式：使用 ## 作为二级标题，使用 **粗体** 强调关键建议，使用列表展示具体措施
- 直接给出建议，不要重复问题
- 不要添加"好的"、"以下是"等过渡语
- 不要输出"每个建议不超过X句话"等要求描述"""
        
        else:
            return f"""分析以下温度数据：

{data_summary}

请使用Markdown格式输出分析结果：
- 使用 ## 作为二级标题
- 使用 **粗体** 强调关键信息
- 使用列表展示要点
- 用中文回答，简洁明了，不要重复"""
    
    def analyze_temperature_data(self, data_summary: str, 
                                 analysis_type: str = "comprehensive") -> str:
        """
        分析温度数据（非流式）
        
        Args:
            data_summary: 数据摘要
            analysis_type: 分析类型 (comprehensive, anomaly, trend, recommendation)
            
        Returns:
            分析结果
        """
        prompt = self._build_analysis_prompt(data_summary, analysis_type)
        
        # 优化生成参数以减少重复
        return self.generate(
            prompt, 
            max_tokens=600,  # 进一步减少最大token数，防止过长
            temperature=0.75,  # 适中的温度
            top_p=0.9,
            top_k=40,
            repeat_penalty=1.2,  # 增加重复惩罚
            stop=["\n\n\n", "###", "---", "分析完成", "报告结束", "希望您能理解", 
                  "如果还有其他问题", "好的，我现在", "以下是最终回答"]
        )
    
    def is_available(self) -> bool:
        """
        检查模型是否可用
        
        Returns:
            模型是否可用
        """
        if self.model_type == "openai":
            return self.openai_available
        else:
            return self.model_loaded
    
    def get_model_info(self) -> Dict[str, str]:
        """
        获取模型信息
        
        Returns:
            模型信息字典
        """
        if self.model_type == "openai":
            return {
                "type": "OpenAI",
                "model": self.openai_model,
                "available": self.openai_available
            }
        else:
            return {
                "type": "Local",
                "model": str(self.model_path) if self.model_path else "N/A",
                "available": self.model_loaded
            }

