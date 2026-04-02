"""LLM client wrapper for OpenAI-compatible providers."""

import json
import logging
import re
import time
from typing import Optional, Dict, Any, List
from openai import OpenAI

from ..config import Config

logger = logging.getLogger(__name__)


class LLMClient:
    """LLM客户端"""
    CHAT_JSON_MAX_RETRIES = 3
    CHAT_JSON_RETRY_DELAY_SECONDS = 3
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None
    ):
        self.api_key = api_key or Config.LLM_API_KEY
        self.base_url = base_url or Config.LLM_BASE_URL
        self.model = model or Config.LLM_MODEL_NAME
        
        if not self.api_key:
            raise ValueError("LLM_API_KEY 未配置")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: Optional[Dict] = None
    ) -> str:
        """
        发送聊天请求
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            response_format: 响应格式（如JSON模式）
            
        Returns:
            模型响应文本
        """
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        if response_format:
            kwargs["response_format"] = response_format
        
        response = self.client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content
        # 部分模型（如MiniMax M2.5）会在content中包含<think>思考内容，需要移除
        content = re.sub(r'<think>[\s\S]*?</think>', '', content).strip()
        return content
    
    def chat_json(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """
        发送聊天请求并返回JSON
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            
        Returns:
            解析后的JSON对象
        """
        last_error: Optional[Exception] = None

        for attempt in range(1, self.CHAT_JSON_MAX_RETRIES + 1):
            try:
                response = self.chat(
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    response_format={"type": "json_object"}
                )
                # 清理markdown代码块标记
                cleaned_response = response.strip()
                cleaned_response = re.sub(r'^```(?:json)?\s*\n?', '', cleaned_response, flags=re.IGNORECASE)
                cleaned_response = re.sub(r'\n?```\s*$', '', cleaned_response)
                cleaned_response = cleaned_response.strip()
                return json.loads(cleaned_response)
            except Exception as exc:
                last_error = exc
                if attempt >= self.CHAT_JSON_MAX_RETRIES:
                    break
                logger.warning(
                    "chat_json attempt %s/%s failed: %s",
                    attempt,
                    self.CHAT_JSON_MAX_RETRIES,
                    exc,
                )
                time.sleep(self.CHAT_JSON_RETRY_DELAY_SECONDS * attempt)

        if isinstance(last_error, json.JSONDecodeError):
            raise ValueError(f"LLM返回的JSON格式无效: {last_error}")
        if last_error:
            raise last_error
        raise ValueError("LLM返回的JSON格式无效")
