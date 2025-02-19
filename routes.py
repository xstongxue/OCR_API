from fastapi import APIRouter, File, Form, UploadFile,HTTPException
from fastapi.responses import JSONResponse
from fastapi.responses import StreamingResponse
from starlette.responses import RedirectResponse
import numpy as np
from io import BytesIO
from PIL import Image
from pydantic import BaseModel
import base64
import cv2
import json
import re

from config import *
from utils import *

app_routers = APIRouter()
@app_routers.get("/")
async def document():
    """
    重定向到文档页面
    """
    return RedirectResponse(url="/docs")

# ======================================  QWen7B-VL-OCR  =====================================
@app_routers.post("/OCR-QWen2.5-7B-VL1")
async def qwen7bvl_ocr(img: UploadFile = File(...)):
    """
    原始多模态 OCR，用于测试未擦除的原图像
    Args:
        img (UploadFile): 上传的图像文件
    Returns:
        JSONResponse: 包含 OCR 结果的 JSON 响应
    """
    result = {"success": False}

    # 读取上传的文件并转为图像
    image_bytes = await img.read()  # 读取文件内容(二进制格式)
    image_np = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

    # 解析文件名
    image_name = img.filename
    
    if img is None:
        result = {'code': -1, 'message': '测试文件为空'}
        return JSONResponse(content=result, status_code=400)

    # 将 mask 图像转为 base64 编码
    pil_img = Image.fromarray(image)
    buffered = BytesIO()
    pil_img.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()
    base64_str = base64.b64encode(img_bytes).decode('utf-8')
    img_content = f"data:image/png;base64,{base64_str}"

    # 调用 OCR API
    ocr_text = await call_ocr(img_content, prompt_ocr, qwen_VL_url, headers)

    ret_json = {
        'code': 200,
        'message': '成功',
        'ocr': ocr_text, 
    }
    return JSONResponse(content=ret_json)


# ======================================  QWen7B-VL-OCR（给前端调用）  =====================================
class Box(BaseModel):
    x: float
    y: float
    width: float
    height: float

class OcrRequest(BaseModel):
    image: str  # base64 encoded image data
    box: Box    # target box information

@app_routers.post("/OCR-QWen2.5-7B-VL")
async def ocr(payload: OcrRequest):
    """
    接收前端传递的图像 base64 编码和 box 信息，进行 OCR 识别
    Args:
        payload (OcrRequest): 包含图像 base64 编码和 box 信息的请求体
    Returns:
        JSONResponse: 包含 OCR 识别结果的 JSON 响应
    Raises:
        HTTPException: 如果输入无效或 OCR 处理失败
    """
    try:
        # Validate and clean base64 string
        base64_data = payload.image
        if ',' in base64_data:
            base64_data = base64_data.split(',')[1]
            
        # Validate base64 format
        if not re.match('^[A-Za-z0-9+/]*={0,2}$', base64_data):
            raise ValueError("Invalid base64 format")
            
        # Decode base64 image data
        try:
            image_bytes = base64.b64decode(base64_data)
        except Exception as e:
            raise ValueError(f"Base64 decoding failed: {str(e)}")
            
        # Construct image content with proper format
        img_content = f"data:image/png;base64,{base64.b64encode(image_bytes).decode('utf-8')}"
        
        # Call OCR model
        ocr_text = await call_ocr(img_content, prompt_ocr, qwen_VL_url, headers)
        
        # Prepare response
        ret_json = {
            'code': 200,
            'message': '成功',
            'ocr_text': ocr_text
        }
        
        return JSONResponse(content=ret_json)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR 处理失败: {str(e)}")
# ======================================  OCR-MiniCPM2.6-V-8B(用于测试未擦除的原图像)  =====================================
@app_routers.post("/OCR-MiniCPM2.6-V-8B")
async def minicpm_ocr(img: UploadFile = File(...)):
    """
    原始多模态 OCR，用于测试未擦除的原图像
    Args:
        img (UploadFile): 上传的图像文件
    Returns:
        JSONResponse: 包含 OCR 结果的 JSON 响应
    """
    result = {"success": False}

    # 读取上传的文件并转为图像
    image_bytes = await img.read()  # 读取文件内容(二进制格式)
    image_np = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

    # 解析文件名
    image_name = img.filename
    
    if img is None:
        result = {'code': -1, 'message': '测试文件为空'}
        return JSONResponse(content=result, status_code=400)

    # 将 mask 图像转为 base64 编码
    pil_img = Image.fromarray(image)
    buffered = BytesIO()
    pil_img.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()
    base64_str = base64.b64encode(img_bytes).decode('utf-8')
    img_content = f"data:image/png;base64,{base64_str}"

    # 请求URL
    url = "http://192.168.4.22:8892/MiniCPM2.6-V-8B/OCR"
    # 请求体
    data = {
        "params_form": {
            "Beam_Search": {
                "sampling": False,
                "num_beams": 3,
                "repetition_penalty": 1.2,
                "temperature": 0.7,
                "max_new_tokens": 2048
            }
        },
        "prompt": "ocr",
        "image": img_content
    }
    
    # 调用 OCR API
    try:
        response = requests.post(url, json=data)
        response_json = response.json()["response"]
        ret_json = {
            'code': 200,
            'message': '成功',
            'ocr': response_json,
        }
        return JSONResponse(content=ret_json)
    except requests.exceptions.Timeout as e:
            raise e
    except requests.exceptions.RequestException as e:
        raise e
    except Exception as e:
        raise e
