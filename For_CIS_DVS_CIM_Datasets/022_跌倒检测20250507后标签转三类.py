import os
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime

# 定义输入和输出路径
input_root = r"D:\数据集转换汇总\原始任务标签整理\跌倒"
output_root = r"D:\数据集转换汇总\跌倒检测任务所有标签转三类"

# 定义日期范围
start_date = datetime.strptime("20250507", "%Y%m%d")
end_date = datetime.strptime("20250714", "%Y%m%d")

# 定义标签映射规则
label_mapping = {
    "crawl": "fallen",
    "lie": "fallen",
    "kneel": "falling",
    "sit": "falling",
    "stand": "notfalling"
}

def is_date_in_range(video_id):
    """检查视频号的日期是否在指定范围内"""
    try:
        # 提取视频号中的日期部分（前8位）
        date_str = video_id[:8]
        video_date = datetime.strptime(date_str, "%Y%m%d")
        return start_date <= video_date <= end_date
    except ValueError:
        print(f"视频号 {video_id} 的日期格式无效，跳过")
        return False

def process_xml_file(input_path, output_path):
    """处理单个 XML 文件，替换标签名称并保存到新路径"""
    try:
        # 解析 XML 文件
        tree = ET.parse(input_path)
        root = tree.getroot()

        # 修改 object 标签中的 name 字段
        for obj in root.findall('object'):
            name = obj.find('name')
            if name is not None and name.text in label_mapping:
                name.text = label_mapping[name.text]

        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # 保存修改后的 XML 文件
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
        print(f"已处理并保存: {output_path}")
    except Exception as e:
        print(f"处理文件 {input_path} 时出错: {e}")

def main():
    # 遍历输入根目录下的视频号文件夹
    for video_id in os.listdir(input_root):
        video_path = os.path.join(input_root, video_id)
        # 确保是目录且日期在范围内
        if os.path.isdir(video_path) and is_date_in_range(video_id):
            # 遍历视频号文件夹下的子目录（aps 和 evs）
            for sub_dir in ['aps', 'evs']:
                sub_dir_path = os.path.join(video_path, sub_dir)
                if os.path.exists(sub_dir_path):
                    # 遍历子目录中的所有 XML 文件
                    for root_dir, _, files in os.walk(sub_dir_path):
                        for file in files:
                            if file.endswith('.xml'):
                                # 构造输入文件的完整路径
                                input_file = os.path.join(root_dir, file)

                                # 构造输出文件的完整路径
                                relative_path = os.path.relpath(root_dir, input_root)
                                output_file = os.path.join(output_root, relative_path, file)

                                # 处理 XML 文件
                                process_xml_file(input_file, output_file)
        else:
            if os.path.isdir(video_path):
                print(f"视频号 {video_id} 的日期不在20250507-20250714范围内，跳过")

if __name__ == "__main__":
    # 确保输出根目录存在
    os.makedirs(output_root, exist_ok=True)
    main()