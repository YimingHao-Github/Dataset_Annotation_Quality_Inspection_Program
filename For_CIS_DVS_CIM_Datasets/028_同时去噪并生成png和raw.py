import numpy as np
import os
import glob
from scipy.ndimage import median_filter
from PIL import Image
from tqdm import tqdm

# 参数设置
SRC_ROOT = r"E:\DatasetFor5Task\High-AltitudeThrowing"
DST_ROOT = r"D:\Denoising2\High-AltitudeThrowing"
RESOLUTION = (612, 816)  # 高度 612，宽度 816
FILTER_SIZE = 2  # 中值滤波核大小，推荐 2 或 1（不滤波）以保留小型目标
THRESHOLD = 0.5  # 中值滤波后掩码的阈值，降低以保留更多细节（范围 0 到 1）


def read_raw_file(file_path, resolution):
    """读取 RAW 文件，返回 numpy 数组"""
    height, width = resolution
    with open(file_path, 'rb') as f:
        data = np.fromfile(f, dtype=np.uint8, count=height * width)
    return data.reshape(height, width)


def write_raw_file(file_path, data):
    """将数据保存为 RAW 文件"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    data.tofile(file_path)


def raw_to_png(data):
    """将 RAW 数据转换为 RGB 图像（0:黑, 1:红, 2:蓝）"""
    height, width = data.shape
    rgb_image = np.zeros((height, width, 3), dtype=np.uint8)
    rgb_image[data == 0] = [0, 0, 0]  # 黑色
    rgb_image[data == 1] = [255, 255, 255]  # 白色
    rgb_image[data == 2] = [ 255, 0, 0]  # 红色
    return rgb_image


def save_png_file(file_path, rgb_image):
    """将 RGB 图像保存为 PNG 文件"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    image = Image.fromarray(rgb_image, mode='RGB')
    image.save(file_path, 'PNG')


def median_filter_cpu(data, filter_size, threshold=0.5):
    """使用 SciPy 进行中值滤波，保留极性"""
    filtered = np.zeros_like(data)
    for value in [0, 1, 2]:
        mask = (data == value).astype(np.uint8)
        filtered_mask = median_filter(mask, size=filter_size, mode='constant')
        filtered[filtered_mask >= threshold] = value
    return filtered


def process_frame(src_path, raw_dst_path, png_dst_path, resolution, filter_size, threshold):
    """处理单个帧，保存 RAW 和 PNG"""
    # 读取 RAW 文件
    data = read_raw_file(src_path, resolution)

    # 应用中值滤波
    if filter_size > 1:  # 仅当 filter_size > 1 时应用滤波
        filtered_data = median_filter_cpu(data, filter_size, threshold)
    else:
        filtered_data = data  # 不滤波，直接使用原始数据

    # 保存去噪后的 RAW 文件
    write_raw_file(raw_dst_path, filtered_data)

    # 转换为 PNG 并保存
    rgb_image = raw_to_png(filtered_data)
    save_png_file(png_dst_path, rgb_image)


def main():
    # 查找所有视频文件夹
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
            # 构建目标路径
            relative_path = os.path.relpath(src_path, SRC_ROOT)
            raw_dst_path = os.path.join(DST_ROOT, relative_path)
            png_dst_path = os.path.join(DST_ROOT, relative_path.replace("evs_raw", "evs_png").replace(".raw", ".png"))
            all_files.append((src_path, raw_dst_path, png_dst_path))

    # 使用 tqdm 显示进度条
    with tqdm(total=len(all_files), desc="处理帧", unit="frame", ncols=100) as pbar:
        for src_path, raw_dst_path, png_dst_path in all_files:
            pbar.set_postfix(file=os.path.basename(src_path))
            process_frame(src_path, raw_dst_path, png_dst_path, RESOLUTION, FILTER_SIZE, THRESHOLD)
            pbar.update(1)


if __name__ == "__main__":
    main()