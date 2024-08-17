from utils import *

import argparse


parser = argparse.ArgumentParser(description="Rename All the files in the directory")
parser.add_argument(
    "directory", type=str, help="Enter The Directory which files you want to rename"
)
parser.add_argument(
    "device", type=str, help="Enter The Device type i.e. 'cuda','mps','cpu'"
)

args = parser.parse_args()




directory_path = args.directory
device=args.device

rename(directory_path,device)
