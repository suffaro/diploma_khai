import os
import tempfile
import pytest
import torch
from PIL import Image
from transformers import BlipForConditionalGeneration
from safetensors.numpy import save_file
import numpy as np
import hashlib

import sys
sys.path.insert(0, "d:\\diploma\\gui")

from clip_interrogator import Config, Interrogator, LabelTable, _truncate_to_fit

# Sample image for testing
def create_sample_image():
    image = Image.new('RGB', (128, 128), color = 'red')
    return image

# Sample config for testing
def create_sample_config():
    return Config(
        caption_model_name='blip-base',
        clip_model_name='ViT-L-14/openai',
        caption_offload=False,
        clip_offload=False,
        cache_path='cache',
        data_path='fakepath',
        quiet=True
    )

def test_load_caption_model():
    config = create_sample_config()
    interrogator = Interrogator(config)
    interrogator.load_caption_model()
    assert isinstance(interrogator.caption_model, BlipForConditionalGeneration)

def test_load_clip_model():
    config = create_sample_config()
    interrogator = Interrogator(config)
    interrogator.load_clip_model()
    assert interrogator.clip_model is not None

def test_generate_caption():
    config = create_sample_config()
    interrogator = Interrogator(config)
    interrogator.load_caption_model()
    sample_image = create_sample_image()
    caption = interrogator.generate_caption(sample_image)
    assert isinstance(caption, str)
    assert len(caption) > 0

def test_image_to_features():
    config = create_sample_config()
    interrogator = Interrogator(config)
    interrogator.load_clip_model()
    sample_image = create_sample_image()
    features = interrogator.image_to_features(sample_image)
    assert isinstance(features, torch.Tensor)

def test_label_table():
    config = create_sample_config()
    config.chunk_size = 1  # Force small chunks to test chunking
    interrogator = Interrogator(config)
    labels = ["label1", "label2", "label3"]
    table = LabelTable(labels, "test", interrogator)
    assert len(table.labels) == 3
    assert len(table.embeds) == 3

def test_rank_top():
    config = create_sample_config()
    interrogator = Interrogator(config)
    interrogator.load_clip_model()
    sample_image = create_sample_image()
    image_features = interrogator.image_to_features(sample_image)
    labels = ["hot", "cold", "warm"]
    table = LabelTable(labels, "test", interrogator)
    top_label = table.rank(image_features, top_count=1)[0]
    assert top_label in labels

def test_truncate_to_fit():
    text = "part1, part2, part3, part4"
    tokenize = lambda x: [[1, 2, 3, 4, 5, 0]]  # Mock tokenizer
    truncated = _truncate_to_fit(text, tokenize)
    assert truncated == "part1, part2, part3, part4"

# Mock data for caching
def test_label_table_cache():
    config = create_sample_config()
    labels = ["label1", "label2", "label3"]
    sanitized_name = config.clip_model_name.replace('/', '_').replace('@', '_')
    desc = "test"
    hash = hashlib.sha256(",".join(labels).encode()).hexdigest()
    cache_path = os.path.join(config.cache_path, f"{sanitized_name}_{desc}.safetensors")

    embeds = [torch.randn(512).numpy() for _ in labels]
    tensors = {
        "embeds": np.stack(embeds),
        "hash": np.array([ord(c) for c in hash], dtype=np.int8)
    }
    save_file(tensors, cache_path)

    interrogator = Interrogator(config)
    table = LabelTable(labels, desc, interrogator)
    assert len(table.embeds) == 3

if __name__ == '__main__':
    pytest.main()
