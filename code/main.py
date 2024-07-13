import utils
from transformers import AutoProcessor, AutoModelForCausalLM, AutoTokenizer
import torch
import argparse


parser = argparse.ArgumentParser(description='Rename All the files in the directory')
parser.add_argument('directory', type=str, help="Enter The Directory which files you want to rename" )
args = parser.parse_args()

torch.set_default_device("cuda")

image_model = AutoModelForCausalLM.from_pretrained(
    "microsoft/Florence-2-base", trust_remote_code=True
).eval()
image_processor = AutoProcessor.from_pretrained(
    "microsoft/Florence-2-base", trust_remote_code=True
).eval()

text_model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen1.5-1.8B-Chat", torch_dtype="auto", device_map="auto"
)
text_tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen1.5-1.8B-Chat")


directory_path=args.directory

utils.rename(directory_path)
