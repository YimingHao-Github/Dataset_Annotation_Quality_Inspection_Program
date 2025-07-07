import os
from pathlib import Path


def get_folder_list(root_path):
    """获取根路径下的所有文件夹列表"""
    return [f for f in os.listdir(root_path) if os.path.isdir(os.path.join(root_path, f))]


def check_frame_continuity(files, prefix, suffix, path):
    """检查帧编号是否连续"""
    if not files:
        print(f"错误: {path} 下没有找到任何 {suffix} 文件")
        return False

    # 提取帧编号
    frame_numbers = []
    for f in files:
        if f.startswith(prefix) and f.endswith(suffix):
            try:
                frame_num = int(f[len(prefix):-len(suffix)])
                frame_numbers.append(frame_num)
            except ValueError:
                continue

    if not frame_numbers:
        print(f"错误: {path} 下没有符合格式的 {suffix} 文件")
        return False

    # 检查连续性
    frame_numbers.sort()
    min_frame, max_frame = min(frame_numbers), max(frame_numbers)
    expected_frames = set(range(min_frame, max_frame + 1))
    actual_frames = set(frame_numbers)

    if expected_frames != actual_frames:
        missing_frames = expected_frames - actual_frames
        print(f"错误: {path} 下 {suffix} 文件帧编号不连续，缺失帧: {sorted(missing_frames)}")
        return False

    return True


def check_aps_files(video_id, base_path):
    """检查APS相关路径的文件完整性"""
    aps_base = os.path.join(base_path, "APS", f"quadbayer_10bit_3264_2448_{video_id}")

    # 检查 aps_png
    aps_png_path = os.path.join(aps_base, "aps_png")
    if not os.path.exists(aps_png_path):
        print(f"错误: 路径 {aps_png_path} 不存在")
        return False

    png_files = os.listdir(aps_png_path)
    prefix_png = "3264_2448_10_"
    check_frame_continuity(png_files, prefix_png, ".png", aps_png_path)

    # 检查 aps_raw
    aps_raw_path = os.path.join(aps_base, "aps_raw")
    if not os.path.exists(aps_raw_path):
        print(f"错误: 路径 {aps_raw_path} 不存在")
        return False

    raw_files = os.listdir(aps_raw_path)
    prefix_raw = "3264_2448_10_"
    check_frame_continuity(raw_files, prefix_raw, ".raw", aps_raw_path)

    # 检查 Video 文件
    video_path = os.path.join(aps_base, "Video")
    if not os.path.exists(video_path):
        print(f"错误: 路径 {video_path} 不存在")
        return False

    expected_videos = [
        f"quadbayer_10bit_3264_2448_{video_id}_aps.avi",
        f"quadbayer_10bit_3264_2448_{video_id}_evs_aps.avi"
    ]
    video_files = os.listdir(video_path)
    for expected in expected_videos:
        if expected not in video_files:
            print(f"错误: 路径 {video_path} 下缺少视频文件 {expected}")


def check_evs_files(video_id, base_path):
    """检查EVS相关路径的文件完整性"""
    evs_base = os.path.join(base_path, "EVS", f"normal_v2_816_612_{video_id}")

    # 检查 evs_png
    evs_png_path = os.path.join(evs_base, "evs_png")
    if not os.path.exists(evs_png_path):
        print(f"错误: 路径 {evs_png_path} 不存在")
        return False

    png_files = os.listdir(evs_png_path)
    prefix_png = "816_612_8_"
    check_frame_continuity(png_files, prefix_png, ".png", evs_png_path)

    # 检查 evs_raw
    evs_raw_path = os.path.join(evs_base, "evs_raw")
    if not os.path.exists(evs_raw_path):
        print(f"错误: 路径 {evs_raw_path} 不存在")
        return False

    raw_files = os.listdir(evs_raw_path)
    prefix_raw = "816_612_8_"
    check_frame_continuity(raw_files, prefix_raw, ".raw", evs_raw_path)

    # 检查 Video 文件
    video_path = os.path.join(evs_base, "Video")
    if not os.path.exists(video_path):
        print(f"错误: 路径 {video_path} 不存在")
        return False

    expected_video = f"normal_v2_816_612_{video_id}_evs.avi"
    video_files = os.listdir(video_path)
    if expected_video not in video_files:
        print(f"错误: 路径 {video_path} 下缺少视频文件 {expected_video}")


def check_folders(root_path, folder_list):
    """检查指定文件夹列表下所有视频号的文件完整性"""
    for folder in folder_list:
        folder_path = os.path.join(root_path, folder)
        if not os.path.exists(folder_path):
            print(f"错误: 文件夹 {folder_path} 不存在")
            continue

        print(f"\n正在检查文件夹: {folder}")
        # 遍历文件夹下的每个视频号
        for video_id in os.listdir(folder_path):
            video_path = os.path.join(folder_path, video_id)
            if os.path.isdir(video_path):
                print(f"  检查视频号: {video_id} (路径: {video_path})")
                check_aps_files(video_id, video_path)
                check_evs_files(video_id, video_path)
                print("-" * 50)


def main():
    root_path = r"D:\数据集转换汇总"

    # 获取所有文件夹列表
    all_folders = get_folder_list(root_path)
    print("D:\数据集转换汇总 下的所有文件夹：")
    print(all_folders)

    # 示例：选择要检查的文件夹（你可以修改这个列表）
    folders_to_check = ["高空抛物-易华录", "高空抛物-教师公寓"]  # 用户可以替换为其他文件夹名

    print(f"\n将检查以下文件夹：{folders_to_check}")
    check_folders(root_path, folders_to_check)


if __name__ == "__main__":
    main()