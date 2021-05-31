# -*- coding: utf-8 -*-

from PIL import Image, ImageOps
import GlobalModule
from RegionGrowingModule import guttae_seed_border
import cv2
import numpy as np
from skimage import io
from skimage.measure import label
temp_folder = "tmp/"


def clic_Guttae_S(event):
    GlobalModule.did_something = True
    x, y = event.x, event.y
    x, y = round(x / GlobalModule.GUI.escala_P), round(y / GlobalModule.GUI.escala_P)
    GlobalModule.ventana.after_cancel(GlobalModule.GUI.after_id)
    GlobalModule.GUI.normal_update = True
    antes = GlobalModule.GUI.texto
    GlobalModule.GUI.texto = "Please wait..."
    GlobalModule.GUI.color = "black"
    GlobalModule.ventana.update_idletasks()
    hh = Image.open(GlobalModule.GUI.file_path)

    hh = hh.crop((12, 0, 256, 476))
    hh.save(temp_folder + "toGrow.png")
    hh = cv2.imread(temp_folder + 'toGrow.png', 1)
    guttas = GlobalModule.GUI.data["guttas"]
    temporal, filled = guttae_seed_border(hh, [y, x], guttas)
    #imagen_actual2=np.array(imagen_actual2)
    temporal = np.array(temporal)
    filled = np.array(filled)
    im = Image.open(GlobalModule.GUI.file_path)
    im.seek(0)
    Ax2 = im.crop((12, 0, 256, 477))
    Ax2 = Ax2.convert("L")
    Ax2 = np.array(Ax2)
    Ax_Original = Ax2.copy()
    segmen = io.imread(temp_folder + "SegmentacionInversa.png", as_gray=True)
    seg_normal = ImageOps.invert(
        Image.open(
            GlobalModule.dir_path + temp_folder + "SegmentacionInversa.png"))
    seg_normal = np.array(seg_normal)
    temp3 = temporal
    temp3 = np.delete(x, (-1), axis=0)
    resul = np.subtract(temp3, seg_normal * 255)
    resul = Image.fromarray(resul * 255)
    Ax = GlobalModule.GUI.data["Ax"]

    for i in range(len(temporal)):
        for j in range(len(temporal[0])):
            if temporal[i, j] != 0:
                #Ax[i,j]=0
                segmen[i][j] = 0
            elif filled[i][j] != 0:
                guttas[i][j] = 255
                #count[i][j]=count[y][x]
                segmen[i][j] = 255
                Ax[i][j] = Ax2[i][j]

    ju = Image.fromarray(guttas.astype(np.uint8) * 255)
    ju = ju.point(lambda p: (p > 0) and 255)
    ju.save(temp_folder + "guttas.png")
    GlobalModule.GUI.data["count"] = label(segmen, 4)

    for i in range(len(segmen)):
        for j in range(len(segmen[0])):
            if ((segmen[i][j] != 255)):
                Ax[i][j] = 0
                Ax2[i][j] = 0
                Ax_Original[i][j] = 0
            if guttas[i][j] == 255:
                aux = Ax_Original[i][j] - 30
                if aux < 0:
                    aux = 0
                Ax[i][j] = aux
    GlobalModule.GUI.data["Imagen_Segmentacion"] = Image.fromarray(Ax2)
    segmen = Image.fromarray(segmen)
    GlobalModule.GUI.data["inverted_image"] = segmen.copy()

    ju = Image.fromarray(guttas.astype(np.uint8) * 255)
    ju = ju.point(lambda p: (p > 0) and 255)
    ju.save(temp_folder + "guttas.png")
    GlobalModule.GUI.data["Ax"] = Ax
    GlobalModule.GUI.texto = antes
    GlobalModule.GUI.normal_update = False
    GlobalModule.GUI.after_id = GlobalModule.ventana.after(
        GlobalModule.GUI.timeout, GlobalModule.GUI.update_GUI_messages)
