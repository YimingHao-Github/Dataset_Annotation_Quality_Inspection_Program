import os
from pathlib import Path
import re


def find_consecutive_ranges(numbers):
    """将离散的数字整理为连续的范围，如 [45, 46, 47, 50, 51] -> ['45-47', '50-51']"""
    if not numbers:
        return []
    numbers = sorted(numbers)
    ranges = []
    start = numbers[0]
    prev = numbers[0]

    for num in numbers[1:] + [None]:
        if num is None or num != prev + 1:
            if start == prev:
                ranges.append(str(start))
            else:
                ranges.append(f"{start}-{prev}")
            start = num
        prev = num if num is not None else prev

    return ranges


def check_dataset_integrity(path1, path2):
    # 路径一：E:\DatasetFor5Task\High-AltitudeThrowing\
    # 路径二：D:\数据集转换汇总\原始任务标签整理\高空抛物\
    path1 = Path(path1)
    path2 = Path(path2)

    # 获取路径一下的所有视频号
    video_numbers = [d.name for d in path1.iterdir() if d.is_dir() and d.name.isdigit()]

    print("开始检查数据集完整性...")
    print("=" * 50)

    # 首先检查完全没有标签文件的视频号
    print("检查完全没有标签文件的视频号：")
    no_label_videos = []
    for video_num in video_numbers:
        path2_video = path2 / video_num / "evs"
        if not path2_video.exists() or not any(path2_video.glob("*.txt")):
            no_label_videos.append(video_num)

    if no_label_videos:
        print(f"以下视频号完全没有标签文件：{', '.join(no_label_videos)}")
    else:
        print("所有视频号都有标签文件。")
    print("=" * 50)

    # 检查每个视频号的标签连续性
    print("检查标签文件的连续性：")
    for video_num in video_numbers:
        # 路径二对应的视频文件夹
        path2_video = path2 / video_num / "evs"

        # 检查路径二是否存在对应视频号的文件夹
        if not path2_video.exists():
            continue  # 已在上一步报告缺失文件夹

        # 获取路径一中该视频的帧文件
        path1_frames_dir = path1 / video_num / "EVS" / f"normal_v2_816_612_{video_num}" / "evs_png"
        if not path1_frames_dir.exists():
            print(f"视频号 {video_num} 在路径一中缺少帧文件夹 {path1_frames_dir}！")
            continue

        # 获取所有帧文件
        frame_files = sorted([f.name for f in path1_frames_dir.glob("*.png")])
        if not frame_files:
            print(f"视频号 {video_num} 在路径一的帧文件夹 {path1_frames_dir} 中没有帧文件！")
            continue

        # 提取帧编号
        frame_numbers = []
        for f in frame_files:
            match = re.match(r"816_612_8_(\d+)\.png", f)
            if match:
                frame_numbers.append(int(match.group(1)))

        if not frame_numbers:
            print(f"视频号 {video_num} 的帧文件名格式不正确！")
            continue

        # 获取路径二中的标签文件
        path2_labels = sorted([f.name for f in path2_video.glob("*.txt")])
        if not path2_labels:
            continue  # 已在上一步报告无标签文件

        # 提取标签文件的帧编号
        label_numbers = []
        for f in path2_labels:
            match = re.match(r"816_612_8_(\d+)\.txt", f)
            if match:
                label_numbers.append(int(match.group(1)))

        if not label_numbers:
            print(f"视频号 {video_num} 的标签文件名格式不正确！")
            continue

        # 检查标签文件的连续性
        if label_numbers:
            min_label = min(label_numbers)
            max_label = max(label_numbers)
            expected_labels = set(range(min_label, max_label + 1))
            actual_labels = set(label_numbers)
            missing_labels = expected_labels - actual_labels

            if missing_labels:
                # 找到连续的标签范围
                present_ranges = find_consecutive_ranges(actual_labels)
                missing_ranges = find_consecutive_ranges(missing_labels)
                print(f"视频号 {video_num} 的标签文件：")
                print(f"  连续部分：{', '.join(present_ranges) if present_ranges else '无连续范围'}")
                print(f"  缺失的帧编号：{', '.join(missing_ranges) if missing_ranges else '无'}")
            else:
                print(f"视频号 {video_num} 的标签文件连续性检查通过。")

    print("=" * 50)
    print("检查完成！")


# 设置路径
path1 = r"E:\DatasetFor5Task\High-AltitudeThrowing"
path2 = r"D:\数据集转换汇总\原始任务标签整理\高空抛物"

# 运行检查
check_dataset_integrity(path1, path2)