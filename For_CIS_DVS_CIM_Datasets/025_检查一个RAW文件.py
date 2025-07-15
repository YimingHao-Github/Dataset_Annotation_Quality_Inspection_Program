import numpy as np
from PIL import Image


def read_raw_to_png(raw_file_path, output_png_path, width=816, height=612):
    # 尝试不同的位深度 (uint8, uint16, uint32)
    for dtype in [np.uint8, np.uint16, np.uint32]:
        try:
            # 计算文件大小
            file_size = width * height * np.dtype(dtype).itemsize
            # 读取RAW文件
            with open(raw_file_path, 'rb') as f:
                data = np.fromfile(f, dtype=dtype, count=width * height)
                if data.size != width * height:
                    print(f"文件大小不匹配 {dtype} 类型，尝试下一个位深度")
                    continue

                # 重塑为2D矩阵
                matrix = data.reshape(height, width)

                # 检查数据是否只包含0,1,2
                unique_values = np.unique(matrix)
                if not all(val in [0, 1, 2] for val in unique_values):
                    print(f"数据包含非0,1,2的值: {unique_values}，尝试下一个位深度")
                    continue

                # 创建RGB图像数组
                rgb_image = np.zeros((height, width, 3), dtype=np.uint8)

                # 映射颜色：0->黑色(0,0,0), 1->红色(255,0,0), 2->蓝色(0,0,255)
                rgb_image[matrix == 0] = [0, 0, 0]  # 黑色
                rgb_image[matrix == 1] = [255, 0, 0]  # 红色
                rgb_image[matrix == 2] = [0, 0, 255]  # 蓝色

                # 保存为PNG
                image = Image.fromarray(rgb_image, 'RGB')
                image.save(output_png_path, 'PNG')
                print(f"成功将RAW文件转换为PNG，保存为 {output_png_path}，位深度: {dtype}")
                return

        except Exception as e:
            print(f"尝试 {dtype} 失败: {e}")

    print("无法读取RAW文件，请检查文件格式或位深度")


# 使用示例
raw_file_path = 'input.raw'  # 替换为你的RAW文件路径
output_png_path = 'output.png'  # 输出PNG文件路径
read_raw_to_png(raw_file_path, output_png_path)