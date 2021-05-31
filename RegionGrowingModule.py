# -*- coding: utf-8 -*-
try:
    import cv2
except:
    print("ERROR! You need to install OpenCV to run this software")
import numpy as np
import PIL
import scipy.ndimage as ndimage
import PIL.ImageOps
from skimage.measure import label
from skimage import io
import scipy as sp
from PIL import Image
import warnings

###IGNORE WARNINGS###
warnings.filterwarnings("ignore")
temp_folder = "tmp"
temp_folder = temp_folder + "/"

#TOLERANCE:
tolerance = 20


def region_growing(img, seed):
    outimg = np.zeros_like(img)
    valor = img[seed[0], seed[1]]

    try:
        for i in range(len(img)):
            for j in range(len(img[0])):
                outimg[i, j] = img[i, j] - valor
                #print (outimg[i,j])
                outimg[i, j] = abs(outimg[i, j])
                if outimg[i, j] < tolerance:
                    outimg[i, j] = 255
                else:
                    outimg[i, j] = 0

    except KeyboardInterrupt:
        pass
    return outimg


def on_mouse(event, x, y, flags, params):
    global clicks
    if event == cv2.EVENT_LBUTTONDOWN:
        clicks.append([y, x])


clicks = []


def imAdjust(img):
    #-----Converting image to LAB Color model-----------------------------------
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)

    #-----Splitting the LAB image to different channels-------------------------
    l, a, b = cv2.split(lab)

    #-----Applying CLAHE to L-channel-------------------------------------------
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)

    #-----Merge the CLAHE enhanced L-channel with the a and b channel-----------
    limg = cv2.merge((cl, a, b))

    #-----Converting image from LAB Color model to RGB model--------------------
    imgFinal = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    imgFinal = cv2.cvtColor(imgFinal, cv2.COLOR_BGR2GRAY)
    return imgFinal


LL = 0


def guttae_seed_border(img, seed, guttas):
    global LL
    print("Processing...")
    img = imAdjust(img)
    label_G = label(io.imread(temp_folder + "guttas.png", as_gray=True), 4)
    out = region_growing(img, seed)
    ret, out = cv2.threshold(out, 0, 255, cv2.THRESH_BINARY)
    SA = np.zeros((3, 3), dtype=np.int)
    SA_2 = np.zeros((5, 5), dtype=np.int)
    SA_3 = np.zeros((9, 9), dtype=np.int)
    SA[1, 0:3] = 1
    SA[0, 1] = 1
    SA[2, 1] = 1
    SA_2[2, :] = 1
    SA_2[1:4, 1:4] = 1
    SA_2[:, 2] = 1
    SA_3[4, :] = 1
    SA_3[1:8, 3:6] = 1
    SA_3[2:7, 2:7] = 1
    SA_3[3:6, 1:8] = 1
    SA_3[:, 4] = 1

    out2 = PIL.Image.fromarray(out)
    out = label(out, 4)
    out = ndimage.binary_opening(out.astype(np.uint8), SA).astype(np.uint8)
    out3 = PIL.Image.fromarray(out.astype(np.uint8))
    out3 = out3.point(lambda p: (p > 0) and 255)

    out = ndimage.binary_closing(out.astype(np.uint8), SA_3).astype(np.uint8)
    out2 = PIL.Image.fromarray(out.astype(np.uint8))
    out2 = out2.point(lambda p: (p > 0) and 255)

    main_image = np.zeros_like(out2)
    out2.save(temp_folder + "labelOut.png")
    labelOut = label(io.imread(temp_folder + "labelOut.png", as_gray=True), 4)
    LL = labelOut
    for i in range(len(main_image)):
        for j in range(len(main_image[0])):
            if labelOut[seed[0], seed[1]] == labelOut[i, j]:
                main_image[i, j] = 255
    main_image = Image.fromarray(main_image)
    main_image = flood_fill(main_image)
    main_image = Image.fromarray(main_image)
    filled = main_image
    filled_array = np.array(filled)
    touch_guttas = []
    for i in range(len(filled_array)):
        for j in range(len(filled_array[0])):
            if filled_array[i][j] != 0 and guttas[i][j] != 0 and label_G[i][j] not in touch_guttas:
                touch_guttas.append(label_G[i][j])

    for i in range(len(label_G)):
        for j in range(len(label_G[0])):
            if label_G[i][j] in touch_guttas:
                filled_array[i][j] = 255

    filled_array = out = ndimage.binary_closing(
        filled_array.astype(np.uint8), SA_3).astype(np.uint8)
    filled = Image.fromarray(filled_array)
    filled = filled.point(lambda p: (p > 0) and 255)
    main_image = filled
    out2 = main_image.filter(PIL.ImageFilter.FIND_EDGES)
    out2 = np.array(out2) * 255
    outimg2 = np.array(img)
    borde = np.zeros_like(img)
    for i in range(len(out2)):
        for j in range(len(out2[0])):
            if out2[i][j] != 0:
                outimg2[i][j] = 255
                borde[i][j] = 255

    ret, out = cv2.threshold(out2, 0, 255, cv2.THRESH_BINARY)
    dilate = ndimage.binary_dilation(out, SA_2).astype(np.uint8)
    dilate = PIL.Image.fromarray(dilate * 255)
    dilate2 = dilate.filter(PIL.ImageFilter.FIND_EDGES)
    dilate2 = np.array(dilate2) * 255
    dilate2 = PIL.Image.fromarray(dilate2 * 128)
    dilate2 = np.array(dilate2)

    for i in range(len(out2)):
        for j in range(len(out2[0])):
            if dilate2[i][j] != 0:
                borde[i][j] = 128

    borde = PIL.Image.fromarray(borde)
    out2 = PIL.Image.fromarray(out2 * 255)
    print("Finish")
    return out2, filled


def flood_fill(test_array, h_max=255):
    input_array = np.copy(test_array)
    el = sp.ndimage.generate_binary_structure(2, 2).astype(np.int)
    inside_mask = sp.ndimage.binary_erosion(
        ~np.isnan(input_array), structure=el)
    output_array = np.copy(input_array)
    output_array[inside_mask] = h_max
    output_old_array = np.copy(input_array)
    output_old_array.fill(0)
    el = sp.ndimage.generate_binary_structure(2, 1).astype(np.int)
    while not np.array_equal(output_old_array, output_array):
        output_old_array = np.copy(output_array)
        output_array = np.maximum(input_array,
                                  sp.ndimage.grey_erosion(
                                      output_array, size=(3, 3), footprint=el))
    return output_array
