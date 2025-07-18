import numpy as np
import os
import glob
from PIL import Image
from tqdm import tqdm

# 参数设置
SRC_ROOT = r"D:\Denoising\High-AltitudeThrowing"
DST_ROOT = r"D:\Denoising\High-AltitudeThrowing"
RESOLUTION = (612, 816)  # 高度 612，宽度 816


def read_raw_file(file_path, resolution):
    """读取 RAW 文件，返回 numpy 数组"""
    height, width = resolution
    with open(file_path, 'rb') as f:
        data = np.fromfile(f, dtype=np.uint8, count=height * width)
    return data.reshape(height, width)


def raw_to_png(data):
    """将 RAW 数据转换为 RGB 图像（0:黑, 1:红, 2:蓝）"""
    height, width = data.shape
    rgb_image = np.zeros((height, width, 3), dtype=np.uint8)

    # 颜色映射
    rgb_image[data == 0] = [0, 0, 0]  # 黑色
    rgb_image[data == 1] = [255, 0, 0]  # 红色
    rgb_image[data == 2] = [0, 0, 255]  # 蓝色

    return rgb_image


def save_png_file(file_path, rgb_image):
    """将 RGB 图像保存为 PNG 文件"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    image = Image.fromarray(rgb_image, mode='RGB')
    image.save(file_path, 'PNG')


def main():
    # 查找所有视频文件夹中的 RAW 文件
    video_dirs = glob.glob(os.path.join(SRC_ROOT, "*"))

    # 统计所有待处理的文件
    all_files = []
    for video_dir in video_dirs:
        if not os.path.isdir(video_dir):
            continue
        video_id = os.path.basename(video_dir)
        raw_dir = os.path.join(video_dir, "EVS", f"normal_v2_816_612_{video_id}", "evs_raw")
        if not os.path.exists(raw_dir):
            continue
        raw_files = glob.glob(os.path.join(raw_dir, "*.raw"))
        for src_path in raw_files:
            # 构建目标 PNG 路径
            relative_path = os.path.relpath(src_path, SRC_ROOT)
            png_path = os.path.join(DST_ROOT, relative_path.replace("evs_raw", "evs_png").replace(".raw", ".png"))
            all_files.append((src_path, png_path))

    # 使用 tqdm 显示进度条
    with tqdm(total=len(all_files), desc="转换 PNG", unit="frame", ncols=100) as pbar:
        for src_path, dst_path in all_files:
            pbar.set_postfix(file=os.path.basename(src_path))
            # 读取 RAW 文件
            data = read_raw_file(src_path, RESOLUTION)
            # 转换为 RGB 图像
            rgb_image = raw_to_png(data)
            # 保存为 PNG
            save_png_file(dst_path, rgb_image)
            pbar.update(1)


if __name__ == "__main__":
    main()