# -*- coding: utf-8 -*-
from PIL import Image
import numpy as np
import GlobalModule

x, y = 0, 0


def clic_cell(event):
    global x, y
    x, y = event.x, event.y
    x, y = round(x / GlobalModule.GUI.escala_P), round(
        y / GlobalModule.GUI.escala_P)
    GlobalModule.did_something = True
    Seleccionar_cell()


def Seleccionar_cell():
    Ax = GlobalModule.GUI.data["Ax"]
    Imagen_Segmentacion = GlobalModule.GUI.data["Imagen_Segmentacion"]
    guttas = GlobalModule.GUI.data["guttas"]
    LG = GlobalModule.GUI.data["LG"]
    CG = GlobalModule.GUI.data["CG"]
    count = GlobalModule.GUI.data["count"]
    imagen = Image.open(GlobalModule.GUI.file_path)
    temp = np.array(imagen.convert("L"))
    if (count[y][x] > 1):
        for i in range(len(count)):
            for j in range(len(count[0])):
                if count[i][j] == count[y][x]:
                    guttas[i][j] = 0
                    Ax[i][j] = temp[i][j]
                    LG[i][j] = count[i][j] - 1
                    CG[i][j] = count[i][j] - 1
    GlobalModule.GUI.data["Imagen_Segmentacion"] = Imagen_Segmentacion
    GlobalModule.GUI.data["guttas"] = guttas
    GlobalModule.GUI.data["LG"] = LG
    GlobalModule.GUI.data["CG"] = CG
    GlobalModule.GUI.data["count"] = count
    GlobalModule.GUI.data["Ax"] = Ax
    imagen_actual = Image.fromarray(Ax)
    iw, ih = imagen_actual.size
    size = int(iw * GlobalModule.GUI.escala_P), int(
        ih * GlobalModule.GUI.escala_P)
    imagen_actual = imagen_actual.resize(size, Image.ANTIALIAS)
    GlobalModule.GUI.data["imagen_actual"] = imagen_actual
    GlobalModule.GUI.update_values_GUI(GlobalModule.GUI.data)
