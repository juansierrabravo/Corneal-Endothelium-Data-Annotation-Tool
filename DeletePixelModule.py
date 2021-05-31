# -*- coding: utf-8 -*-
import GlobalModule
from PIL import Image
import numpy as np


def clic_DeletePixel(event):
    GlobalModule.did_something = True
    x, y = event.x, event.y
    x, y = round(x / GlobalModule.GUI.escala_P), round(
        y / GlobalModule.GUI.escala_P)
    guttas = GlobalModule.GUI.data["guttas"]
    im = Image.open(GlobalModule.GUI.file_path)
    inverted_image_array = np.array(GlobalModule.GUI.data["inverted_image"])
    if guttas[y][x] != 255:
        temp = np.array(im.convert("L"))
        GlobalModule.GUI.data["count"][y][x] = temp[y][x]
        GlobalModule.GUI.data["Ax"][y][x] = temp[y][x]
        GlobalModule.GUI.data["CG"][y][x] = temp[y][x]
        GlobalModule.GUI.data["LG"][y][x] = temp[y][x]
        inverted_image_array[y][x] = temp[y][x]
        inverted = Image.fromarray(inverted_image_array)
        GlobalModule.GUI.data["inverted_image"] = inverted
        imagen_actual = Image.fromarray(GlobalModule.GUI.data["Ax"])
        iw, ih = imagen_actual.size
        size = int(iw * GlobalModule.GUI.escala_P), int(
            ih * GlobalModule.GUI.escala_P)
        imagen_actual = imagen_actual.resize(size, Image.ANTIALIAS)
        GlobalModule.GUI.data["imagen_actual"] = imagen_actual
        GlobalModule.GUI.update_values_GUI(GlobalModule.GUI.data)
