import subprocess
import sys

def install_package(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to install {package}")
        return False

def main():
    packages = [
        "streamlit",
        "pandas", 
        "scikit-learn",
        "nltk",
        "python-docx",
        "PyPDF2",
        "plotly"
    ]
    
    print("Installing required packages...")
    
    success_count = 0
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print(f"\nInstallation complete: {success_count}/{len(packages)} packages installed successfully")
    
    if success_count >= 3:  # At least streamlit, pandas, sklearn
        print("\n✅ Minimum requirements met. You can run the basic version.")
        print("Run: streamlit run app_simple.py")
    else:
        print("\n❌ Installation failed. Please install packages manually.")

if __name__ == "__main__":
    main()