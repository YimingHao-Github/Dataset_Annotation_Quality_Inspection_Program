import os

# 定义路径
label_path = r"D:\数据集转换汇总\标签专用文件夹\标签整理2\0整理\跌倒"
data_path = r"E:\五大任务数据集\跌倒检测"

# 获取文件夹列表
label_folders = set(os.listdir(label_path))
data_folders = set(os.listdir(data_path))

# 找出有本体没标签的视频
data_no_label = data_folders - label_folders

# 找出有标签没本体的视频
label_no_data = label_folders - data_folders

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