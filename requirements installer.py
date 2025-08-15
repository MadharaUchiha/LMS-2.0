import subprocess
import sys

# List all required libraries here
required_libraries = [
    "customtkinter",
    "matplotlib",
    "pillow",
    "numpy",
    "sqlite3"  # sqlite3 is built-in, so no need to install usually
]

def install_library(lib):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
        print(f"[✔] {lib} installed successfully.")
    except subprocess.CalledProcessError:
        print(f"[✖] Failed to install {lib}.")

def main():
    print("Checking and installing required libraries...\n")
    for lib in required_libraries:
        try:
            __import__(lib)
            print(f"[✔] {lib} is already installed.")
        except ImportError:
            print(f"[⚠] {lib} not found. Installing...")
            install_library(lib)

    print("\nAll required libraries are installed. You can now run the project!")

if __name__ == "__main__":
    main()
