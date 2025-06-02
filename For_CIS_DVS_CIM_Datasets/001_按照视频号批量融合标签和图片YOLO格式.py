import os
import cv2


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
    frame_number = filename.split('_')[-1].split('.')[0]  # 从文件名中提取帧编号
    return video_id, camera_type, frame_number


# 加载所有label文件到字典中
def load_labels(label_dir):
    """
    遍历Label目录，加载所有标签文件到字典
    参数:
        label_dir (str): Label目录路径
    返回:
        dict: 键为(video_id, camera_type, frame_number)，值为标签列表
    """
    label_dict = {}
    for root, dirs, files in os.walk(label_dir):
        for file in files:
            if file.endswith('.txt'):
                label_path = os.path.join(root, file)
                video_id, camera_type, frame_number = parse_path(label_path)
                key = (video_id, camera_type, frame_number)
                with open(label_path, 'r') as f:
                    labels = []
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) == 5:  # YOLO标签应有5个值
                            try:
                                label = [float(p) for p in parts]  # 转换为浮点数
                                labels.append(label)
                            except ValueError:
                                print(f"警告: {label_path} 中的标签格式错误: {line}")
                    if labels:  # 只有非空标签列表才存入字典
                        label_dict[key] = labels
    return label_dict


# 在图片上绘制标签
def draw_labels(image, labels):
    """
    根据YOLO标签在图片上绘制边界框
    参数:
        image (numpy.ndarray): 输入图片
        labels (list): 标签列表，每个标签为[class_id, center_x, center_y, width, height]
    返回:
        numpy.ndarray: 绘制了边界框的图片
    """
    h, w = image.shape[:2]  # 获取图片高度和宽度
    for label in labels:
        class_id, center_x, center_y, width, height = label
        # 将归一化坐标转换为像素坐标
        x1 = int((center_x - width / 2) * w)
        y1 = int((center_y - height / 2) * h)
        x2 = int((center_x + width / 2) * w)
        y2 = int((center_y + height / 2) * h)
        # 绘制绿色边界框，厚度为2
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
    return image


# 处理单张图片
def process_image(image_path, label_dict, merge_dir, label_dir):
    """
    处理单张图片：读取、绘制标签（如果有）、保存，并打印标签文件信息
    参数:
        image_path (str): 图片路径
        label_dict (dict): 标签字典
        merge_dir (str): 输出目录
        label_dir (str): Label目录路径
    """
    video_id, camera_type, frame_number = parse_path(image_path)
    key = (video_id, camera_type, frame_number)

    # 构建标签文件的路径
    label_filename = os.path.basename(image_path).replace('.png', '.txt')
    label_path = os.path.join(label_dir, video_id, camera_type, label_filename)

    # 读取图片
    image = cv2.imread(image_path)
    if image is None:
        print(f"错误: 无法读取图片 {image_path}")
        return

    # 检查是否有标签
    if key in label_dict:
        labels = label_dict[key]
        image = draw_labels(image, labels)
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

    # 遍历Data目录，处理每张图片
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith('.png'):
                image_path = os.path.join(root, file)
                print("处理图片:", image_path)
                process_image(image_path, label_dict, merge_dir, label_dir)


# 运行程序
if __name__ == "__main__":
    # 设置目录路径
    data_dir = "Data"
    label_dir = "Label"
    merge_dir = "Merge"

    # 执行主函数
    main(data_dir, label_dir, merge_dir)
    print("处理完成，所有图片已保存至Merge目录")