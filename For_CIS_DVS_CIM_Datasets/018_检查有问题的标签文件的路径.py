import os
import xml.etree.ElementTree as ET
from pathlib import Path


def find_xml_with_labels(xml_path, target_labels):
    """
    检查单个 XML 文件是否包含指定的标签

    Args:
        xml_path: XML 文件路径
        target_labels: 要查找的标签集合

    Returns:
        set: 该文件中包含的目标标签集合
    """
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        found_labels = set()

        for obj in root.findall('object'):
            class_name = obj.find('name').text
            if class_name in target_labels:
                found_labels.add(class_name)

        return found_labels
    except ET.ParseError:
        print(f"解析错误: {xml_path}")
        return set()
    except Exception as e:
        print(f"处理文件 {xml_path} 时出错: {e}")
        return set()


def find_error_label_files(video_ids, target_labels, base_path):
    """
    查找指定视频号中包含非目标标签的 XML 文件路径

    Args:
        video_ids: 视频号列表
        target_labels: 要查找的非目标标签集合
        base_path: 标签数据根路径
    """
    base_path = Path(base_path)

    # 存储包含非目标标签的文件路径
    error_files = []

    # 遍历指定视频号
    for video_id in video_ids:
        video_dir = base_path / video_id

        if not video_dir.exists():
            print(f"警告: 视频号 {video_id} 的标签文件夹不存在")
            continue

        # 检查 aps 和 evs 文件夹
        for sub_dir_name in ['aps', 'evs']:
            sub_dir = video_dir / sub_dir_name

            if sub_dir.exists():
                # 遍历所有 XML 文件
                for xml_file in sub_dir.glob('*.xml'):
                    found_labels = find_xml_with_labels(xml_file, target_labels)
                    if found_labels:
                        error_files.append((xml_file, found_labels))

    # 打印结果
    print("\n=== 包含非目标标签的 XML 文件路径 ===")
    if error_files:
        for xml_file, labels in error_files:
            print(f"文件: {xml_file}")
            print(f"  包含的非目标标签: {', '.join(labels)}")
    else:
        print("未找到任何包含非目标标签的文件。")


def main():
    # 输入路径
    base_path = r"D:\数据集转换汇总\标签专用文件夹\标签整理2\0整理\跌倒"

    # 指定的视频号和非目标标签
    video_ids = [
        "20250507152207934",
        "20250507152335423",
        "20250523143130190"
    ]
    target_labels = {"a", "dwdw", "www"}

    # 执行查找
    find_error_label_files(video_ids, target_labels, base_path)


if __name__ == "__main__":
    main()