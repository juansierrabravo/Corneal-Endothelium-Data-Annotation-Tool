# -*- coding: utf-8 -*-
import GlobalModule
from PIL import Image
import numpy as np


def clic_DrawPixel(event):
    x, y = event.x - 2, event.y - 2
    GlobalModule.did_something = True
    #print (" ***Clic en:",event.x, event.y,"***")
    x, y = round(x / GlobalModule.GUI.escala_P), round(y / GlobalModule.GUI.escala_P)
    guttas = GlobalModule.GUI.data["guttas"]
    inverted_image_array = np.array(GlobalModule.GUI.data["inverted_image"])
    if guttas[y][x] != 255:
        GlobalModule.GUI.data["count"][y][x] = 0
        GlobalModule.GUI.data["Ax"][y][x] = 0
        GlobalModule.GUI.data["CG"][y][x] = 0
        GlobalModule.GUI.data["LG"][y][x] = 0
        inverted_image_array[y][x] = 0
        inverted = Image.fromarray(inverted_image_array)
        GlobalModule.GUI.data["inverted_image"] = inverted
        imagen_actual = Image.fromarray(GlobalModule.GUI.data["Ax"])
        iw, ih = imagen_actual.size
        size = int(iw * GlobalModule.GUI.escala_P), int(
            ih * GlobalModule.GUI.escala_P)
        imagen_actual = imagen_actual.resize(size, Image.ANTIALIAS)
        GlobalModule.GUI.data["imagen_actual"] = imagen_actual
        GlobalModule.GUI.update_values_GUI(GlobalModule.GUI.data)
