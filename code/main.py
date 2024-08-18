from utils import *

import argparse


parser = argparse.ArgumentParser(description="Rename All the files in the directory")
parser.add_argument(
    "directory", type=str, help="Enter The Directory which files you want to rename"
)

args = parser.parse_args()




directory_path = args.directory

rename(directory_path)
