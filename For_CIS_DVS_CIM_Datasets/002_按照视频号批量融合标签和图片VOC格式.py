import os
import cv2
import xml.etree.ElementTree as ET

# 解析路径，提取视频编号、相机类型和帧编号
def parse_path(path):
    """
    从图片或标签路径中提取视频编号、相机类型和帧编号
    参数:
        path (str): 文件路径
    返回:
        tuple: (video_id, camera_type, frame_number)
    """
    parts = path.split(os.sep)
    video_id = parts[1]  # 第二部分是视频编号
    camera_type = parts[2].lower()  # 第三部分是相机类型，转为小写以保持一致
    filename = parts[-1]  # 最后一部分是文件名
    if filename.endswith('.xml'):
        frame_number = filename.split('_')[-1].split('.')[0]
    else:
        frame_number = filename.split('_')[-1].split('.')[0]
    return video_id, camera_type, frame_number

# 加载所有VOC XML标签文件到字典中
def load_labels(label_dir):
    """
    遍历Label目录，加载所有VOC XML标签文件到字典
    参数:
        label_dir (str): Label目录路径
    返回:
        dict: 键为(video_id, camera_type, frame_number)，值为对象列表
    """
    label_dict = {}
    for root, dirs, files in os.walk(label_dir):
        for file in files:
            if file.endswith('.xml'):
                label_path = os.path.join(root, file)
                video_id, camera_type, frame_number = parse_path(label_path)
                key = (video_id, camera_type, frame_number)
                tree = ET.parse(label_path)
                xml_root = tree.getroot()
                objects = []
                for obj in xml_root.findall('object'):
                    class_name = obj.find('name').text
                    bndbox = obj.find('bndbox')
                    xmin = int(bndbox.find('xmin').text)
                    ymin = int(bndbox.find('ymin').text)
                    xmax = int(bndbox.find('xmax').text)
                    ymax = int(bndbox.find('ymax').text)
                    objects.append({'class': class_name, 'bbox': [xmin, ymin, xmax, ymax]})
                if objects:
                    label_dict[key] = objects
    return label_dict

# 为所有类别生成颜色映射
def get_class_colors(label_dict):
    """
    为所有类别生成颜色映射
    参数:
        label_dict (dict): 标签字典
    返回:
        dict: 类别到颜色的映射
    """
    all_classes = set()
    for objects in label_dict.values():
        for obj in objects:
            all_classes.add(obj['class'])
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]
    class_colors = {}
    for i, cls in enumerate(all_classes):
        class_colors[cls] = colors[i % len(colors)]
    return class_colors

# 在图片上绘制VOC标签
def draw_labels(image, objects, class_colors):
    """
    根据VOC标签在图片上绘制边界框和类别名称
    参数:
        image (numpy.ndarray): 输入图片
        objects (list): 对象列表，每个对象为{'class': str, 'bbox': [xmin, ymin, xmax, ymax]}
        class_colors (dict): 类别到颜色的映射
    返回:
        numpy.ndarray: 绘制了边界框和类别的图片
    """
    for obj in objects:
        class_name = obj['class']
        xmin, ymin, xmax, ymax = obj['bbox']
        color = class_colors.get(class_name, (0, 255, 0))  # 默认绿色
        cv2.rectangle(image, (xmin, ymin), (xmax, ymax), color, 2)
        cv2.putText(image, class_name, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
    return image

# 处理单张图片
def process_image(image_path, label_dict, merge_dir, label_dir, class_colors):
    """
    处理单张图片：读取、绘制标签（如果有）、保存，并打印标签文件信息
    参数:
        image_path (str): 图片路径
        label_dict (dict): 标签字典
        merge_dir (str): 输出目录
        label_dir (str): Label目录路径
        class_colors (dict): 类别到颜色的映射
    """
    video_id, camera_type, frame_number = parse_path(image_path)
    key = (video_id, camera_type, frame_number)

    # 构建标签文件的路径（VOC为.xml文件）
    label_filename = os.path.basename(image_path).replace('.png', '.xml')
    label_path = os.path.join(label_dir, video_id, camera_type, label_filename)

    # 读取图片
    image = cv2.imread(image_path)
    if image is None:
        print(f"错误: 无法读取图片 {image_path}")
        return

    # 检查是否有标签
    if key in label_dict:
        objects = label_dict[key]
        image = draw_labels(image, objects, class_colors)
        print(f"已绘制标签: {label_path}")
    else:
        print(f"该图片没有标签文件: {image_path}")

    # 构造输出路径并保存
    output_dir = os.path.join(merge_dir, video_id, camera_type)
    os.makedirs(output_dir, exist_ok=True)  # 确保目录存在
    output_path = os.path.join(output_dir, os.path.basename(image_path))
    cv2.imwrite(output_path, image)

# 主函数
def main(data_dir, label_dir, merge_dir):
    """
    主函数：加载标签，处理所有图片并保存
    参数:
        data_dir (str): Data目录路径
        label_dir (str): Label目录路径
        merge_dir (str): Merge目录路径
    """
    # 加载所有标签
    label_dict = load_labels(label_dir)
    print(f"已加载 {len(label_dict)} 个标签文件")

    # 生成类别颜色映射
    class_colors = get_class_colors(label_dict)

    # 遍历Data目录，处理每张图片
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith('.png'):
                image_path = os.path.join(root, file)
                print("处理图片:", image_path)
                process_image(image_path, label_dict, merge_dir, label_dir, class_colors)

# 运行程序
if __name__ == "__main__":
    # 设置目录路径
    # 下面的这几个就是工程目录下的三个文件夹，也就是相对路径
    data_dir = r"D:\Dataset\CIS_Network_Integration\Datas"
    label_dir = r"D:\Dataset\CIS_Network_Integration\Labels"
    merge_dir = "Merge"

    # 执行主函数
    main(data_dir, label_dir, merge_dir)
    print("处理完成，所有图片已保存至Merge目录")