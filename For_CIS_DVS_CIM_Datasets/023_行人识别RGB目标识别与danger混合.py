import os
import xml.etree.ElementTree as ET
import shutil
import chardet

# 定义路径
base_path = r"D:\数据集转换汇总\原始任务标签整理"
rgb_label_path = os.path.join(base_path, "行人识别RGB标签Yolov5已清洗")
aps_evs_path = os.path.join(base_path, "行人识别")
output_base_path = r"D:\数据集转换汇总\行人识别任务种类与danger合并"

# 确保输出目录存在
if not os.path.exists(output_base_path):
    os.makedirs(output_base_path)


def detect_encoding(file_path):
    """检测文件编码"""
    with open(file_path, 'rb') as f:
        raw_data = f.read(10000)  # 读取前10000字节以检测编码
        result = chardet.detect(raw_data)
        return result['encoding'] or 'utf-8'


def yolo_to_voc(yolo_line, width=3264, height=2448):
    """将 YOLO 格式转换为 VOC 格式的边界框"""
    parts = yolo_line.strip().split()
    if len(parts) != 5:
        return None
    _, center_x, center_y, w, h = map(float, parts)

    # 转换为像素坐标
    x_min = int((center_x - w / 2) * width)
    x_max = int((center_x + w / 2) * width)
    y_min = int((center_y - h / 2) * height)
    y_max = int((center_y + h / 2) * height)

    return x_min, y_min, x_max, y_max


def create_voc_object(xmin, ymin, xmax, ymax, name="danger"):
    """创建 VOC 格式的 object 节点"""
    obj = ET.Element("object")
    name_elem = ET.SubElement(obj, "name")
    name_elem.text = name
    pose = ET.SubElement(obj, "pose")
    pose.text = "Unspecified"
    truncated = ET.SubElement(obj, "truncated")
    truncated.text = "0"
    difficult = ET.SubElement(obj, "difficult")
    difficult.text = "0"
    bndbox = ET.SubElement(obj, "bndbox")
    ET.SubElement(bndbox, "xmin").text = str(xmin)
    ET.SubElement(bndbox, "ymin").text = str(ymin)
    ET.SubElement(bndbox, "xmax").text = str(xmax)
    ET.SubElement(bndbox, "ymax").text = str(ymax)
    return obj


def process_video_folder(video_id):
    """处理单个视频号文件夹"""
    # 输入路径
    rgb_video_path = os.path.join(rgb_label_path, video_id)
    aps_video_path = os.path.join(aps_evs_path, video_id, "aps")
    evs_video_path = os.path.join(aps_evs_path, video_id, "evs")

    # 输出路径
    output_video_path = os.path.join(output_base_path, video_id)
    output_aps_path = os.path.join(output_video_path, "aps")
    output_evs_path = os.path.join(output_video_path, "evs")

    # 创建输出目录
    os.makedirs(output_aps_path, exist_ok=True)
    os.makedirs(output_evs_path, exist_ok=True)

    # 处理 EVS 文件（直接复制，修改类别为 0）
    if os.path.exists(evs_video_path):
        for evs_file in os.listdir(evs_video_path):
            if evs_file.endswith(".txt"):
                input_evs_file = os.path.join(evs_video_path, evs_file)
                output_evs_file = os.path.join(output_evs_path, evs_file)

                try:
                    # 检测文件编码
                    encoding = detect_encoding(input_evs_file)
                    with open(input_evs_file, 'r', encoding=encoding) as f:
                        lines = f.readlines()

                    with open(output_evs_file, 'w', encoding='utf-8') as f:
                        for line in lines:
                            parts = line.strip().split()
                            if len(parts) == 5:
                                parts[0] = "0"  # 修改类别为 0
                                f.write(" ".join(parts) + "\n")
                except UnicodeDecodeError as e:
                    print(f"无法解码文件 {input_evs_file}: {e}")
                    continue
                except Exception as e:
                    print(f"处理文件 {input_evs_file} 时出错: {e}")
                    continue

    # 处理 APS 文件（转换为 VOC 格式并与 RGB 标签合并）
    if os.path.exists(aps_video_path) and os.path.exists(rgb_video_path):
        for aps_file in os.listdir(aps_video_path):
            if aps_file.endswith(".txt"):
                aps_file_path = os.path.join(aps_video_path, aps_file)
                rgb_file_name = aps_file.replace(".txt", ".xml")
                rgb_file_path = os.path.join(rgb_video_path, rgb_file_name)

                if os.path.exists(rgb_file_path):
                    try:
                        # 读取 XML 文件
                        tree = ET.parse(rgb_file_path)
                        root = tree.getroot()

                        # 读取 YOLO 格式的 APS 文件
                        encoding = detect_encoding(aps_file_path)
                        with open(aps_file_path, 'r', encoding=encoding) as f:
                            yolo_lines = f.readlines()

                        # 将 YOLO 格式转换为 VOC 格式并添加到 XML
                        for line in yolo_lines:
                            voc_box = yolo_to_voc(line)
                            if voc_box:
                                xmin, ymin, xmax, ymax = voc_box
                                danger_obj = create_voc_object(xmin, ymin, xmax, ymax)
                                root.append(danger_obj)

                        # 保存新的 XML 文件
                        output_xml_path = os.path.join(output_aps_path, rgb_file_name)
                        tree.write(output_xml_path, encoding='utf-8', xml_declaration=True)
                    except UnicodeDecodeError as e:
                        print(f"无法解码文件 {aps_file_path}: {e}")
                        continue
                    except Exception as e:
                        print(f"处理文件 {aps_file_path} 时出错: {e}")
                        continue


def main():
    """主函数，遍历所有视频号文件夹"""
    if not os.path.exists(rgb_label_path):
        print(f"RGB标签路径不存在: {rgb_label_path}")
        return

    # 获取所有视频号文件夹
    video_ids = [d for d in os.listdir(rgb_label_path) if os.path.isdir(os.path.join(rgb_label_path, d))]

    for video_id in video_ids:
        print(f"处理视频号: {video_id}")
        process_video_folder(video_id)

    print("处理完成！")


if __name__ == "__main__":
    main()