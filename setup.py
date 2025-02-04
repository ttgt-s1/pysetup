import getpass
import os
import platform
from contextlib import contextmanager
from shutil import which
import sys
import subprocess


USERNAME = getpass.getuser()
CONDA_ENV_NAME = 'totogoto'
PLATFORM = platform.system().lower()

VS_CODE_EXTENSIONS = [
    "ms-python.vscode-pylance",
    "ms-toolsai.jupyter",
    "ms-toolsai.jupyter-keymap",
    "ms-toolsai.jupyter-renderers"
]


YAML_FILE_NAME = 'environment.yml'
ENV_YAML_CONTENT = '''name: totogoto
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.9.5
  - git
  - pip
  - ipython=7.29.0
  - ipykernel=6.4.2
  - pip:
      - ottopy
      - requests
'''


def is_bin_exist(name):
    return which(name) is not None


def run_command(cmd):
    print(f"Running ==> `{cmd}`")
    stream = os.popen(cmd)
    op = stream.read()

    return op


def create_env_yaml_file():
    if not os.path.isfile(YAML_FILE_NAME):
        with open(YAML_FILE_NAME, "w") as f:
            f.write(ENV_YAML_CONTENT)


def download_file(url, file_name):
    import requests
    get_response = requests.get(url, stream=True)
    with open(file_name, 'wb') as f:
        for chunk in get_response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)


def create_run_py():
    if not os.path.isfile('run.py'):
        download_file(
            'https://raw.githubusercontent.com/totogoto/pysetup/main/run.py', 'run.py')


def conda_path():
    if os.environ.get('CONDA_PREFIX') is not None:
        return os.environ['CONDA_PREFIX']
    else:
        if PLATFORM == 'linux':
            return f'/home/{USERNAME}/miniconda3'
        if PLATFORM == 'windows':
            return f'C:/Users/{USERNAME}/miniconda3'
        if PLATFORM == 'darwin':
            return '/Users/{USERNAME}/miniconda3'


@contextmanager
def pushd(dir):
    old_dir = os.getcwd()
    os.chdir(dir)
    yield
    os.chdir(old_dir)


def check_env_exist():
    ouput = run_command('conda env list').split("\n")[2:]
    env_names = list(filter(lambda x: len(x) > 0, map(
        lambda f:  f.split(" ")[0], ouput)))
    return CONDA_ENV_NAME in env_names


def setup_env():
    conda_dir = conda_path()
    conda_env_path = f"{conda_dir}/envs/{CONDA_ENV_NAME}"
    if os.path.isdir(conda_env_path) and check_env_exist():
        print(f"{CONDA_ENV_NAME} environment exists")
    else:
        print(f"Creating {CONDA_ENV_NAME} Env ...\n")
        print(run_command(f"conda env create -f {YAML_FILE_NAME}"))


def setup_vscode():
    if not is_bin_exist('code'):
        raise RuntimeError('VS Code is Not Installed')
    else:
        existing_extensions = run_command('code --list-extensions').split("\n")
        for extension in VS_CODE_EXTENSIONS:
            if extension in existing_extensions:
                print(f"vscode extension: {extension} already exists.")
            else:
                print(f"Installing vscode extension: {extension}.")

                run_command(f"code --install-extension {extension}")


def setup_pkgs():
    subprocess.check_call([sys.executable, '-m', 'conda', 'install', '-y',
                           'requests'])


def main():
    setup_pkgs()
    create_env_yaml_file()
    setup_env()
    setup_vscode()
    create_run_py()


if __name__ == "__main__":
    main()
