import os

# 定义路径
txt_path = r"D:\PycharmProjects\Dataset_Annotation_Quality_Inspection_Program\For_CIS_DVS_CIM_Datasets\行人识别.txt"
folder_path = r"E:\五大任务数据集\行人识别"

# 读取txt文件中的视频编号
def read_video_ids_from_txt(txt_file):
    video_ids = set()
    try:
        with open(txt_file, 'r', encoding='utf-8') as f:
            for line in f:
                video_id = line.strip()
                if video_id:  # 确保不是空行
                    video_ids.add(video_id)
        return video_ids
    except Exception as e:
        print(f"读取txt文件出错: {e}")
        return set()

# 获取文件夹中的视频编号
def get_video_ids_from_folders(folder_path):
    video_ids = set()
    try:
        for folder_name in os.listdir(folder_path):
            full_path = os.path.join(folder_path, folder_name)
            if os.path.isdir(full_path):  # 确保是文件夹
                video_ids.add(folder_name)
        return video_ids
    except Exception as e:
        print(f"读取文件夹出错: {e}")
        return set()

# 主函数
def compare_video_ids():
    # 读取txt文件和文件夹中的视频编号
    txt_video_ids = read_video_ids_from_txt(txt_path)
    folder_video_ids = get_video_ids_from_folders(folder_path)

    # 找出差异
    in_txt_not_in_folder = txt_video_ids - folder_video_ids
    in_folder_not_in_txt = folder_video_ids - txt_video_ids

    # 输出结果
    print("在txt文件中但不在文件夹中的视频编号：")
    if in_txt_not_in_folder:
        for vid in sorted(in_txt_not_in_folder):
            print(vid)
    else:
        print("无")

    print("\n在文件夹中但不在txt文件中的视频编号：")
    if in_folder_not_in_txt:
        for vid in sorted(in_folder_not_in_txt):
            print(vid)
    else:
        print("无")

# 运行程序
if __name__ == "__main__":
    compare_video_ids()