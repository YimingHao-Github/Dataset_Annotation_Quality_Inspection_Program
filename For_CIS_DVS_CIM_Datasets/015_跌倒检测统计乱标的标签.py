import os
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import defaultdict


def parse_xml_classes(xml_path):
    """解析单个 XML 文件，提取所有类别及其出现次数"""
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        class_counts = defaultdict(int)
        for obj in root.findall('object'):
            class_name = obj.find('name').text
            if class_name:
                class_counts[class_name] += 1
        return class_counts
    except ET.ParseError:
        print(f"解析错误: {xml_path}")
        return defaultdict(int)
    except Exception as e:
        print(f"处理文件 {xml_path} 时出错: {e}")
        return defaultdict(int)


def check_non_target_classes(video_base_path, label_base_path, target_classes):
    """
    检查所有视频的标签，找出包含非目标类别的视频，并统计非目标类别的出现次数

    Args:
        video_base_path: 视频数据根路径 (E:\五大任务数据集\FallDetection\)
        label_base_path: 标签数据根路径 (D:\数据集转换汇总\标签专用文件夹\标签整理2\0整理\跌倒\)
        target_classes: 目标类别集合，需保留的类别
    """
    video_base_path = Path(video_base_path)
    label_base_path = Path(label_base_path)

    # 非目标类别统计，结构：{video_id: {'aps': {class: count}, 'evs': {class: count}}}
    non_target_stats = defaultdict(lambda: {'aps': defaultdict(int), 'evs': defaultdict(int)})

    # 遍历标签根路径下的所有视频号文件夹
    for label_dir in label_base_path.iterdir():
        if label_dir.is_dir():
            video_id = label_dir.name  # 视频号，例如 20250308115805125

            # 检查对应的视频文件夹是否存在
            video_dir = video_base_path / video_id
            if not video_dir.exists():
                print(f"警告: 视频号 {video_id} 有标签但无视频源")
                continue

            # 检查 aps 和 evs 文件夹
            aps_dir = label_dir / 'aps'
            evs_dir = label_dir / 'evs'

            # 处理 APS 标签
            if aps_dir.exists():
                for xml_file in aps_dir.glob('*.xml'):
                    class_counts = parse_xml_classes(xml_file)
                    for class_name, count in class_counts.items():
                        if class_name not in target_classes:
                            non_target_stats[video_id]['aps'][class_name] += count

            # 处理 EVS 标签
            if evs_dir.exists():
                for xml_file in evs_dir.glob('*.xml'):
                    class_counts = parse_xml_classes(xml_file)
                    for class_name, count in class_counts.items():
                        if class_name not in target_classes:
                            non_target_stats[video_id]['evs'][class_name] += count

    # 打印结果
    print("\n=== 包含非目标类别的视频及其类别出现次数 ===")
    if not non_target_stats:
        print("所有视频的标签均只包含目标类别（stand, sit, lie, kneel）。")
        return

    for video_id in sorted(non_target_stats.keys()):
        aps_counts = non_target_stats[video_id]['aps']
        evs_counts = non_target_stats[video_id]['evs']

        # 检查是否有非目标类别
        has_non_target = any(aps_counts.values()) or any(evs_counts.values())
        if not has_non_target:
            continue

        print(f"\n视频号: {video_id}")

        # 打印 APS 中的非目标类别
        if aps_counts:
            print("  APS 标签中的非目标类别：")
            for class_name, count in sorted(aps_counts.items()):
                if count > 0:
                    print(f"    - {class_name}: {count} 次")
        else:
            print("  APS 标签中无非目标类别")

        # 打印 EVS 中的非目标类别
        if evs_counts:
            print("  EVS 标签中的非目标类别：")
            for class_name, count in sorted(evs_counts.items()):
                if count > 0:
                    print(f"    - {class_name}: {count} 次")
        else:
            print("  EVS 标签中无非目标类别")


def main():
    # 输入路径
    video_base_path = r"E:\五大任务数据集\FallDetection"
    label_base_path = r"D:\数据集转换汇总\标签专用文件夹\标签整理2\0整理\跌倒"

    # 目标类别
    target_classes = {'stand', 'sit', 'lie', 'kneel'}

    # 执行检查
    check_non_target_classes(video_base_path, label_base_path, target_classes)


if __name__ == "__main__":
    main()