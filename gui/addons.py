import os, platform, subprocess, re
import subprocess
import bcrypt
from dataclasses import dataclass

def get_processor_name():
    if platform.system() == "Windows":
        var = subprocess.check_output(['wmic', 'cpu', 'get', 'name']).decode('utf-8')
        var = var.replace(" ", "").replace('\n', '').replace('\r', '')
        return var[4:]
    elif platform.system() == "Darwin":
        os.environ['PATH'] = os.environ['PATH'] + os.pathsep + '/usr/sbin'
        command ="sysctl -n machdep.cpu.brand_string"
        return subprocess.check_output(command).strip()
    elif platform.system() == "Linux":
        command = "cat /proc/cpuinfo"
        all_info = subprocess.check_output(command, shell=True).decode().strip()
        for line in all_info.split("\n"):
            if "model name" in line:
                return re.sub( ".*model name.*:", "", line,1)
    return ""


def get_gpus():
    output = subprocess.check_output("nvidia-smi -L", shell=True)
    output = output.decode("utf-8").strip().split('\n')
    gpus = []
    for line in output:
        line, _ = line.split("(", 1)
        gpu_id, gpu_name = line.strip().split(":")
        gpus.append((gpu_id.strip(), gpu_name.strip()))
    return gpus

def hash_password(password):
    # Generate a salt
    salt = bcrypt.gensalt()
    # Hash the password
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


if __name__ == '__main__':

    gpus = get_gpus()
    for gpu_id, gpu_name in gpus:
        print(f"{gpu_id}: {gpu_name}")

    print(get_processor_name(), end="")


    #print(get_processor_name())


