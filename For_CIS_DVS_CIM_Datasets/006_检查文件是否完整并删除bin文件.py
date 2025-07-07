import os
from pathlib import Path


def get_folder_list(root_path):
    """获取根路径下的所有文件夹列表"""
    return [f for f in os.listdir(root_path) if os.path.isdir(os.path.join(root_path, f))]


def check_frame_continuity(files, prefix, suffix, path):
    """检查帧编号是否连续"""
    if not files:
        print(f"错误: 路径 {path} 下没有找到任何 {suffix} 文件")
        return False

    frame_numbers = []
    for f in files:
        if f.startswith(prefix) and f.endswith(suffix):
            try:
                frame_num = int(f[len(prefix):-len(suffix)])
                frame_numbers.append(frame_num)
            except ValueError:
                continue

    if not frame_numbers:
        print(f"错误: 路径 {path} 下没有符合格式的 {suffix} 文件")
        return False

    frame_numbers.sort()
    min_frame, max_frame = min(frame_numbers), max(frame_numbers)
    expected_frames = set(range(min_frame, max_frame + 1))
    actual_frames = set(frame_numbers)

    if expected_frames != actual_frames:
        missing_frames = expected_frames - actual_frames
        print(f"错误: 路径 {path} 下 {suffix} 文件帧编号不连续，缺失帧: {sorted(missing_frames)}")
        return False

    return True


def check_additional_files(video_id, base_path):
    """检查额外的四个文件"""
    # 检查 ApsEvsInfo.txt 和 DeviceCfg.txt
    txt_files = ["ApsEvsInfo.txt", "DeviceCfg.txt"]
    for txt_file in txt_files:
        txt_path = os.path.join(base_path, txt_file)
        if not os.path.exists(txt_path):
            print(f"错误: 路径 {txt_path} 不存在")

    # 检查 APS 下的 .bin 文件
    aps_bin_path = os.path.join(base_path, "APS", f"quadbayer_10bit_3264_2448_{video_id}.bin")
    if not os.path.exists(aps_bin_path):
        print(f"错误: 路径 {aps_bin_path} 不存在")

    # 检查 EVS 下的 .bin 文件
    evs_bin_path = os.path.join(base_path, "EVS", f"normal_v2_816_612_{video_id}.bin")
    if not os.path.exists(evs_bin_path):
        print(f"错误: 路径 {evs_bin_path} 不存在")

    return [os.path.join(base_path, f) for f in txt_files] + [aps_bin_path, evs_bin_path]


def check_aps_files(video_id, base_path):
    """检查APS相关路径的文件完整性"""
    aps_base = os.path.join(base_path, "APS", f"quadbayer_10bit_3264_2448_{video_id}")

    aps_png_path = os.path.join(aps_base, "aps_png")
    if not os.path.exists(aps_png_path):
        print(f"错误: 路径 {aps_png_path} 不存在")
        return False

    png_files = os.listdir(aps_png_path)
    prefix_png = "3264_2448_10_"
    check_frame_continuity(png_files, prefix_png, ".png", aps_png_path)

    aps_raw_path = os.path.join(aps_base, "aps_raw")
    if not os.path.exists(aps_raw_path):
        print(f"错误: 路径 {aps_raw_path} 不存在")
        return False

    raw_files = os.listdir(aps_raw_path)
    prefix_raw = "3264_2448_10_"
    check_frame_continuity(raw_files, prefix_raw, ".raw", aps_raw_path)

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

    evs_png_path = os.path.join(evs_base, "evs_png")
    if not os.path.exists(evs_png_path):
        print(f"错误: 路径 {evs_png_path} 不存在")
        return False

    png_files = os.listdir(evs_png_path)
    prefix_png = "816_612_8_"
    check_frame_continuity(png_files, prefix_png, ".png", evs_png_path)

    evs_raw_path = os.path.join(evs_base, "evs_raw")
    if not os.path.exists(evs_raw_path):
        print(f"错误: 路径 {evs_raw_path} 不存在")
        return False

    raw_files = os.listdir(evs_raw_path)
    prefix_raw = "816_612_8_"
    check_frame_continuity(raw_files, prefix_raw, ".raw", evs_raw_path)

    video_path = os.path.join(evs_base, "Video")
    if not os.path.exists(video_path):
        print(f"错误: 路径 {video_path} 不存在")
        return False

    expected_video = f"normal_v2_816_612_{video_id}_evs.avi"
    video_files = os.listdir(video_path)
    if expected_video not in video_files:
        print(f"错误: 路径 {video_path} 下缺少视频文件 {expected_video}")


def delete_additional_files(file_paths):
    """删除指定的文件"""
    for file_path in file_paths:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"已删除: {file_path}")
            except Exception as e:
                print(f"删除失败: {file_path}, 错误: {e}")
        else:
            print(f"文件不存在，无需删除: {file_path}")


def check_folders(root_path, folder_list):
    """检查指定文件夹列表下所有视频号的文件完整性，并收集需要删除的文件"""
    files_to_delete = []
    for folder in folder_list:
        folder_path = os.path.join(root_path, folder)
        if not os.path.exists(folder_path):
            print(f"错误: 文件夹 {folder_path} 不存在")
            continue

        print(f"\n正在检查文件夹: {folder}")
        for video_id in os.listdir(folder_path):
            video_path = os.path.join(folder_path, video_id)
            if os.path.isdir(video_path):
                print(f"  检查视频号: {video_id} (路径: {video_path})")
                # 检查额外的四个文件
                files_to_delete.extend(check_additional_files(video_id, video_path))
                # 检查APS和EVS文件
                check_aps_files(video_id, video_path)
                check_evs_files(video_id, video_path)
                print("-" * 50)

    return files_to_delete


def main():
    root_path = r"D:\数据集转换汇总"

    # 获取所有文件夹列表
    all_folders = get_folder_list(root_path)
    print("D:\数据集转换汇总 下的所有文件夹：")
    print(all_folders)

    # 指定要检查的文件夹
    folders_to_check =   ["跌倒", "跌倒检测", "跌倒检测-二楼", "跌倒检测-室外", "红桥学生的跌倒检测"]  # 用户可以修改

    print(f"\n将检查以下文件夹：{folders_to_check}")
    files_to_delete = check_folders(root_path, folders_to_check)

    # 询问是否删除
    if files_to_delete:
        print("\n检查完成，以下是找到的额外文件：")
        for f in files_to_delete:
            print(f"  {f}")
        response = input("\n是否要删除所有上述文件？(输入 'yes' 删除，其他跳过): ").strip().lower()
        if response == 'yes':
            delete_additional_files(files_to_delete)
        else:
            print("未删除任何文件")
    else:
        print("\n未找到任何额外文件")


if __name__ == "__main__":
    main()