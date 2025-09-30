import subprocess
import os
import re

def list_git_files_to_utf8_decoded(output_filename="git_files_decoded.txt"):
    """
    执行 'git ls-files' 命令，明确设置 core.quotepath 为 false，
    以确保 Git 输出可直接解码的 UTF-8 文件名，并将其写入指定文件。
    """
    try:
        # 使用 -c core.quotepath=false 告诉 Git 不要对非 ASCII 字符进行转义。
        # 这样 Git 的输出就会是原始的 UTF-8 编码的文件名。
        result = subprocess.run(
            ["git", "-c", "core.quotepath=false", "ls-files"],
            capture_output=True,
            check=True,
            shell=False # 通常不建议使用 shell=True
        )

        # Git 在 core.quotepath=false 时会输出 UTF-8 编码的文件名。
        # 尝试以 UTF-8 解码输出。
        try:
            output_str = result.stdout.decode('utf-8')
        except UnicodeDecodeError:
            # 如果依然出现问题，作为备用方案，尝试系统默认编码，但通常不会发生
            print("警告：UTF-8 解码失败，尝试使用系统默认编码进行解码。")
            output_str = result.stdout.decode(os.sys.getdefaultencoding(), errors='replace')

        # 处理每一行，移除 Git 可能为包含空格或其他特殊字符的文件名添加的引号。
        processed_lines = []
        for line in output_str.strip().splitlines():
            if line.startswith('"') and line.endswith('"'):
                # 移除首尾引号
                processed_lines.append(line[1:-1])
            else:
                processed_lines.append(line)

        # 将处理后的字符串写入 UTF-8 编码的文件
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write("\n".join(processed_lines) + "\n") # 确保文件末尾有换行符

        print(f"所有 Git 文件列表已成功写入 '{output_filename}' (UTF-8 编码)。")

    except subprocess.CalledProcessError as e:
        print(f"执行 Git 命令时发生错误：{e}")
        # 确保错误输出也能被解码以方便查看
        print(f"错误输出：{e.stderr.decode(os.sys.getdefaultencoding(), errors='replace')}")
    except Exception as e:
        print(f"发生未知错误：{e}")

# 调用函数
if __name__ == "__main__":
    list_git_files_to_utf8_decoded()