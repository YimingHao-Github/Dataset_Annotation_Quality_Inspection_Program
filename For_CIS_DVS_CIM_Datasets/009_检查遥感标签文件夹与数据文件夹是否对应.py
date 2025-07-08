import os

# 定义路径
head_label_path = r"D:\数据集转换汇总\标签专用文件夹\标签整理2\0整理\遥感\head"
vehicle_label_path = r"D:\数据集转换汇总\标签专用文件夹\标签整理2\0整理\遥感\vehicle"
data_path = r"E:\五大任务数据集\遥感"

# 获取 head 标签（CSV 文件名，去掉 .csv 后缀）
head_labels = {os.path.splitext(f)[0] for f in os.listdir(head_label_path) if f.endswith('.csv')}

# 获取 vehicle 标签（文件夹名）
vehicle_labels = set(os.listdir(vehicle_label_path))

# 合并所有标签
all_labels = head_labels | vehicle_labels

# 获取数据本体（文件夹名）
data_folders = set(os.listdir(data_path))

# 找出有本体没标签的视频
data_no_label = data_folders - all_labels

# 找出有标签没本体的视频
label_no_data = all_labels - data_folders

# 打印结果
print("有本体但没有标签的视频：")
if data_no_label:
    for folder in sorted(data_no_label):
        print(folder)
else:
    print("无")

print("\n有标签但没有本体的视频：")
if label_no_data:
    for folder in sorted(label_no_data):
        print(folder)
else:
    print("无")