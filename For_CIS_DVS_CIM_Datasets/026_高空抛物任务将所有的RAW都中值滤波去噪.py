import numpy as np
import os
import glob
from scipy.ndimage import median_filter
from tqdm import tqdm

# 参数设置
SRC_ROOT = r"E:\DatasetFor5Task\High-AltitudeThrowing"
DST_ROOT = r"D:\Denoising\High-AltitudeThrowing"
RESOLUTION = (612, 816)  # 高度 612，宽度 816
FILTER_SIZE = 3  # 中值滤波的核大小


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


def median_filter_cpu(data, filter_size):
    """使用 SciPy 进行中值滤波"""
    filtered = np.zeros_like(data)
    for value in [0, 1, 2]:
        mask = (data == value).astype(np.uint8)
        filtered_mask = median_filter(mask, size=filter_size)
        filtered[filtered_mask > 0] = value
    return filtered


def process_frame(src_path, dst_path, resolution, filter_size):
    """处理单个帧"""
    data = read_raw_file(src_path, resolution)
    filtered_data = median_filter_cpu(data, filter_size)
    write_raw_file(dst_path, filtered_data)


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
        all_files.extend([(src, os.path.join(DST_ROOT, os.path.relpath(src, SRC_ROOT))) for src in raw_files])

    # 使用 tqdm 显示进度条
    with tqdm(total=len(all_files), desc="处理帧", unit="frame", ncols=100) as pbar:
        for src_path, dst_path in all_files:
            pbar.set_postfix(file=os.path.basename(src_path))
            process_frame(src_path, dst_path, RESOLUTION, FILTER_SIZE)
            pbar.update(1)


if __name__ == "__main__":
    main()