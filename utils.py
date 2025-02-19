import json
from ultralytics import YOLO
import requests
import asyncio
from concurrent.futures import ThreadPoolExecutor

from config import *
from BaseClass import *


# 创建一个全局的线程池
executor = ThreadPoolExecutor(max_workers=1)

def call_ocr_sync(img_content, prompt, qwen_url, headers, reocr='no'):
    """
    同步调用 OCR API，传入图像和提示文本，返回 OCR 结果。
    Args:
        img_content (str): 图像的 base64 编码
        prompt (str):  给 OCR 模型的提示文本
        qwen_url (str): OCR 服务的 URL
        headers (dict): 请求头
        reocr (str): 是否进行重试 OCR 的标志
    Returns:
        str: OCR 识别结果
    """
    data_format_7B = {
        "model": ocr_model,
        "messages": [
            {"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": img_content}}]}
        ],
        "temperature": 0.1,
        # "repetition_penalty": 1.1,
    }

    attempt = 0
    while attempt <= 1:
        try:
            response = requests.post(qwen_url, headers=headers, data=json.dumps(data_format_7B), timeout=60)
            response_json = response.json()
            return response_json['choices'][0]['message']['content']
        except requests.exceptions.Timeout as e:
            if attempt <= 1 and reocr=='yes':
                attempt += 1
                print(f"Timeout occurred. Retrying... ({attempt}/{1}, temperature: 0.7)")
                data_format_7B["temperature"] = 0.7
            else:
                raise e
        except requests.exceptions.RequestException as e:
            raise e
        except Exception as e:
            raise e

async def call_ocr(img_content, prompt, qwen_url, headers, reocr='no'):
    """
    使用线程池异步执行 OCR 请求，避免阻塞主线程。
    Args:
        img_content (str): 图像的 base64 编码
        prompt (str):  给 OCR 模型的提示文本
        qwen_url (str): OCR 服务的 URL
        headers (dict): 请求头
        reocr (str): 是否进行重试 OCR 的标志
    Returns:
        str: OCR 识别结果
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, call_ocr_sync, img_content, prompt, qwen_url, headers, reocr)
