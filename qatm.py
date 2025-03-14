from pathlib import Path
import torch
import torchvision
from torchvision import models, transforms, utils
import argparse
import pickle
from utils import *

import time

# +
# import functions and classes from qatm_pytorch.py
print("import qatm_pytorch.py...")
import ast
import types
import sys


with open("qatm_pytorch.py") as f:
       p = ast.parse(f.read())

for node in p.body[:]:
    if not isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Import, ast.ImportFrom)):
        p.body.remove(node)

module = types.ModuleType("mod")
code = compile(p, "mod.py", 'exec')
sys.modules["mod"] = module
exec(code,  module.__dict__)

from mod import *
# -

RESULT_DIR = 'result'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='QATM Pytorch Implementation')
    parser.add_argument('--cuda', action='store_true')
    parser.add_argument('-s', '--sample_image', default='sample/sample1.jpg')
    parser.add_argument('-t', '--template_images_dir', default='template/')
    parser.add_argument('--alpha', type=float, default=25)
    parser.add_argument('--thresh_csv', type=str, default='thresh_template.csv')
    args = parser.parse_args()
    
    template_dir = args.template_images_dir
    image_path = args.sample_image
    dataset = ImageDataset(Path(template_dir), image_path, thresh_csv='thresh_template.csv')

    start_time = time.time()
    print("define model...")
    # model = CreateModel(model=models.vgg19(pretrained=True).features, alpha=args.alpha, use_cuda=args.cuda)
    model = pickle.load(open('model.obj', 'rb'))
    print(f'took {time.time() - start_time}s.')

    print("calculate score...")
    start_time = time.time()
    scores, w_array, h_array, thresh_list = run_multi_sample(model, dataset)
    print("nms...")
    print(f'took {time.time() - start_time}s.')
    boxes, indices = nms_multi(scores, w_array, h_array, thresh_list)
    
    result_path = os.path.join(RESULT_DIR, os.path.splitext(os.path.basename(image_path))[0] + '.png')
    _ = plot_result_multi(dataset.image_raw, boxes, indices, show=False, save_name=result_path)
    print(f"{result_path=}")
