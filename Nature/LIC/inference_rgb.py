import math
import io
import torch
from torchvision import transforms
import torchvision.transforms.functional as TF
import numpy as np
import os
import cv2

from compressai.zoo import bmshj2018_hyperprior, cheng2020_attn


def read_rgb_file(file_path):
    rgb_data = cv2.imread(file_path)
    rgb_data = rgb_data.transpose(2, 0, 1).astype(np.float64)
    rgb_data /= 255.0
    rgb_data = torch.Tensor(rgb_data).unsqueeze(0)
    return  rgb_data


def save_image(x, output_path):
    pil_image = TF.to_pil_image(x.squeeze(0))
    pil_image.save(output_path)


def compute_psnr(x, x_hat):
    mse = torch.mean((x - x_hat) ** 2).item()
    return mse, -10 * math.log10(mse)


# def compute_psnr(x, x_hat):
#     mse = torch.mean((x - x_hat) ** 2).item()
#     return mse, -10 * math.log10(mse) + 10 * math.log10((2**16) ** 2)


def compute_bpp(out_net):
    size = out_net['x_hat'].size()
    num_pixels = size[0] * size[2] * size[3]
    return sum(torch.log(likelihoods).sum() / (-math.log(2) * num_pixels)
              for likelihoods in out_net['likelihoods'].values()).item()


device = 'cpu'
metric = 'mse'

rgb_png_path = "/user2/data/kodak24/"
rgb_png = os.listdir(rgb_png_path)
png_len = len(rgb_png)

qp_list = [1, 2, 3, 4, 5, 6]
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
    for png in rgb_png:
        file_path = rgb_png_path + png

        x = read_rgb_file(file_path)
        _, _, h, w = x.size()

        with torch.no_grad():
            encoded = network.compress(x)
            strings = encoded['strings']
            shape = encoded['shape']

            y = len(strings[0][0]) * 8
            z = len(strings[1][0]) * 8
            bpp = (y + z) / (h * w)
            print("BPP:", bpp)

            y_string = strings[0]
            z_string = strings[1]

            strings = [y_string, z_string]

            x_hat = network.decompress(strings, shape)['x_hat']

            mse, psnr = compute_psnr(x, x_hat)

            print(mse, psnr)
            psnr_list.append(psnr)
            bpp_list.append(bpp)

    psnr_avg = sum(psnr_list) / png_len
    bpp_avg = sum(bpp_list) / png_len

    results[f'QP{qp}_BPP:'] = bpp_avg
    results[f'QP{qp}_PSNR:'] = psnr_avg

print(results)

