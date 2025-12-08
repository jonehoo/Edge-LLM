"""
启动Streamlit Web应用
"""

import subprocess
import sys
from pathlib import Path

def main():
    """启动Web应用"""
    web_app_path = Path(__file__).parent / "web" / "app.py"
    
    if not web_app_path.exists():
        print(f"错误：找不到Web应用文件 {web_app_path}")
        sys.exit(1)
    
    print("正在启动Streamlit Web应用...")
    print("访问地址: http://localhost:8501")
    print("按 Ctrl+C 停止应用")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(web_app_path),
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n应用已停止")

if __name__ == "__main__":
    main()


