# crop landscape image to aspect ration 16:9


import cv2 as cv
import errno
import numpy as np
import sys
from matplotlib import pyplot as plt
import os

VERTICAL = 1
HORIZONTAL = 0


def _volume_crop(img):
    height, width = img.shape
    crop_direction = -1
    number_pixels_to_crop = 0
    if float(width) / float(height) - (16.0 / 9.0) > 0.1:
        crop_direction = VERTICAL
        number_pixels_to_crop = width - (16.0 / 9.0) * height
    elif float(width) / float(height) - (16.0 / 9.0) < -0.1:
        crop_direction = HORIZONTAL
        number_pixels_to_crop = height - (9.0 / 16.0) * width

    return crop_direction, int(number_pixels_to_crop)


def smart_crop(image):
    direction, num = _volume_crop(image)
    if direction == 0:
        rows = _crop_horizontal(_laplacian_(image), num)
        return image[rows[0]: rows[1], :]
    elif direction == 1:
        columns = _crop_vertical(_laplacian_(image), num)
        return image[:, columns[0]:columns[1]]
    else:
        return image


def smart_crop_opt(image):
    direction, num = _volume_crop(image)
    if direction == 0:
        rows = _crop_horizontal_optimal(_laplacian_(image), num)
        return image[rows[0]: rows[1], :]


def _laplacian_(image):
    laplacian = cv.Laplacian(image, cv.CV_64F)
    abs_laplacian = np.absolute(laplacian)
    laplacian_8u = np.uint8(abs_laplacian)

    # plt.imshow(laplacian_8u, cmap='gray')
    # plt.show()
    return laplacian_8u


def _crop_horizontal(edge_image, num):
    top = edge_image[0:num, :]
    bottom = edge_image[edge_image.shape[0] - num: edge_image.shape[0], :]

    top_sum = top.sum(axis=1)
    bottom_sum = bottom.sum(axis=1)

    min_cost = sys.maxint
    crop = [0, 0]
    # crop top
    cost_top = top_sum.sum()
    if cost_top < min_cost:
        crop[0] = num + 1
        crop[1] = edge_image.shape[0]
        min_cost = cost_top

    # crop bottom
    cost_bottom = bottom_sum.sum()
    if cost_bottom < min_cost:
        crop[0] = 0
        crop[1] = edge_image.shape[0] - num - 1
        min_cost = cost_bottom

    # half-half
    cost_hh = top_sum[0: top_sum.shape[0] / 2].sum() + bottom_sum[bottom_sum.shape[0] / 2:bottom_sum.shape[0]].sum()
    if cost_hh < min_cost:
        crop[0] = num / 2 + 1
        crop[1] = edge_image.shape[0] - num / 2 - 1

    return crop


def _crop_horizontal_optimal(edge_image, num):
    height = edge_image.shape[0]
    min_cost = sys.maxint
    crop = [0, 0]
    for p in range(0, num):
        cost = edge_image[0:p, :].sum() + edge_image[height - num + p: height, :].sum()
        if cost < min_cost:
            min_cost = cost
            crop[0] = p
            crop[1] = height - num + p

    return crop


def _crop_vertical(edge_image, num):
    width = edge_image.shape[1]
    left = edge_image[:, 0:num]
    right = edge_image[:, width - num: width]

    left_sum = left.sum(axis=1)
    right_sum = right.sum(axis=1)

    min_cost = sys.maxint
    crop = [0, 0]
    # crop left
    cost_left = left_sum.sum()
    if cost_left < min_cost:
        crop[0] = num + 1
        crop[1] = width

    # crop right
    cost_right = right_sum.sum()
    if cost_right < min_cost:
        crop[0] = 0
        crop[1] = width - num - 1

    # half-half
    cost_hh = left_sum[0: len(left_sum) / 2].sum() + right_sum[len(right_sum) / 2: len(right_sum)].sum()
    if cost_hh < min_cost:
        crop[0] = num / 2 + 1
        crop[1] = width - num / 2 - 1

    return crop


def compare_crop(imagefile, filename):
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.mkdir(os.path.dirname(filename))
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise

    original_image = cv.imread(imagefile, 0)
    cropped_image = smart_crop(original_image)

    plt.subplot(1, 2, 1)
    plt.imshow(original_image, cmap='gray')
    plt.title('original')
    plt.xticks([]), plt.yticks([])

    plt.subplot(1, 2, 2)
    plt.imshow(cropped_image, cmap='gray')
    plt.title('cropped')
    plt.xticks([]), plt.yticks([])

    plt.savefig(filename, bbox_inches='tight')


def show_crop(imagefile):
    original_image = cv.imread(imagefile, 0)
    cropped_image = smart_crop(original_image)

    plt.subplot(1, 2, 1)
    plt.imshow(original_image, cmap='gray')
    plt.title('original')
    plt.xticks([]), plt.yticks([])

    plt.subplot(1, 2, 2)
    plt.imshow(cropped_image, cmap='gray')
    plt.title('cropped')
    plt.xticks([]), plt.yticks([])
    plt.show()


if __name__ == '__main__':
    # show_crop('/Users/jge/PycharmProjects/imageOpt/data/10312/Hotel Front - Evening/Night/large100010919414.jpg')
    show_crop('/Users/jge/PycharmProjects/imageOpt/data/10534/Meeting Facility/large10008715640.jpg')
