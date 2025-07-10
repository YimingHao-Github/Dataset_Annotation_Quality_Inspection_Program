import os
import xml.etree.ElementTree as ET
from pathlib import Path


def replace_labels_in_xml(xml_path, output_path, illegal_label, legal_label):
    """
    处理单个 XML 文件，将指定的非法标签替换为合法标签，并保存到新路径

    Args:
        xml_path: 输入 XML 文件路径
        output_path: 输出 XML 文件路径
        illegal_label: 要替换的非法标签
        legal_label: 替换为的合法标签

    Returns:
        int: 该文件中替换的标签数量
    """
    try:
        # 解析 XML 文件
        tree = ET.parse(xml_path)
        root = tree.getroot()

        # 统计替换数量
        replace_count = 0

        # 查找所有 object 标签
        for obj in root.findall('object'):
            class_name_elem = obj.find('name')
            if class_name_elem is not None and class_name_elem.text == illegal_label:
                class_name_elem.text = legal_label
                replace_count += 1

        # 如果有替换，保存修改后的 XML
        if replace_count > 0:
            # 确保输出目录存在
            output_path.parent.mkdir(parents=True, exist_ok=True)
            # 保存 XML 文件，保留原始格式
            tree.write(output_path, encoding='utf-8', xml_declaration=True)

        return replace_count

    except ET.ParseError:
        print(f"解析错误: {xml_path}")
        return 0
    except Exception as e:
        print(f"处理文件 {xml_path} 时出错: {e}")
        return 0


def replace_labels_in_video(video_id, illegal_label, legal_label, input_base_path, output_base_path):
    """
    处理指定视频号的标签文件，将非法标签替换为合法标签

    Args:
        video_id: 视频号（例如 20250308115805125）
        illegal_label: 要替换的非法标签
        legal_label: 替换为的合法标签
        input_base_path: 输入标签根路径
        output_base_path: 输出标签根路径
    """
    input_base_path = Path(input_base_path)
    output_base_path = Path(output_base_path)

    # 构造输入和输出视频号目录
    input_video_dir = input_base_path / video_id
    output_video_dir = output_base_path / video_id

    # 检查输入目录是否存在
    if not input_video_dir.exists():
        print(f"错误: 视频号 {video_id} 的标签文件夹不存在")
        return

    # 统计总替换数量
    total_replace_count = 0

    # 处理 aps 和 evs 文件夹
    for sub_dir_name in ['aps', 'evs']:
        input_sub_dir = input_video_dir / sub_dir_name
        output_sub_dir = output_video_dir / sub_dir_name

        if input_sub_dir.exists():
            sub_dir_replace_count = 0
            # 遍历子目录中的所有 XML 文件
            for xml_file in input_sub_dir.glob('*.xml'):
                output_xml_path = output_sub_dir / xml_file.name
                replace_count = replace_labels_in_xml(xml_file, output_xml_path, illegal_label, legal_label)
                sub_dir_replace_count += replace_count

            if sub_dir_replace_count > 0:
                print(
                    f"在 {sub_dir_name} 文件夹中替换了 {sub_dir_replace_count} 个 '{illegal_label}' 为 '{legal_label}'")

            total_replace_count += sub_dir_replace_count

    # 打印总结
    if total_replace_count > 0:
        print(f"\n视频号 {video_id} 共替换了 {total_replace_count} 个 '{illegal_label}' 为 '{legal_label}'")
    else:
        print(f"\n视频号 {video_id} 中未找到任何 '{illegal_label}' 标签")


def main():
    # 输入和输出路径
    input_base_path = r"D:\数据集转换汇总\标签专用文件夹\标签整理2\0整理\跌倒"
    output_base_path = r"D:\数据集转换汇总\标签专用文件夹\标签整理2\0整理\跌倒"

    # 用户指定的参数（可根据需要修改）
    video_id = "20250523143526827"  # 视频号
    illegal_label = "knee"  # 要替换的非法标签
    legal_label = "kneel"  # 替换为的合法标签

    # 执行替换
    replace_labels_in_video(video_id, illegal_label, legal_label, input_base_path, output_base_path)


if __name__ == "__main__":
    main()