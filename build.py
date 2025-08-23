#!/usr/bin/env python3
"""
基金考试题库系统构建脚本
自动清理垃圾文件并构建独立的exe文件
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def print_step(step_name):
    """打印构建步骤"""
    print(f"\n{'='*50}")
    print(f"  {step_name}")
    print(f"{'='*50}")

def clean_build_artifacts():
    """清理构建产物和垃圾文件"""
    print_step("清理垃圾文件和构建产物")
    
    # 需要清理的目录
    dirs_to_clean = [
        'build',
        'dist', 
        '__pycache__',
        '.pytest_cache',
        'htmlcov',
        '.coverage',
        '.mypy_cache',
        '.pytype'
    ]
    
    # 需要清理的文件模式
    files_to_clean = [
        '*.pyc',
        '*.pyo', 
        '*.pyd',
        '*.so',
        '*.egg-info',
        '*.spec',
        '*.log'
    ]
    
    # 清理目录
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"删除目录: {dir_name}")
            shutil.rmtree(dir_name, ignore_errors=True)
        
        # 递归清理子目录中的缓存
        for root, dirs, files in os.walk('.'):
            for d in dirs[:]:  # 使用切片复制避免修改正在迭代的列表
                if d == dir_name:
                    full_path = os.path.join(root, d)
                    print(f"删除缓存目录: {full_path}")
                    shutil.rmtree(full_path, ignore_errors=True)
                    dirs.remove(d)
    
    # 清理文件
    import glob
    for pattern in files_to_clean:
        for file_path in glob.glob(pattern, recursive=True):
            if os.path.exists(file_path):
                print(f"删除文件: {file_path}")
                os.remove(file_path)
    
    print("✅ 垃圾文件清理完成")

def check_dependencies():
    """检查构建依赖"""
    print_step("检查构建依赖")
    
    try:
        import PyInstaller
        print(f"✅ PyInstaller 版本: {PyInstaller.__version__}")
    except ImportError:
        # 尝试通过命令行检查
        try:
            result = subprocess.run(['pyinstaller', '--version'], 
                                  capture_output=True, text=True, check=True)
            version = result.stdout.strip()
            print(f"✅ PyInstaller 版本: {version}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ PyInstaller 未安装")
            print("请先运行 'uv sync --group build' 安装构建依赖")
            sys.exit(1)
    
    # 检查其他依赖
    required_modules = ['docx', 'lxml', 'PIL']
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} 模块可用")
        except ImportError:
            print(f"⚠️  {module} 模块未找到，构建时可能需要额外处理")

def build_executable():
    """构建可执行文件"""
    print_step("构建可执行文件")
    
    # PyInstaller 构建参数
    build_args = [
        'pyinstaller',
        '--onefile',                    # 打包成单个文件
        '--windowed',                   # 窗口模式，不显示控制台
        '--name=基金考试题库系统',        # 输出文件名
        '--icon=icon.ico',              # 程序图标
        '--clean',                      # 清理临时文件
        '--noconfirm',                  # 不询问覆盖
        '--hidden-import=docx',         # 隐式导入docx模块
        '--hidden-import=docx.shared',  # docx子模块
        '--hidden-import=lxml',         # lxml模块
        '--hidden-import=PIL',          # Pillow模块
        '--distpath=dist',              # 输出目录
        '--workpath=build',             # 工作目录
        'main.py'                       # 主程序文件
    ]
    
    print("构建命令:")
    print(" ".join(build_args))
    print()
    
    try:
        # 执行构建
        result = subprocess.run(build_args, check=True, capture_output=True, text=True)
        print("✅ 构建成功完成")
        
        # 检查输出文件
        exe_path = Path("dist/基金考试题库系统.exe")
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"✅ 可执行文件已生成: {exe_path}")
            print(f"   文件大小: {size_mb:.1f} MB")
        else:
            print("⚠️  可执行文件未找到")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        if e.stdout:
            print("标准输出:")
            print(e.stdout)
        if e.stderr:
            print("错误输出:")
            print(e.stderr)
        return False
    
    return True

def post_build_cleanup():
    """构建后清理"""
    print_step("构建后清理")
    
    # 清理PyInstaller生成的临时文件
    temp_dirs = ['build']
    for dir_name in temp_dirs:
        if os.path.exists(dir_name):
            print(f"清理临时目录: {dir_name}")
            shutil.rmtree(dir_name, ignore_errors=True)
    
    # 清理spec文件（如果是自动生成的）
    spec_files = [f for f in os.listdir('.') if f.endswith('.spec')]
    for spec_file in spec_files:
        if spec_file != '基金考试题库系统.spec':  # 保留我们的spec文件
            print(f"清理spec文件: {spec_file}")
            os.remove(spec_file)
    
    print("✅ 构建后清理完成")

def main():
    """主构建流程"""
    print("🚀 基金考试题库系统构建脚本")
    print(f"Python 版本: {sys.version}")
    print(f"工作目录: {os.getcwd()}")
    
    try:
        # 1. 清理垃圾文件
        clean_build_artifacts()
        
        # 2. 检查依赖
        check_dependencies()
        
        # 3. 构建可执行文件
        if build_executable():
            # 4. 构建后清理
            post_build_cleanup()
            
            print_step("构建完成")
            print("🎉 构建成功！")
            print("📁 可执行文件位置: dist/基金考试题库系统.exe")
            print("💡 提示: 可以直接运行该exe文件，无需安装Python环境")
        else:
            print("❌ 构建失败，请检查错误信息")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  构建被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 构建过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
