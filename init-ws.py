import os
import sys
import json
import subprocess


def run_command(cmd, shell=False):
    # On Windows, if the command is 'code', run it using the shell
    if sys.platform == "win32" and isinstance(cmd, list) and cmd[0] == "code":
        cmd = " ".join(cmd)
        shell = True
    print(f"Running: {cmd}")
    subprocess.run(cmd, check=True, shell=shell)


def get_venv_python():
    if sys.platform == "win32":
        return os.path.join(".venv", "Scripts", "python.exe")
    else:
        return os.path.join(".venv", "bin", "python")


def create_virtualenv():
    if not os.path.exists(".venv"):
        run_command([sys.executable, "-m", "venv", ".venv"])
    else:
        print("Virtual environment already exists.")


def activate_virtualenv():
    venv_dir = os.path.abspath(".venv")
    if sys.platform == "win32":
        venv_bin = os.path.join(venv_dir, "Scripts")
    else:
        venv_bin = os.path.join(venv_dir, "bin")
    os.environ["VIRTUAL_ENV"] = venv_dir
    os.environ["PATH"] = venv_bin + os.pathsep + os.environ.get("PATH", "")


def upgrade_tools():
    venv_python = get_venv_python()
    run_command([venv_python, "-m", "pip", "install", "-U", "pip", "setuptools"])


def install_poetry():
    venv_python = get_venv_python()
    run_command([venv_python, "-m", "pip", "install", "poetry"])


def install_dependencies():
    venv_python = get_venv_python()
    run_command([venv_python, "-m", "poetry", "install"])


def install_precommit():
    venv_python = get_venv_python()
    run_command([venv_python, "-m", "poetry", "run", "pre-commit", "install"])


def install_vscode_extensions():
    extensions_file = os.path.join(".vscode", "extensions.json")
    if not os.path.exists(extensions_file):
        print("No VSCode extensions file found.")
        return
    try:
        with open(extensions_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print("Error parsing extensions.json:", e)
        return
    recommendations = data.get("recommendations", [])
    if not recommendations:
        print("No VSCode extension recommendations found.")
        return
    for ext in recommendations:
        print(f"Installing VSCode extension: {ext}")
        try:
            run_command(["code", "--install-extension", ext])
        except subprocess.CalledProcessError:
            print(f"Regular release installation failed, trying pre-release for: {ext}")
            try:
                run_command(["code", "--install-extension", ext, "--pre-release"])
            except subprocess.CalledProcessError:
                print(f"Failed to install {ext} (both release and pre-release)")


def main():
    create_virtualenv()
    activate_virtualenv()
    upgrade_tools()
    install_poetry()
    install_dependencies()
    install_precommit()
    install_vscode_extensions()
    print(
        "Setup complete. Please reload your windows terminal or IDE to use the new environment."
    )


if __name__ == "__main__":
    main()