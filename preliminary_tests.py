import sys
import os
import importlib

def run_preliminary_tests():
    print("Running Preliminary Tests for the Dam Reservoir Area Project...")
    print("-" * 50)
    
    # 1. Check Python Version
    print("\n[1] Checking Python Version...")
    if sys.version_info >= (3, 8):
        print(f"✅ Python version {sys.version_info.major}.{sys.version_info.minor} is supported.")
    else:
        print(f"❌ Python version {sys.version_info.major}.{sys.version_info.minor} is too old. Please use 3.8 or higher.")
        
    # 2. Check Required External Packages
    print("\n[2] Checking Required Dependencies...")
    required_packages = {
        "numpy": "numpy",
        "scipy": "scipy",
        "matplotlib": "matplotlib",
        "sentinelhub": "sentinelhub",
        "dotenv": "python-dotenv"
    }
    
    missing_packages = []
    for module_name, pip_name in required_packages.items():
        try:
            importlib.import_module(module_name)
            print(f"✅ {pip_name} is installed.")
        except ImportError:
            missing_packages.append(pip_name)
            print(f"❌ {pip_name} is MISSING.")
            
    if missing_packages:
        print("\n⚠️ Missing dependencies detected! Run the following command to install them:")
        print(f"pip install {' '.join(missing_packages)}")
    else:
        print("✅ All required external packages are installed.")

    # 3. Check for Sentinel Hub API Credentials
    print("\n[3] Checking Sentinel Hub API Credentials...")
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass # Handle case where dotenv is not installed yet
        
    client_id = os.environ.get('SH_CLIENT_ID')
    client_secret = os.environ.get('SH_CLIENT_SECRET')
    
    # Check fallback configs for SH credentials directly if possible
    has_creds = bool(client_id and client_secret)
    if not has_creds:
        try:
            from sentinelhub.config import SHConfig
            config = SHConfig()
            if config.sh_client_id and config.sh_client_secret:
                has_creds = True
                print("✅ Sentinel Hub API Credentials found via sentinelhub configuration.")
        except Exception:
            pass

    if has_creds:
        if bool(client_id and client_secret):
            print("✅ Sentinel Hub API Credentials found in environment variables.")
    else:
        print("❌ Sentinel Hub API Credentials are MISSING.")
        print("   Please create a '.env' file in the root directory and add:")
        print("   SH_CLIENT_ID=your_client_id")
        print("   SH_CLIENT_SECRET=your_client_secret")
        print("   Or configure them globally via the target tool 'sentinelhub.config SHConfig'.")

    # 4. Check Internal Project Imports (Structural integrity)
    print("\n[4] Checking Project Structure & Imports...")
    project_imports = [
        "constants",
        "objects",
        "fetch_dam.get_dam",
        "pipeline.acquisition",
        "pipeline.processing",
        "pipeline.raw_data",
        "pipeline.visuals",
        "sentinel.request",
        "processing.select_reservoir"
    ]
    
    broken_imports = []
    for mod in project_imports:
        try:
            importlib.import_module(mod)
            print(f"✅ Successfully imported '{mod}'")
        except ImportError as e:
            broken_imports.append((mod, e))
            print(f"❌ Failed to import '{mod}': {e}")
            
    if broken_imports:
        print("\n⚠️ Structural issues detected. Make sure module roots are accurate.")
    else:
        print("✅ Core project modules are importing successfully.")

    # 5. Check Dam Database
    print("\n[5] Checking Dam Database Access...")
    try:
        from fetch_dam.get_dam import DATABASE_PATH
        if os.path.exists(DATABASE_PATH):
            print(f"✅ Dam database found at {DATABASE_PATH}")
        else:
            print(f"❌ Dam database '{DATABASE_PATH}' not found. Check fetch_dam module.")
    except Exception as e:
        print(f"⚠️ Could not verify database path: {e}")

    # Final Summary
    print("-" * 50)
    all_passed = (not missing_packages) and has_creds and (not broken_imports)
    if all_passed:
        print("🎉 All preliminary checks passed! The project is ready to run.")
        print("Try running: python3 main.py \"Panshet Dam\"")
    else:
        print("⚠️ Some checks failed. Please resolve the issues above before running main.py.")

if __name__ == "__main__":
    # Ensure the root directory is in sys.path so we can import packages correctly
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
        
    run_preliminary_tests()
