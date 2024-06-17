import sys
sys.path.insert(0, "d:\\diploma\\app")
print(sys.path)



import pytest
import bcrypt
from unittest.mock import patch
from addons import Config, get_processor_name, get_gpus, hash_password

def test_config_defaults():
    config = Config()

    assert config.caption_max_length == 32
    assert config.caption_model_name == 'blip-large'
    assert config.caption_offload is False
    assert config.clip_model_name == 'ViT-L-14/openai'
    assert config.clip_model_path is None
    assert config.clip_offload is False
    assert config.cache_path == 'cache'
    assert config.download_cache is True
    assert config.chunk_size == 2048
    assert config.device == 'cuda'
    assert config.flavor_intermediate_count == 2048
    assert config.quiet is False

def test_apply_low_vram_defaults():
    config = Config()
    config.apply_low_vram_defaults()

    assert config.caption_model_name == 'blip-base'
    assert config.caption_offload is True
    assert config.clip_offload is True
    assert config.chunk_size == 1024
    assert config.flavor_intermediate_count == 1024


@patch('platform.system')
@patch('subprocess.check_output')
def test_get_processor_name_windows(mock_subprocess, mock_platform):
    mock_platform.return_value = 'Windows'
    mock_subprocess.return_value = b'Name  Intel(R) Core(TM) i7-9750H CPU @ 2.60GHz  \r\n\r\n'

    processor_name = get_processor_name()
    assert processor_name == 'Intel(R)Core(TM)i7-9750HCPU@2.60GHz'

@patch('platform.system')
@patch('subprocess.check_output')
def test_get_processor_name_darwin(mock_subprocess, mock_platform):
    mock_platform.return_value = 'Darwin'
    mock_subprocess.return_value = b'Intel(R) Core(TM) i7-9750H CPU @ 2.60GHz\n'

    processor_name = get_processor_name()
    assert processor_name == 'Intel(R) Core(TM) i7-9750H CPU @ 2.60GHz'

@patch('platform.system')
@patch('subprocess.check_output')
def test_get_processor_name_linux(mock_subprocess, mock_platform):
    mock_platform.return_value = 'Linux'
    mock_subprocess.return_value = b'processor\t: 0\nmodel name\t: Intel(R) Core(TM) i7-9750H CPU @ 2.60GHz\n'

    processor_name = get_processor_name()
    assert processor_name == ' Intel(R) Core(TM) i7-9750H CPU @ 2.60GHz'

@patch('subprocess.check_output')
def test_get_gpus(mock_subprocess):
    mock_subprocess.return_value = b'GPU 0: Tesla K80 (UUID: GPU-12345678-1234-5678-1234-567812345678)\nGPU 1: Tesla T4 (UUID: GPU-87654321-4321-8765-4321-876543218765)'

    gpus = get_gpus()
    assert gpus == [('GPU 0', 'Tesla K80'), ('GPU 1', 'Tesla T4')]

def test_hash_password():
    password = 'securepassword123'
    hashed_password = hash_password(password)
    
    assert bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

# Only include this if you want to run the file directly
if __name__ == '__main__':
    pytest.main()
