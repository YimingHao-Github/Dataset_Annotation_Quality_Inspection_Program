import os
import xml.etree.ElementTree as ET
from pathlib import Path


def get_all_classes(base_path):
    # 初始化类别集合
    classes = set()

    # 将路径转换为 Path 对象
    base_path = Path(base_path)

    # 遍历所有子目录（视频号目录）
    for video_dir in base_path.iterdir():
        if video_dir.is_dir():  # 确保是目录
            # 遍历目录下的所有 xml 文件
            for xml_file in video_dir.glob('*.xml'):
                try:
                    # 解析 XML 文件
                    tree = ET.parse(xml_file)
                    root = tree.getroot()

                    # 查找所有 object 标签中的 name 标签
                    for obj in root.findall('object'):
                        class_name = obj.find('name').text
                        if class_name:  # 确保类别名称不为空
                            classes.add(class_name)
                except ET.ParseError:
                    print(f"解析错误: {xml_file}")
                except Exception as e:
                    print(f"处理文件 {xml_file} 时出错: {e}")

    return classes


def main():
    # 指定基础路径
    base_path = r"D:\数据集转换汇总\行人识别RGB收集与整理\行人识别RGB标签Yolov5"

    # 获取所有类别
    all_classes = get_all_classes(base_path)

    # 打印结果
    print("所有标签文件中包含的类别：")
    if all_classes:
        for idx, class_name in enumerate(sorted(all_classes), 1):
            print(f"{idx}. {class_name}")
    else:
        print("未找到任何类别。")


if __name__ == "__main__":
    main()