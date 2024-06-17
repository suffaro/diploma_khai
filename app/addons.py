import os, platform, subprocess, re
import subprocess
import bcrypt
from dataclasses import dataclass
from typing import Optional

def get_processor_name():
    if platform.system() == "Windows":
        var = subprocess.check_output(['wmic', 'cpu', 'get', 'name']).decode('utf-8')
        var = var.replace(" ", "").replace('\n', '').replace('\r', '')
        return var[4:]
    elif platform.system() == "Darwin":
        os.environ['PATH'] = os.environ['PATH'] + os.pathsep + '/usr/sbin'
        command ="sysctl -n machdep.cpu.brand_string"
        return subprocess.check_output(command).decode('utf-8').strip()
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

@dataclass 
class Config:
    # models can optionally be passed in directly
    caption_model = None
    caption_processor = None
    clip_model = None
    clip_preprocess = None

    # blip settings
    caption_max_length: int = 32
    caption_model_name: Optional[str] = 'blip-large' # use a key from CAPTION_MODELS or None
    caption_offload: bool = False

    # clip settings
    clip_model_name: str = 'ViT-L-14/openai'
    clip_model_path: Optional[str] = None
    clip_offload: bool = False

    # interrogator settings
    cache_path: str = 'cache'   # path to store cached text embeddings
    download_cache: bool = True # when true, cached embeds are downloaded from huggingface
    chunk_size: int = 2048      # batch size for CLIP, use smaller for lower VRAM
    data_path: str = os.path.join(os.path.dirname(__file__), 'data')
    device: str = "cuda"
    flavor_intermediate_count: int = 2048
    quiet: bool = False # when quiet progress bars are not shown

    def apply_low_vram_defaults(self):
        self.caption_model_name = 'blip-base'
        self.caption_offload = True
        self.clip_offload = True
        self.chunk_size = 1024
        self.flavor_intermediate_count = 1024
