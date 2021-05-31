# -*- coding: utf-8 -*-
import GlobalModule
from PIL import Image, ImageDraw
import numpy as np

coordenadas = None


def clic_DBorder(event):
    global coordenadas
    x, y = event.x, event.y
    x, y = round(x / GlobalModule.GUI.escala_P), round(
        y / GlobalModule.GUI.escala_P)
    inverted_image = GlobalModule.GUI.data["inverted_image"]
    #count=GlobalModule.GUI.data["count"]
    temp = Image.new(
        'L', (len(GlobalModule.GUI.data["count"][0]),
              len(GlobalModule.GUI.data["count"])),
        color=255)
    CG = GlobalModule.GUI.data["CG"]
    Ax = GlobalModule.GUI.data["Ax"]
    guttas = GlobalModule.GUI.data["guttas"]

    if coordenadas:
        x1, y1 = coordenadas
        draw = ImageDraw.Draw(temp)
        draw.line((x1, y1, x, y), fill=0)
        draw2 = ImageDraw.Draw(inverted_image)
        draw2.line((x1, y1, x, y), fill=0)
        temp = np.array(temp)
        inverted_image_array = np.array(inverted_image)
        for i in range(len(GlobalModule.GUI.data["count"])):
            for j in range(len(GlobalModule.GUI.data["count"][0])):
                if temp[i][j] == 0:
                    GlobalModule.GUI.data["count"][i][j] = 0
                    Ax[i][j] = 0
                    GlobalModule.GUI.data["Ax"][i][j] = 0
                    CG[i][j] = 0
                    GlobalModule.GUI.data["CG"][i][j] = 0
                    guttas[i][j] = 0
                    GlobalModule.GUI.data["guttas"][i][j] = 0
                    GlobalModule.GUI.data["LG"][i][j] = 0
                    inverted_image_array[i][j] = 0

        inverted_image = Image.fromarray(inverted_image_array)
        GlobalModule.did_something = True
        imagen_actual = Image.fromarray(GlobalModule.GUI.data["Ax"])
        iw, ih = imagen_actual.size
        size = int(iw * GlobalModule.GUI.escala_P), int(
            ih * GlobalModule.GUI.escala_P)
        imagen_actual = imagen_actual.resize(size, Image.ANTIALIAS)

        GlobalModule.GUI.data["imagen_actual"] = imagen_actual
        GlobalModule.GUI.data["inverted_image"] = inverted_image
        #GlobalModule.GUI.data["count"]=count
        #GlobalModule.GUI.update_values_GUI(GlobalModule.GUI.data)
        GlobalModule.did_something = True
        j = Image.fromarray(GlobalModule.GUI.data["count"].astype(np.uint8))
        coordenadas = x, y
    else:
        coordenadas = x, y
    GlobalModule.GUI.update_values_GUI(GlobalModule.GUI.data)
