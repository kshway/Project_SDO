import math
import io
import torch
from torchvision import transforms
import torchvision.transforms.functional as TF
import numpy as np
import os

from PIL import Image

import matplotlib.pyplot as plt

from pytorch_msssim import ms_ssim
from compressai.zoo import bmshj2018_hyperprior, cheng2020_attn


def read_yuv400_file(file_path, width, height):
    with open(file_path, 'rb') as f:
        yuv_size = int(width * height * 2)
        yuv_data = f.read(yuv_size)

    return yuv_data


def yuv400_to_rgb(yuv_data, width, height):
    yuv = np.frombuffer(yuv_data, dtype=np.uint16)
    y = yuv.reshape((height, width))
    y = y.astype(np.float32)
    y = torch.tensor(y).unsqueeze(0).unsqueeze(1)
    r = y
    g = y
    b = y

    rgb = torch.cat([r, g, b], dim=1)
    # rgb = np.dstack((r, g, b)).astype(np.float32)
    return rgb


def save_image(x, output_path):
    pil_image = TF.to_pil_image(x.squeeze(0))
    pil_image.save(output_path)


# def compute_psnr(x, x_hat):
#     mse = torch.mean((x - x_hat) ** 2).item()
#     return mse, -10 * math.log10(mse)


def compute_psnr(x, x_hat):
    mse = torch.mean((x - x_hat) ** 2).item()
    return mse, -10 * math.log10(mse) + 10 * math.log10((2**16) ** 2)


def compute_bpp(out_net):
    size = out_net['x_hat'].size()
    num_pixels = size[0] * size[2] * size[3]
    return sum(torch.log(likelihoods).sum() / (-math.log(2) * num_pixels)
              for likelihoods in out_net['likelihoods'].values()).item()


# device = 'cuda' if torch.cuda.is_available() else 'cpu'
device = 'cpu'
metric = 'mse'

sun_yuv = os.listdir("/home/vmlab/project_sh/sun")
qp_list = [1, 2, 3, 4, 5, 6]


height = width = 4096
results = {}

###############################3
for qp in qp_list:
    psnr_list = []
    bpp_list = []
    psnr_avg = 0
    bpp_avg = 0

    network = cheng2020_attn(quality=qp, pretrained=True).eval().to(device)
    # network = bmshj2018_hyperprior(quality=qp, pretrained=True).eval().to(device)

    print(f"==========QP{qp}==========")
    for yuv in sun_yuv:
        file_path = "/home/vmlab/project_sh/sun/" + yuv

        yuv_data = read_yuv400_file(file_path, height, width)
        x = yuv400_to_rgb(yuv_data, width, height).to(device)

        x_max = torch.max(x)
        x = x / x_max

        with torch.no_grad():
            encoded = network.compress(x)
            strings = encoded['strings']
            shape = encoded['shape']

            y = len(strings[0][0]) * 8
            z = len(strings[1][0]) * 8
            bpp = (y + z) / (4096 * 4096)
            print("BPP:", bpp)

            y_string = strings[0]
            z_string = strings[1]

            strings = [y_string, z_string]

            x_hat = network.decompress(strings, shape)['x_hat']
            # print(torch.max(x_hat))
            # print(torch.min(x_hat))

            x = x * x_max
            x_hat = x_hat * x_max

            mse, psnr = compute_psnr(x, x_hat)

            print(mse, psnr)
            psnr_list.append(psnr)
            bpp_list.append(bpp)

    psnr_avg = sum(psnr_list) / 28.0
    bpp_avg = sum(bpp_list) / 28.0

    results[f'QP{qp}_BPP:'] = bpp_avg
    results[f'QP{qp}_PSNR:'] = psnr_avg

print(results)

