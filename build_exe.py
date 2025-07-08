import os
import subprocess
import shutil

def build_exe():
    print("🔨 Building EXE file...")
    
    # Clean previous builds
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    # Build with spec file
    cmd = ["pyinstaller", "--clean", "app.spec"]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build successful!")
        print(f"📁 EXE file location: {os.path.abspath('dist/MyApp.exe')}")
    except subprocess.CalledProcessError as e:
        print("❌ Build failed!")
        print(f"Error: {e.stderr}")

if __name__ == "__main__":
    build_exe()