import os
import sys
import argparse


def search_files(directory, keyword, file_extensions=None, case_sensitive=False):
    """
    在指定目录及其子目录中搜索包含特定关键字的文件

    Args:
        directory: 要搜索的目录路径
        keyword: 要搜索的关键字
        file_extensions: 要搜索的文件扩展名列表，如 ['.txt', '.py']，None表示所有文件
        case_sensitive: 是否区分大小写，默认为False

    Returns:
        包含匹配文件的路径和匹配行信息的列表
    """
    matches = []

    # 遍历目录和子目录
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)

            # 检查文件扩展名
            if file_extensions:
                _, ext = os.path.splitext(file)
                if ext.lower() not in [ext.lower() for ext in file_extensions]:
                    continue

            try:
                # 尝试以不同编码打开文件
                encodings = ['utf-8', 'gbk', 'latin-1', 'cp1252']
                content = None

                for encoding in encodings:
                    try:
                        with open(file_path, 'r', encoding=encoding) as f:
                            content = f.read()
                        break
                    except (UnicodeDecodeError, UnicodeError):
                        continue

                # 如果无法用文本模式读取，跳过该文件
                if content is None:
                    continue

                # 搜索关键字
                lines = content.split('\n')
                for line_num, line in enumerate(lines, 1):
                    search_line = line if case_sensitive else line.lower()
                    search_keyword = keyword if case_sensitive else keyword.lower()

                    if search_keyword in search_line:
                        matches.append({
                            'file_path': file_path,
                            'line_number': line_num,
                            'line_content': line.strip(),
                            'keyword': keyword
                        })

            except Exception as e:
                print(f"无法读取文件 {file_path}: {e}", file=sys.stderr)

    return matches


def main():
    parser = argparse.ArgumentParser(description='在目录中搜索包含特定关键字的文件')
    parser.add_argument('directory', help='要搜索的目录路径')
    parser.add_argument('keyword', help='要搜索的关键字')
    parser.add_argument('-e', '--extensions', nargs='+',
                        help='文件扩展名列表，例如: .txt .py .md')
    parser.add_argument('-c', '--case-sensitive', action='store_true',
                        help='区分大小写')
    parser.add_argument('-o', '--output',
                        help='将结果保存到指定文件')

    args = parser.parse_args()

    # 检查目录是否存在
    if not os.path.isdir(args.directory):
        print(f"错误: 目录 '{args.directory}' 不存在")
        return 1

    print(f"在目录 '{args.directory}' 中搜索关键字 '{args.keyword}'...")

    # 执行搜索
    matches = search_files(
        args.directory,
        args.keyword,
        args.extensions,
        args.case_sensitive
    )

    # 输出结果
    if matches:
        print(f"\n找到 {len(matches)} 个匹配结果:")
        print("-" * 80)

        for match in matches:
            print(f"文件: {match['file_path']}")
            print(f"行 {match['line_number']}: {match['line_content']}")
            print("-" * 80)

        # 保存到文件
        if args.output:
            try:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(f"搜索目录: {args.directory}\n")
                    f.write(f"搜索关键字: {args.keyword}\n")
                    f.write(f"找到 {len(matches)} 个匹配结果:\n\n")

                    for match in matches:
                        f.write(f"文件: {match['file_path']}\n")
                        f.write(f"行 {match['line_number']}: {match['line_content']}\n")
                        f.write("-" * 80 + "\n")

                print(f"\n结果已保存到: {args.output}")
            except Exception as e:
                print(f"保存结果到文件时出错: {e}")
    else:
        print("未找到匹配的文件")

    return 0


# 函数式使用示例
def search_files_simple(directory, keyword):
    """
    简化版的搜索函数，返回匹配的文件路径列表
    """
    matches = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)

            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if keyword.lower() in content.lower():
                        matches.append(file_path)
            except:
                continue

    return matches


if __name__ == "__main__":
    # 作为脚本运行
    sys.exit(main())