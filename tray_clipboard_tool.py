import os
import sys
import pyperclip
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw, ImageFont # Pillow (PIL) is required by pystray for image handling

# --- 配置区 ---
# 脚本的根目录，相对于脚本文件所在位置的上一级目录
# 如果脚本在 C:\Project\scripts\tray_clipboard_tool.py，那么 ROOT_DIR 就是 C:\Project\
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# .role 目录的绝对路径
ROLE_DIR = os.path.join(ROOT_DIR, '.role')

# 托盘图标设置
# 可以使用自定义的 .ico 或 .png 文件路径，例如: ICON_PATH = os.path.join(ROOT_DIR, 'my_icon.png')
# 如果留空，将生成一个默认的圆形图标
ICON_PATH = "" 
ICON_NAME = "Clipboard Tool"

# --- 辅助函数 ---

def create_default_icon_image():
    """创建一个简单的默认圆形图标"""
    width, height = 64, 64
    image = Image.new('RGBA', (width, height), (0, 0, 0, 0)) # 透明背景
    draw = ImageDraw.Draw(image)

    # 绘制一个蓝色圆圈
    draw.ellipse((5, 5, width - 5, height - 5), fill=(70, 130, 180, 255), outline=(25, 25, 112, 255), width=3)
    
    try:
        # 尝试添加一个字符，例如 'C'
        font_path = "arial.ttf" # Windows系统通常有此字体
        if not os.path.exists(font_path):
            font_path = "C:/Windows/Fonts/arial.ttf" # 尝试绝对路径
        
        font = ImageFont.truetype(font_path, 36)
        text_bbox = draw.textbbox((0,0), "C", font=font) # 获取文本边界框
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        text_x = (width - text_width) / 2
        text_y = (height - text_height) / 2 - 5 # 微调位置
        
        draw.text((text_x, text_y), "C", font=font, fill=(255, 255, 255, 255))
    except Exception as e:
        print(f"Warning: Could not load font or draw text on icon: {e}. Icon will be plain circle.")

    return image

def get_icon_image():
    """加载或生成托盘图标图像"""
    if ICON_PATH and os.path.exists(ICON_PATH):
        try:
            return Image.open(ICON_PATH)
        except Exception as e:
            print(f"Error loading custom icon '{ICON_PATH}': {e}. Using default icon.")
            return create_default_icon_image()
    return create_default_icon_image()

def read_file_content(filepath):
    """安全地读取文件内容"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}")
        return f"ERROR: File not found: {filepath}"
    except IOError as e:
        print(f"Error reading file {filepath}: {e}")
        return f"ERROR: Could not read file: {filepath} - {e}"
    except Exception as e:
        print(f"An unexpected error occurred while reading {filepath}: {e}")
        return f"ERROR: Unexpected error: {filepath} - {e}"

def format_file_content(full_path, root_dir):
    """读取文件内容并将其格式化为带有相对路径标题的字符串"""
    content = read_file_content(full_path)
    # 计算相对于根目录的路径
    relative_path = os.path.relpath(full_path, root_dir)
    # 统一路径分隔符为 '/', 保证跨平台一致性
    display_path = relative_path.replace('\\', '/')
    
    return (
        f"#### file: {display_path}\n"
        f"```\n"
        f"{content}\n"
        f"```\n"
    )

def on_click(icon_instance, item):
    """菜单项点击事件处理器"""
    menu_item_name = item.text
    role_txt_file = os.path.join(ROLE_DIR, f"{menu_item_name}.txt")
    
    print(f"Clicked: {menu_item_name}, processing {role_txt_file}")

    if not os.path.exists(role_txt_file):
        error_msg = f"Error: .role file not found for '{menu_item_name}'"
        print(error_msg)
        pyperclip.copy(error_msg)
        return

    try:
        with open(role_txt_file, 'r', encoding='utf-8') as f:
            paths_from_file = [line.strip() for line in f if line.strip()] # 移除空行

        combined_content = []
        for path_entry in paths_from_file:
            full_path = os.path.normpath(os.path.join(ROOT_DIR, path_entry))
            
            # 判断是目录还是文件
            if path_entry.endswith(('/', '\\')):
                print(f"Processing directory: {full_path}")
                if os.path.isdir(full_path):
                    for dirpath, _, filenames in os.walk(full_path):
                        for filename in filenames:
                            file_full_path = os.path.join(dirpath, filename)
                            formatted_content = format_file_content(file_full_path, ROOT_DIR)
                            combined_content.append(formatted_content)
                else:
                    print(f"Warning: Path '{full_path}' specified as a directory but not found or is not a directory.")
            else:
                print(f"Processing file: {full_path}")
                if os.path.isfile(full_path):
                    formatted_content = format_file_content(full_path, ROOT_DIR)
                    combined_content.append(formatted_content)
                else:
                    print(f"Warning: File not found: {full_path}")

        final_clipboard_text = "\n".join(combined_content)
        pyperclip.copy(final_clipboard_text)
        print(f"Content for '{menu_item_name}' copied to clipboard.")

    except Exception as e:
        error_msg = f"An error occurred while processing '{menu_item_name}': {e}"
        print(error_msg)
        pyperclip.copy(error_msg)

def get_menu_items():
    """动态生成菜单项"""
    menu_items = []
    if not os.path.exists(ROLE_DIR):
        print(f"Error: .role directory not found: {ROLE_DIR}")
        menu_items.append(MenuItem(f"Error: {ROLE_DIR} not found", on_click))
        return menu_items

    try:
        for filename in sorted(os.listdir(ROLE_DIR)): # 按字母排序
            if filename.endswith('.txt'):
                menu_name = os.path.splitext(filename)[0] # 移除 .txt 扩展名
                menu_items.append(MenuItem(menu_name, on_click))
        
        if not menu_items:
            menu_items.append(MenuItem("No .txt files found in .role", None))

    except Exception as e:
        print(f"Error listing files in {ROLE_DIR}: {e}")
        menu_items.append(MenuItem(f"Error loading menus: {e}", None))
    
    return menu_items

def exit_action(icon_instance, item):
    """退出程序"""
    print("Exiting application.")
    icon_instance.stop()
    sys.exit(0)

def main():
    """主函数，启动托盘图标应用"""
    print(f"Starting {ICON_NAME}...")
    print(f"Root Directory: {ROOT_DIR}")
    print(f"Role Directory: {ROLE_DIR}")

    icon_image = get_icon_image()

    # 动态生成菜单，并添加退出选项
    menu_items = get_menu_items()
    if menu_items:
        menu_items.append(Menu.SEPARATOR) # 添加分隔线
    menu_items.append(MenuItem("Exit", exit_action))
    
    menu = Menu(*menu_items)

    icon = Icon(ICON_NAME, icon_image, ICON_NAME, menu)
    icon.run()

if __name__ == "__main__":
    # 检查必要的依赖
    try:
        import pystray
        from PIL import Image, ImageDraw, ImageFont
        import pyperclip
    except ImportError:
        print("Required libraries not found. Please install them:")
        print("pip install pystray Pillow pyperclip")
        sys.exit(1)
        
    main()