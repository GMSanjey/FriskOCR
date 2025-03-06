import os
import sys
import subprocess
import logging

def get_base_dir():
    """Get the correct base directory whether running as script or exe"""
    if getattr(sys, 'frozen', False):
        # Running as executable
        return os.path.dirname(sys.executable)
    else:
        # Running as script
        return os.path.dirname(os.path.abspath(__file__))

# Set up basic logging
base_dir = get_base_dir()
logging.basicConfig(
    filename=os.path.join(base_dir, 'friskocr_launcher.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def run_main():
    try:
        # Get the actual directory where the exe/script is located
        base_dir = get_base_dir()
        logging.info(f"Base directory: {base_dir}")
        
        # Set up paths
        venv_dir = os.path.join(base_dir, "friskocr")
        main_script = os.path.join(base_dir, "main.py")
        logging.info(f"Virtual environment path: {venv_dir}")
        logging.info(f"Main script path: {main_script}")
        
        if sys.platform == "win32":
            python_path = os.path.join(venv_dir, "Scripts", "python.exe")
            activate_script = os.path.join(venv_dir, "Scripts", "activate.bat")
        else:
            python_path = os.path.join(venv_dir, "bin", "python")
            activate_script = os.path.join(venv_dir, "bin", "activate")

        # Verify paths exist
        if not os.path.exists(activate_script):
            logging.error(f"Virtual environment not found. Checking paths:")
            logging.error(f"Activate script path: {activate_script}")
            logging.error(f"Base directory contents: {os.listdir(base_dir)}")
            raise FileNotFoundError(f"Virtual environment not found at: {venv_dir}")
            
        if not os.path.exists(main_script):
            logging.error(f"main.py not found at: {main_script}")
            raise FileNotFoundError(f"main.py not found at: {main_script}")

        # Run main.py with activated venv
        if sys.platform == "win32":
            cmd = f'"{activate_script}" && "{python_path}" "{main_script}"'
            logging.info(f"Running command: {cmd}")
            process = subprocess.Popen(
                cmd,
                shell=True,
                cwd=base_dir,  # Set working directory
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
        else:
            cmd = f'source "{activate_script}" && "{python_path}" "{main_script}"'
            logging.info(f"Running command: {cmd}")
            process = subprocess.Popen(
                ['/bin/bash', '-c', cmd],
                cwd=base_dir,  # Set working directory
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

        # Get output
        stdout, stderr = process.communicate()
        
        if stdout:
            print(stdout)
            logging.info(stdout)
        if stderr:
            print(stderr, file=sys.stderr)
            logging.error(stderr)
            
        if process.returncode != 0:
            raise RuntimeError(f"Error running main.py: {stderr}")

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        run_main()
    except Exception as e:
        print(f"Error: {str(e)}")
        logging.error(str(e))
        input("Press Enter to exit...")
        sys.exit(1)