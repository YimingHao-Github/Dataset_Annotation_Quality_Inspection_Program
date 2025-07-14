import os
import xml.etree.ElementTree as ET
from pathlib import Path
import shutil


def process_xml_file(input_path, output_path, valid_classes):
    """
    处理单个 XML 文件，保留指定类别，修改指定字段，并保存到新路径。

    Args:
        input_path: 输入 XML 文件路径
        output_path: 输出 XML 文件路径
        valid_classes: 保留的类别集合
    """
    try:
        # 解析 XML 文件
        tree = ET.parse(input_path)
        root = tree.getroot()

        # 修改 <folder> 字段，移除前缀
        folder_elem = root.find('folder')
        if folder_elem is not None:
            folder_text = folder_elem.text
            prefix = r"D:\PycharmProjects\yolov5\hymlabels\\"
            if folder_text.startswith(prefix):
                folder_elem.text = folder_text[len(prefix):]

        # 修改 <path> 字段，移除前缀
        path_elem = root.find('path')
        if path_elem is not None:
            path_text = path_elem.text
            if path_text.startswith(prefix):
                path_elem.text = path_text[len(prefix):]

        # 修改 <database> 字段
        database_elem = root.find('source/database')
        if database_elem is not None:
            database_elem.text = 'PedestrianDetection'

        # 获取所有 <object> 标签
        objects = root.findall('object')
        objects_to_remove = []

        # 标记需要删除的 <object>（不在 valid_classes 中的类别）
        for obj in objects:
            class_name = obj.find('name').text
            if class_name not in valid_classes:
                objects_to_remove.append(obj)

        # 删除不符合条件的 <object>
        for obj in objects_to_remove:
            root.remove(obj)

        # 如果还有有效的 <object>，保存修改后的 XML
        if len(root.findall('object')) > 0:
            # 确保输出目录存在
            output_path.parent.mkdir(parents=True, exist_ok=True)
            # 保存 XML 文件，保留原始格式
            tree.write(output_path, encoding='utf-8', xml_declaration=True)
            return True
        else:
            # 如果没有有效的 <object>，不保存文件
            return False

    except ET.ParseError:
        print(f"解析错误: {input_path}")
        return False
    except Exception as e:
        print(f"处理文件 {input_path} 时出错: {e}")
        return False


def clean_dataset(input_base_path, output_base_path, valid_classes):
    """
    遍历输入路径下的所有 XML 文件，处理并保存到输出路径。

    Args:
        input_base_path: 输入基础路径
        output_base_path: 输出基础路径
        valid_classes: 保留的类别集合
    """
    input_base_path = Path(input_base_path)
    output_base_path = Path(output_base_path)

    # 统计处理的 XML 文件数量
    processed_count = 0
    skipped_count = 0

    # 遍历所有子目录（视频号目录）
    for video_dir in input_base_path.iterdir():
        if video_dir.is_dir():
            # 构造对应的输出视频号目录
            relative_path = video_dir.relative_to(input_base_path)
            output_video_dir = output_base_path / relative_path

            # 遍历目录下的所有 XML 文件
            for xml_file in video_dir.glob('*.xml'):
                # 构造输出 XML 文件路径
                output_xml_path = output_video_dir / xml_file.name

                # 处理 XML 文件
                if process_xml_file(xml_file, output_xml_path, valid_classes):
                    processed_count += 1
                else:
                    skipped_count += 1

    print(f"处理完成：共处理 {processed_count} 个 XML 文件，跳过 {skipped_count} 个文件（无有效类别）。")


def main():
    # 输入和输出路径
    input_base_path = r"D:\数据集转换汇总\行人识别RGB收集与整理\跌倒检测RGB标签Yolov5"
    output_base_path = r"D:\数据集转换汇总\行人识别RGB收集与整理\跌倒检测RGB标签Yolov5已清洗"

    # 保留的类别
    valid_classes = {'person'}

    # 处理数据集
    clean_dataset(input_base_path, output_base_path, valid_classes)


if __name__ == "__main__":
    main()