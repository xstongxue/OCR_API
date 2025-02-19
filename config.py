import argparse
import os

# ===================== 传参配置 =====================
parser = argparse.ArgumentParser()
parser.add_argument("--device", type=str, default="0", help="Specify the device to use for model inference")
parser.add_argument("--port", type=int, default=8892, help="Specify the port for FastAPI")
args = parser.parse_args()
# ===================== OCR配置 =====================
ocr_model = os.getenv("OCR_MODEL", "Qwen2.5-VL-7B-Instruct")
prompt_ocr = """
    请对以下图像进行识别（有印刷体和手写体，手写体如果出现模糊涂改请返回空）：
    注意：如果文本部分有划线、划掉或涂改，**请务必完全忽略这些部分**，并且**不做任何识别**。仅提取那些没有被划掉的、清晰可读的文本内容，确保输出结果只包含有效信息。
    规定：图片内容是什么就识别什么，不能自我发散（不能翻译或自我发挥）。对于数学公式，公式格式严格按照：$公式部分$。请返回提取结果。
"""
qwen_VL_url = os.getenv("OCR_HOST", 'http://192.168.4.22:9008') + "/v1/chat/completions"
headers = {"Content-Type": "application/json"}
