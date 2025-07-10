import os
import re
from pathlib import Path


def delete_duplicate_xml_files(base_path):
    """
    检查指定路径下所有视频号的标签文件，删除形如 filename(1).xml 的重复文件

    Args:
        base_path: 标签数据根路径 (D:\数据集转换汇总\标签专用文件夹\标签整理2\0整理\跌倒\)

    Returns:
        int: 删除的重复文件数量
    """
    base_path = Path(base_path)

    # 统计删除的文件数量和路径
    deleted_count = 0
    deleted_files = []

    # 正则表达式匹配形如 filename(1).xml 的文件
    duplicate_pattern = re.compile(r'(.+?)\(\d+\)\.xml$')

    # 遍历所有视频号文件夹
    for video_dir in base_path.iterdir():
        if video_dir.is_dir():
            video_id = video_dir.name  # 视频号，例如 20250507152126484

            # 处理 aps 和 evs 文件夹
            for sub_dir_name in ['aps', 'evs']:
                sub_dir = video_dir / sub_dir_name

                if sub_dir.exists():
                    # 收集所有 XML 文件
                    xml_files = list(sub_dir.glob('*.xml'))

                    # 查找重复文件
                    for xml_file in xml_files:
                        match = duplicate_pattern.match(xml_file.name)
                        if match:
                            original_filename = match.group(1) + '.xml'
                            original_file = sub_dir / original_filename

                            # 检查原始文件是否存在
                            if original_file.exists():
                                try:
                                    xml_file.unlink()  # 删除重复文件
                                    deleted_count += 1
                                    deleted_files.append(str(xml_file))
                                    print(f"已删除重复文件: {xml_file}")
                                except Exception as e:
                                    print(f"删除文件 {xml_file} 时出错: {e}")

    return deleted_count, deleted_files


def main():
    # 输入路径
    base_path = r"D:\数据集转换汇总\标签专用文件夹\标签整理2\0整理\跌倒"

    # 执行删除操作
    deleted_count, deleted_files = delete_duplicate_xml_files(base_path)

    # 打印总结
    print("\n=== 删除重复标签文件总结 ===")
    if deleted_count > 0:
        print(f"共删除 {deleted_count} 个重复标签文件：")
        for file_path in deleted_files:
            print(f"- {file_path}")
    else:
        print("未找到任何重复标签文件。")


if __name__ == "__main__":
    main()