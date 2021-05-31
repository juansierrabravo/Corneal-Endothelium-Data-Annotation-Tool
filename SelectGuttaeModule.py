# -*- coding: utf-8 -*-
import GlobalModule
from PIL import Image
import numpy as np


def Seleccionar_gutta(x, y):
    x, y = round(x / GlobalModule.GUI.escala_P), round(
        y / GlobalModule.GUI.escala_P)
    Ax = GlobalModule.GUI.data["Ax"]
    guttas = GlobalModule.GUI.data["guttas"]
    Ax_Original = GlobalModule.GUI.Ax_Original
    Ax_Original = np.array(Ax_Original.convert("L"))
    count = GlobalModule.GUI.data["count"]
    try:
        if (count[y][x] > 1):
            for i in range(len(count)):
                for j in range(len(count[0])):
                    if count[i][j] == count[y][x]:
                        guttas[i][j] = 255
                        aux = Ax_Original[i][j] - 30
                        if aux < 0:
                            aux = 0
                        Ax[i][j] = aux

        GlobalModule.GUI.data["Ax"] = Ax
        GlobalModule.GUI.data["guttas"] = guttas
        GlobalModule.GUI.data["count"] = count
        imagen_actual = Image.fromarray(Ax)
        iw, ih = imagen_actual.size
        size = int(iw * GlobalModule.GUI.escala_P), int(
            ih * GlobalModule.GUI.escala_P)
        imagen_actual = imagen_actual.resize(size, Image.ANTIALIAS)
        GlobalModule.GUI.data["imagen_actual"] = imagen_actual
        GlobalModule.GUI.update_values_GUI(GlobalModule.GUI.data)
        GlobalModule.GUI.did_something = True
    except (IndexError):
        pass
