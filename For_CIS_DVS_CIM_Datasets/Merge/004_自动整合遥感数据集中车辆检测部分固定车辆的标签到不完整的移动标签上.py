import os
import glob
import xml.etree.ElementTree as ET
import numpy as np
import logging
from tqdm import tqdm

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def calculate_iou(box1, box2):
    """
    计算两个边界框的IOU
    box格式: [xmin, ymin, xmax, ymax]
    """
    x1, y1, x2, y2 = box1
    x1_, y1_, x2_, y2_ = box2

    # 计算交集的坐标
    xi1 = max(x1, x1_)
    yi1 = max(y1, y1_)
    xi2 = min(x2, x2_)
    yi2 = min(y2, y2_)

    # 计算交集面积
    inter_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)

    # 计算各自面积
    box1_area = (x2 - x1) * (y2 - y1)
    box2_area = (x2_ - x1_) * (y2_ - y1_)

    # 计算并集面积
    union_area = box1_area + box2_area - inter_area

    # 计算IOU
    iou = inter_area / union_area if union_area > 0 else 0
    return iou


def get_bndbox_coordinates(obj):
    """从object节点获取边界框坐标"""
    bndbox = obj.find('bndbox')
    return [
        int(bndbox.find('xmin').text),
        int(bndbox.find('ymin').text),
        int(bndbox.find('xmax').text),
        int(bndbox.find('ymax').text)
    ]


def add_fixed_vehicles(stationary_xml, fixed_xml, iou_threshold=0.5):
    """
    将固定小车标签添加到静止小车标签中，检查IOU避免重复
    返回是否修改了文件
    """
    try:
        # 解析XML
        stationary_tree = ET.parse(stationary_xml)
        fixed_tree = ET.parse(fixed_xml)

        stationary_root = stationary_tree.getroot()
        fixed_root = fixed_tree.getroot()

        # 获取所有固定小车的边界框
        fixed_boxes = []
        for obj in fixed_root.findall('object'):
            if obj.find('name').text == 'vehicle':
                fixed_boxes.append(get_bndbox_coordinates(obj))

        # 获取静止小车的边界框
        stationary_boxes = []
        for obj in stationary_root.findall('object'):
            if obj.find('name').text == 'vehicle':
                stationary_boxes.append(get_bndbox_coordinates(obj))

        modified = False
        # 检查每个固定小车边界框
        for fixed_obj in fixed_root.findall('object'):
            if fixed_obj.find('name').text != 'vehicle':
                continue

            fixed_box = get_bndbox_coordinates(fixed_obj)
            is_duplicate = False

            # 检查是否与现有边界框重叠
            for stat_box in stationary_boxes:
                iou = calculate_iou(fixed_box, stat_box)
                if iou > iou_threshold:
                    is_duplicate = True
                    logger.debug(f"Skipping duplicate box in {stationary_xml}: IOU={iou:.2f}")
                    break

            # 如果不是重复的，添加到静止标签中
            if not is_duplicate:
                stationary_root.append(fixed_obj)
                modified = True
                logger.debug(f"Added vehicle box to {stationary_xml}")

        # 如果有修改，保存文件
        if modified:
            stationary_tree.write(stationary_xml, encoding='utf-8', xml_declaration=True)
            logger.info(f"Updated {stationary_xml}")

        return modified

    except ET.ParseError as e:
        logger.error(f"XML parse error in {stationary_xml}: {e}")
        return False
    except Exception as e:
        logger.error(f"Error processing {stationary_xml}: {e}")
        return False


def main():
    # 路径配置
    fixed_xml_path = r"D:\Dataset\梁慧标签\2025030917474111_aps\label_png\固定小车标签\3264_2448_10_0000000000.xml"
    stationary_base_path = r"D:\Dataset\关于遥感的标签"

    # 检查固定小车标签文件是否存在
    if not os.path.exists(fixed_xml_path):
        logger.error(f"Fixed vehicle XML not found: {fixed_xml_path}")
        return

    # 查找所有视频文件夹
    video_folders = [f for f in glob.glob(os.path.join(stationary_base_path, "2025*"))
                     if os.path.isdir(f)]

    if not video_folders:
        logger.warning(f"No video folders found in {stationary_base_path}")
        return

    total_files = 0
    modified_files = 0

    # 遍历每个视频文件夹
    for video_folder in tqdm(video_folders, desc="Processing video folders"):
        # 查找所有XML文件
        xml_files = glob.glob(os.path.join(video_folder, "*.xml"))
        total_files += len(xml_files)

        for xml_file in xml_files:
            if add_fixed_vehicles(xml_file, fixed_xml_path):
                modified_files += 1

    logger.info(f"Processed {total_files} XML files, modified {modified_files} files")


if __name__ == "__main__":
    main()