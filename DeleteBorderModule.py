# -*- coding: utf-8 -*-
import GlobalModule
from PIL import Image
import numpy as np
import scipy.ndimage as ndimage

coordenadas = None
x, y = 0, 0


def clic_DeleteBorder(imgInterseccion, event=None, coords=None):
    global coordenadas
    GlobalModule.did_something = True
    if event:
        x, y = event.x, event.y
        x, y = round(x / GlobalModule.GUI.escala_P), round(
            y / GlobalModule.GUI.escala_P)

    lineaT = np.array(Image.new("L", (244, 476), color=255))
    count = GlobalModule.GUI.data["count"]
    inverted_image = GlobalModule.GUI.data["inverted_image"]
    a = np.zeros((476, 244), dtype=np.int)
    imOrin = Image.open(GlobalModule.GUI.file_path)
    temp = imOrin.crop((12, 0, 256, 477))
    temp = temp.convert("L")
    temp = np.array(temp)
    

    if coordenadas or coords:
        if coords:
            y1, x1 = coords[0]
            y, x = coords[1]
        else:
            x1, y1 = coordenadas

        label1 = count[y1][x1]
        label2 = count[y][x]

        for i in range(len(count)):
            for j in range(len(count[0])):
                if (count[i][j] == label1
                        or count[i][j] == label2) and count[i][j] != 0:
                    a[i][j] = 255
                    count[i][j] = label2

        SA = np.zeros((3, 3), dtype=np.int)
        SA[1, 0:3] = 1
        SA[0, 1] = 1
        SA[2, 1] = 1
        a_close = ndimage.binary_closing(a, SA).astype(np.uint8)
        iguales = True
        for i in range(len(count)):
            for j in range(len(count[0])):
                if a[i][j] != a_close[i][j] * 255:
                    iguales = False
                    break
            if not iguales:
                break

        if iguales:
            coordenadas = None
            return 1

        else:
            inverted_image_array = np.array(inverted_image)
            for i in range(len(count)):
                for j in range(len(count[0])):
                    if a_close[i][j] != 0:
                        count[i][j] = label2
                        inverted_image_array[i][j] = 255
            inverted_image = Image.fromarray(inverted_image_array)
            a_close_inter = a_close.copy()
            intersecciones = np.array(imgInterseccion)
            for i in range(len(a_close)):
                for j in range(len(a_close[0])):
                    if a_close[i][j] == 1 and intersecciones[i][j] == 255:
                        a_close_inter[i][j] = 255

            for i in range(len(count)):
                for j in range(len(count[0])):
                    if a_close[i][j] * 255 != a[i][j]:
                        lineaT[i][j] = 0

            for i in range(len(a_close)):
                for j in range(len(a_close[0])):
                    if lineaT[i][j] <= 55:
                        count[i][j] = temp[i][j]
                        GlobalModule.GUI.data["Ax"][i][j] = temp[i][j]
                        GlobalModule.GUI.data["CG"][i][j] = temp[i][j]
                        GlobalModule.GUI.data["LG"][i][j] = temp[i][j]

            imagen_actual = Image.fromarray(GlobalModule.GUI.data["Ax"])
            iw, ih = imagen_actual.size
            size = int(iw * GlobalModule.GUI.escala_P), int(
                ih * GlobalModule.GUI.escala_P)
            imagen_actual = imagen_actual.resize(size, Image.ANTIALIAS)
            GlobalModule.GUI.data["imagen_actual"] = imagen_actual
            GlobalModule.GUI.data["count"] = count
            GlobalModule.GUI.data["inverted_image"] = inverted_image
            GlobalModule.GUI.update_values_GUI(GlobalModule.GUI.data)
            GlobalModule.did_something = True
            coordenadas = x, y
            return 2
    coordenadas = x, y
