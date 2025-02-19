# 使用 pgrep 查找进程 ID 并杀死
pic_ss=$(pgrep -f "ocr_start.py")
if [ -n "$pic_ss" ]; then
    echo "Killing process: $pic_ss"
    kill -9 $pic_ss
else
    echo "No process found"
fi

# 激活环境
source /opt/conda/etc/profile.d/conda.sh
conda activate my_yolo
# 运行
device=cpu # 指定设备
port=8899 # 端口号
nohup python ocr_start.py \
  --device ${device} \
  --port ${port} \
> ocr_start.log 2>&1 &
