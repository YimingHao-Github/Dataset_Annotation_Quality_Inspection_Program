import os
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import defaultdict
import random


def parse_xml_classes(xml_path, video_id, sub_dir_type, video_base_path):
    """解析单个 XML 文件，提取类别名称及对应的图片路径"""
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        class_image_pairs = []

        # 获取图片文件名（假设 XML 文件中有 <filename> 标签，或者通过 xml 文件名推导）
        xml_filename = Path(xml_path).stem  # 例如 frame_001
        # 构造对应的图片路径
        if sub_dir_type == 'aps':
            image_dir = video_base_path / video_id / 'APS' / f'normal_v2_816_612_{video_id}' / 'aps_png'
        else:  # evs
            image_dir = video_base_path / video_id / 'EVS' / f'normal_v2_816_612_{video_id}' / 'evs_png'

        # 假设图片文件名与 XML 文件名一致（去掉 .xml 后缀，添加 .png）
        image_path = image_dir / f"{xml_filename}.png"

        # 检查图片文件是否存在
        if not image_path.exists():
            # print(f"图片文件不存在: {image_path}")
            return []

        for obj in root.findall('object'):
            class_name = obj.find('name').text
            if class_name:
                class_image_pairs.append((class_name, str(image_path)))
        return class_image_pairs
    except ET.ParseError:
        print(f"解析错误: {xml_path}")
        return []
    except Exception as e:
        print(f"处理文件 {xml_path} 时出错: {e}")
        return []


def check_video_labels(video_base_path, label_base_path):
    """
    检查所有视频的标签情况，统计类别，并为每个类别随机抽取 20 个图片路径

    Args:
        video_base_path: 视频数据根路径 (E:\DatasetFor5Task\FallDetection\)
        label_base_path: 标签数据根路径 (D:\数据集转换汇总\标签专用文件夹\标签整理2\0整理\跌倒\)
    """
    video_base_path = Path(video_base_path)
    label_base_path = Path(label_base_path)

    # 存储所有类别及其对应的图片路径
    class_to_images = defaultdict(list)

    # 统计信息（保留原功能）
    no_label_videos = []
    missing_aps_evs = []
    label_no_video = []

    # 遍历视频根路径下的所有视频号文件夹
    for video_dir in video_base_path.iterdir():
        if video_dir.is_dir():
            video_id = video_dir.name

            # 构造对应的标签文件夹路径
            label_dir = label_base_path / video_id

            # 1. 检查是否有标签文件夹
            if not label_dir.exists():
                no_label_videos.append(video_id)
                continue

            # 2. 检查 APS 和 EVS 文件夹
            aps_dir = label_dir / 'aps'
            evs_dir = label_dir / 'evs'

            has_aps = aps_dir.exists() and any(aps_dir.glob('*.xml'))
            has_evs = evs_dir.exists() and any(evs_dir.glob('*.xml'))

            if not (has_aps and has_evs):
                status = []
                if not has_aps:
                    status.append("缺少 APS 标签")
                if not has_evs:
                    status.append("缺少 EVS 标签")
                missing_aps_evs.append(f"{video_id}: {', '.join(status)}")

            # 3. 统计 APS 和 EVS 标签中的类别及其图片路径
            for sub_dir, sub_dir_type in [(aps_dir, 'aps'), (evs_dir, 'evs')]:
                if sub_dir.exists():
                    for xml_file in sub_dir.glob('*.xml'):
                        class_image_pairs = parse_xml_classes(xml_file, video_id, sub_dir_type, video_base_path)
                        for class_name, image_path in class_image_pairs:
                            class_to_images[class_name].append(image_path)

            # 4. 检查视频源是否存在
            evs_video_dir = video_dir / 'EVS' / f'normal_v2_816_612_{video_id}' / 'evs_png'
            aps_video_dir = video_dir / 'APS' / f'normal_v2_816_612_{video_id}' / 'aps_png'

            has_evs_video = evs_video_dir.exists() and any(evs_video_dir.glob('*.png'))
            has_aps_video = aps_video_dir.exists() and any(aps_video_dir.glob('*.png'))

            if (has_aps or has_evs) and not (has_evs_video or has_aps_video):
                label_no_video.append(video_id)

    # 5. 检查标签文件夹中有无对应的视频文件夹
    for label_dir in label_base_path.iterdir():
        if label_dir.is_dir():
            video_id = label_dir.name
            video_dir = video_base_path / video_id
            if not video_dir.exists():
                label_no_video.append(video_id)

    # 打印结果
    print("\n=== 统计结果 ===")

    # 打印所有类别
    print("\n所有标签文件中包含的类别：")
    all_classes = sorted(class_to_images.keys())
    if all_classes:
        for idx, class_name in enumerate(all_classes, 1):
            print(f"{idx}. {class_name}")
    else:
        print("未找到任何类别。")

    # 打印每个类别随机抽取的 20 个图片路径
    print("\n每个类别随机抽取的 20 个图片路径：")
    for class_name in all_classes:
        print(f"\n类别: {class_name}")
        images = class_to_images[class_name]
        # 随机抽取 20 个图片路径（若不足 20 个，则返回所有）
        selected_images = random.sample(images, min(20, len(images)))
        if selected_images:
            for idx, image_path in enumerate(selected_images, 1):
                print(f"{idx}. {image_path}")
        else:
            print("无可用图片路径。")

    # 打印没有标签的视频
    print("\n没有标签文件夹的视频：")
    if no_label_videos:
        for video_id in no_label_videos:
            print(f"- {video_id}")
    else:
        print("所有视频均有标签文件夹。")

    # 打印缺少 APS 或 EVS 的视频
    print("\n缺少 APS 或 EVS 标签的视频：")
    if missing_aps_evs:
        for status in missing_aps_evs:
            print(f"- {status}")
    else:
        print("所有视频的标签文件夹均包含 APS 和 EVS。")

    # 打印有标签但无视频源的视频
    print("\n有标签但无视频源的视频：")
    if label_no_video:
        for video_id in label_no_video:
            print(f"- {video_id}")
    else:
        print("所有标签均有对应的视频源。")


def main():
    # 输入路径
    video_base_path = r"E:\DatasetFor5Task\FallDetection"
    label_base_path = r"D:\数据集转换汇总\原始任务标签整理\跌倒"

    # 设置随机种子以确保可重复性（可选）
    random.seed(42)

    # 执行检查
    check_video_labels(video_base_path, label_base_path)


if __name__ == "__main__":
    main()