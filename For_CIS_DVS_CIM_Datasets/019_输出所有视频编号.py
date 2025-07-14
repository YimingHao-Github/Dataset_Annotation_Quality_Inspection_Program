import os
from pathlib import Path


def get_video_ids(paths):
    """
    遍历指定路径，获取每个路径下的视频号（子文件夹名称）

    Args:
        paths: 要检查的路径列表

    Returns:
        dict: 路径到视频号列表的映射
    """
    result = {}

    for path in paths:
        path = Path(path)
        if not path.exists():
            result[path] = ["路径不存在"]
            continue

        # 获取所有子文件夹（视频号）
        video_ids = [d.name for d in path.iterdir() if d.is_dir()]
        result[path] = sorted(video_ids) if video_ids else ["无子文件夹"]

    return result


def print_video_ids(video_id_map):
    """
    打印每个路径及其视频号

    Args:
        video_id_map: 路径到视频号列表的映射
    """
    print("=== 各任务路径中的视频号 ===")
    for path, video_ids in video_id_map.items():
        print(f"\n路径: {path}")
        if video_ids == ["路径不存在"]:
            print("  - 路径不存在")
        elif video_ids == ["无子文件夹"]:
            print("  - 无子文件夹")
        else:
            for idx, video_id in enumerate(video_ids, 1):
                print(f"  {video_id}")


def main():
    # 指定的路径列表
    paths = [
        r"E:\五大任务数据集\FallDetection",
        r"E:\五大任务数据集\FatigueDetection\blink",
        r"E:\五大任务数据集\FatigueDetection\normal",
        r"E:\五大任务数据集\FatigueDetection\rubeyes",
        r"E:\五大任务数据集\FatigueDetection\yawn",
        r"E:\五大任务数据集\FatigueDetection\yawnandblink",
        r"E:\五大任务数据集\High-AltitudeThrowing",
        r"E:\五大任务数据集\PedestrianDetection",
        r"E:\五大任务数据集\RemoteSensing\person",
        r"E:\五大任务数据集\RemoteSensing\vehicle"
    ]

    # 获取视频号
    video_id_map = get_video_ids(paths)

    # 打印结果
    print_video_ids(video_id_map)


if __name__ == "__main__":
    main()