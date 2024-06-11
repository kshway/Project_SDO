import math
import io
import torch
import torchvision.transforms.functional as TF
import torch.nn.functional as F
import numpy as np

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


def cal_image_padding_size(shape):
        ps = 64

        ori_size = shape

        paddings = []
        unpaddings = []
        padded_size = []

        h = ori_size[0]
        w = ori_size[1]

        h_pad_len = ps - h % ps if h % ps != 0 else 0
        w_pad_len = ps - w % ps if w % ps != 0 else 0

        paddings = (w_pad_len // 2, w_pad_len - w_pad_len // 2, h_pad_len // 2, h_pad_len - h_pad_len // 2)
        unpaddings = (0 - (w_pad_len // 2), 0 - (w_pad_len - w_pad_len // 2), 0 - (h_pad_len // 2), 0 - (h_pad_len - h_pad_len // 2))

        h_pad_len = paddings[2] + paddings[3]
        w_pad_len = paddings[0] + paddings[1]
        padded_size = (h + h_pad_len, w + w_pad_len)

        return {
            "ori_size": ori_size,
            "paddings": paddings,
            "unpaddings": unpaddings,
            "padded_size": padded_size,
        }


def image_padding(img, pad_info):
    paddings = pad_info['paddings']
    padded_img = F.pad(img, paddings, mode='constant', value=0)
    return padded_img


def image_unpadding(img, pad_info):
    unpaddings = pad_info['unpaddings']
    unpadded_img = F.pad(img, unpaddings)
    return unpadded_img


# device = 'cuda' if torch.cuda.is_available() else 'cpu'
device = 'cpu'
metric = 'mse'

qp_list = [1, 2, 3, 4, 5, 6]


results = {}

###############################3
for qp in qp_list:
    network = cheng2020_attn(quality=qp, pretrained=True).eval().to(device)
    # network = bmshj2018_hyperprior(quality=qp, pretrained=True).eval().to(device)

    print(f"==========QP{qp}==========")
    file_path = "/home/vmlab/project_sh/sun/jpeg/aia.lev1_euv_12s.2012-01-04T120001Z.171.image_lev1_AR.yuv"
    height = 644
    width = 1044


    yuv_data = read_yuv400_file(file_path, height, width)
    x = yuv400_to_rgb(yuv_data, width, height).to(device)
    _, _, h, w = x.size()
    pad_info = cal_image_padding_size((h, w))

    x_max = torch.max(x)
    x = x / x_max

    x_pad = image_padding(x, pad_info)

    with torch.no_grad():
        encoded = network.compress(x_pad)
        strings = encoded['strings']
        shape = encoded['shape']

        y = len(strings[0][0]) * 8
        z = len(strings[1][0]) * 8
        bpp = (y + z) / (height * width)
        print("BPP:", bpp)

        y_string = strings[0]
        z_string = strings[1]

        strings = [y_string, z_string]

        x_hat = network.decompress(strings, shape)['x_hat']
        x_hat = image_unpadding(x_hat, pad_info)

        x = x * x_max
        x_hat = x_hat * x_max

        mse, psnr = compute_psnr(x, x_hat)

        print(mse, psnr)

    results[f'QP{qp}_BPP:'] = bpp
    results[f'QP{qp}_PSNR:'] = psnr

print(results)

