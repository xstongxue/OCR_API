import cv2
import base64
import numpy as np
from io import BytesIO
from PIL import Image
import time
from fastapi import HTTPException
import ultralytics

class ModelPredict:
    """
    封装模型预测的方法
    model: 模型
    device: 模型所在设备
    timeout: 模型预测超时时间
    """
    def __init__(self, model, device, timeout=30):
        self.model: ultralytics.models.yolo.model.YOLO = model
        self.device: str = device
        self.timeout: int = timeout
        
    def predict(self, image_bytes):
        """
        使用模型进行预测
        Args:
            image_bytes: 图像字节数据
        Returns:
            模型预测结果
        Raises:
            HTTPException: 如果模型推理超时
        """
        start_time = time.time()  # 记录开始时间
        res = self.model.predict(
                    source=image_bytes,
                    device=self.device,
                    iou=0.2,  
                    conf=0.4,
                    agnostic_nms=True, # 一个目标上出现一个边框
                    save=False,
                    imgsz=640,
                    save_txt=False,
                    save_conf=False,
                    )
        # 检查是否超时
        if time.time() - start_time > self.timeout:
            raise HTTPException(status_code=408, detail="Request timeout: Model inference took too long.")
    
        return res
class ImgProcessTool:
    """
    图像处理工具类
    """
    def __init__(self):
        pass
    
    def img2base64(self, img: np.ndarray):
        """
        图像转base64编码
        Args:
            img: numpy 图像数组
        Returns:
            base64 编码的图像字符串
        """
        pil_img = Image.fromarray(img)
        buffered = BytesIO()
        pil_img.save(buffered, format="PNG")
        img_bytes = buffered.getvalue()
        base64_str = base64.b64encode(img_bytes).decode('utf-8')
        img_content = f"data:image/png;base64,{base64_str}"
        return img_content
