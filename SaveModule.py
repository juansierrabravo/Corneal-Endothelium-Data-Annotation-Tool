# -*- coding: utf-8 -*-

from PIL import Image
import numpy as np
import GlobalModule


def save():
    if GlobalModule.GUI.guardo:
        save_as(just_save=True)
    else:
        save_as()


def pasarRGB(K):
    if 'P' in str(K.mode):
        K=K.convert('RGB')
        
    colores = [[255, 255, 255], [255, 255, 85], [255, 87, 207], [255, 85, 85],
               [85, 255, 255], [84, 254, 80], [88, 86, 247], [84, 84, 84],
               [167, 167, 167], [167, 85, 13], [172, 0, 195], [170, 0, 0],
               [4, 174, 161], [0, 174, 0], [0, 6, 147], [0, 0, 0]]
    equivalencias = {
        "15": 0,
        "14": 1,
        "13": 2,
        "12": 3,
        "11": 4,
        "10": 5,
        "9": 6,
        "8": 7,
        "7": 8,
        "6": 9,
        "5": 10,
        "4": 11
    }
    
    ktemp = np.array(K)
    for i in range(len(ktemp)):
        for j in range(len(ktemp[0])):
            try:
                numero = ktemp[i][j][0]
            except IndexError:
                numero = ktemp[i][j]
            try:
                ktemp[i][j] = colores[equivalencias[str(numero)]]
            except KeyError:
                return K
    ktemp = Image.fromarray(ktemp)
    return ktemp


def traductor(cadena, dic, tipo="normal"):
    tamano = len(cadena)
    imagenNuevo = Image.new("RGB", (8 * tamano, 8), color=0)
    letraActual = 0
    if tipo == "normal":
        for letra in cadena:
            imagenNuevo.paste(dic[letra], [letraActual * 8, 0])
            letraActual += 1

    elif tipo == "grande":
        imagenNuevo = Image.new("RGB", (9 * tamano, 11), color=0)
        for letra in cadena:
            imagenNuevo.paste(dic[letra], [letraActual * 9, 0])
            letraActual += 1

    else:
        raise ValueError("\"" + tipo + "\" is not a valid type to translate")

    return imagenNuevo


diccionarioA = {}
diccionarioB = {}
digits = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "."]
for digit in digits:
    diccionarioA[digit] = Image.open(
        GlobalModule.dir_path + "/files/diccionario/A/" + digit + ".png")
    diccionarioB[digit] = Image.open(
        GlobalModule.dir_path + "/files/diccionario/B/" + digit + "a.png")


def cal_intersecciones():
    count = GlobalModule.GUI.data["count"]
    guttas = GlobalModule.GUI.data["guttas"]

    inter = np.full_like(count, 4)
    #inter[:][:]=4
    for i in range(len(count)):
        for j in range(len(count[0])):
            if len(guttas) > 0:
                if guttas[i][j] == 255:
                    inter[i][j] = 6
            vecinos = []
            if count[i][j] == 0:
                inter[i][j] = 12
                try:
                    if count[i - 1][j] not in vecinos:
                        vecinos.append(count[i - 1][j])
                except IndexError:
                    pass

                try:
                    if count[i + 1][j] not in vecinos:
                        vecinos.append(count[i + 1][j])
                except IndexError:
                    pass

                try:
                    if count[i][j - 1] not in vecinos:
                        vecinos.append(count[i][j - 1])
                except IndexError:
                    pass

                try:
                    if count[i][j + 1] not in vecinos:
                        vecinos.append(count[i][j + 1])
                except IndexError:
                    pass

                try:
                    if count[i - 1][j - 1] not in vecinos:
                        vecinos.append(count[i - 1][j - 1])
                except IndexError:
                    pass

                try:
                    if count[i - 1][j + 1] not in vecinos:
                        vecinos.append(count[i - 1][j + 1])
                except IndexError:
                    pass

                try:
                    if count[i + 1][j + 1] not in vecinos:
                        vecinos.append(count[i + 1][j + 1])
                except IndexError:
                    pass

                try:
                    if count[i + 1][j - 1] not in vecinos:
                        vecinos.append(count[i + 1][j - 1])
                except IndexError:
                    pass

                if len(vecinos) >= 4:
                    inter[i][j] = 14
    inter = Image.fromarray(np.uint8(inter))
    inter = inter.convert("RGB")
    inter = pasarRGB(inter)
    return inter


def escribir(escribir_sobre, datos=0, coords=0):
    sobre = escribir_sobre.copy()

    if datos == 0:
        datos = [
            149.0, 14879.0, 1764.9, 1469.0,0, 2800.0, 1.0, 2.0, 3.0, 4.0,0, 5.0,200
        ]
    else:
        for i in range(len(datos)):
            datos[i] = float(round(datos[i], 1))

    if coords == 0:
        coords = [[566, 114], [566, 130], [566, 146], [566, 162], [566, 178], [566, 198]]
        coords += [[566, 114 + 130], [566, 130 + 130], [566, 146 + 130],
                   [566, 162 + 130], [566, 178 + 130], [566, 198 + 130],[566, 395]]

    if len(datos) != len(coords):
        raise ValueError("Sizes do not match")

    for i in range(len(datos)):
        if i == 5 or i == 11:
            sobre.paste(
                traductor(str(datos[i]), diccionarioB, "grande"),
                [coords[i][0] - (len(str(datos[i])) * 9), coords[i][1]])
        else:
            sobre.paste(
                traductor(str(datos[i]), diccionarioA),
                [coords[i][0] - (len(str(datos[i])) * 8), coords[i][1]])

    sobre.paste(cal_intersecciones(), [12, 0])
    return sobre


def save_as(just_save=False):

    coordenadas_borrar = [[324, 76, 575, 172], [496, 176, 576, 195],
                          [332, 198, 637, 394], [324, 161, 581, 174],
                          [437, 240, 437, 254], [477, 182, 492, 192]]

    if just_save:
        guardar_en = GlobalModule.GUI.trabajando_sobre + ".tif"

    else:

        guardar_en = GlobalModule.GUI.saveBox(just_save)
    if guardar_en == "":
        return

    GlobalModule.GUI.config_buttons(buttons=["Select_F"], state="disable")
    GlobalModule.GUI.Introduce_CD_entry.config(state="disabled")

    im = Image.open(GlobalModule.GUI.file_path)
    imChannel1 = im.copy()
    im.seek(1)

    NuevoTIFF = im.copy()
    print ('MODO DE LA IMAGEN:',NuevoTIFF.mode)
    if 'P' in str(NuevoTIFF.mode):
        NuevoTIFF=NuevoTIFF.convert('RGB')
    
    im.seek(0)

    im.seek(1)
    imChannel2 = im
    imChannel3 = im.copy()
    NuevoTIFF = np.array(NuevoTIFF)
    rojo = NuevoTIFF[467 - 1][393 - 1]
    NN = im.convert("P")
    rojoPixel = np.array(NN)
    rojoPixel = rojoPixel[467 - 1][393 - 1]
    for coor in coordenadas_borrar:
        for x in range(coor[0], coor[2] - 1):
            for y in range(coor[1], coor[3] - 1):
                NuevoTIFF[y][x] = rojo

    NuevoTIFF = Image.fromarray(NuevoTIFF)
    seg = np.array(GlobalModule.GUI.data["inverted_image"])
    w, h = im.size
    try:
        segmen = Image.new("RGB", (w, h), (rojo[0], 0, 0))
    except IndexError:
        segmen = Image.new("RGB", (w, h), (rojo, 0, 0))
    segmen = np.array(segmen)
    for i in range(len(seg)):
        for j in range(len(seg[0])):
            if seg[i][j] < 100:
                segmen[i][j] = [255, 255, 255]
            else:
                pass
                #segmentacion[i][j]=0
    NuevoTIFF = Image.fromarray(segmen).crop((12, 0, 256, 477))

    
    NuevoTIFF = NuevoTIFF.convert("RGB")
    NuevoTIFF = pasarRGB(NuevoTIFF)
    plantilla = Image.open(
        GlobalModule.dir_path + "/files/plantilla.png").crop(
            [340, 69, 637, 455])
    imChannel2 = pasarRGB(imChannel2)
    imChannel2.paste(NuevoTIFF, [24, 0])
    imChannel2 = pasarRGB(imChannel2)
    imChannel2.paste(plantilla, [340, 69])
    imChannel2 = imChannel2.convert("RGB")

    datos = [
        GlobalModule.GUI.data["NC"], GlobalModule.GUI.data["Min_Size"],
        GlobalModule.GUI.data["Max_Size"], GlobalModule.GUI.data["Average"],
        GlobalModule.GUI.data["Area_ratio"],GlobalModule.GUI.data["New_CD"]
    ]
    datos += [
        GlobalModule.GUI.data["NG"],
        GlobalModule.GUI.data["Min_Size_G"],
        GlobalModule.GUI.data["Max_Size_G"],
        GlobalModule.GUI.data["Average_G"],
        GlobalModule.GUI.data["Area_ratio_G"],
        GlobalModule.GUI.data["GD"]
    ]
    datos += [
        GlobalModule.GUI.data["Total_Area"]
    ]
    imChannel2 = escribir(imChannel2, datos)
    guttas = GlobalModule.GUI.data["guttas"]

    for i in (range(len(guttas))):
        for j in range(len(guttas[0])):
            if guttas[i, j] != 0:
                pass  #imChannel2.putpixel((j+12,i),(120,120,120))

    Referencia = imChannel3.getpixel((419, 474))

    if type(Referencia) == type(1):
        imChannel3 = imChannel3.point(lambda p: (p > 4) and 255)
        for i in (range(len(guttas))):
            for j in range(len(guttas[0])):
                if guttas[i, j] != 0:
                    imChannel3.putpixel((j + 12, i), 0)

    else:
        ix, u = imChannel3.size

        for i in range(ix):
            for j in range(u):
                if imChannel3.getpixel(
                    (i, j))[0] > 170 or (imChannel3.getpixel(
                        (i, j))[0] >= 80 and imChannel3.getpixel(
                            (i, j))[0] <= 90):
                    imChannel3.putpixel((i, j), (255, 255, 255))
                else:
                    imChannel3.putpixel((i, j), (0, 0, 0))

        for i in (range(len(guttas))):
            for j in range(len(guttas[0])):
                if guttas[i, j] != 0:
                    imChannel3.putpixel((j + 12, i), (0, 0, 0))

    imChannel3 = imChannel3.convert("RGB")
    imChannel3.paste(imChannel1.crop([0, 0, 320, 480]), [0, 0])
    to_paste=Image.fromarray(GlobalModule.GUI.Ax_Inicial)
    imChannel3.paste(to_paste,[12,0])

    imlist = [imChannel1, imChannel2, imChannel3]
    print(guardar_en)
    imlist[0].save(
        guardar_en,
        compression="tiff_deflate",
        save_all=True,
        append_images=imlist[1:])
    GlobalModule.GUI.data["nombre_archivo"] = guardar_en[
        guardar_en.rfind("/") + 1:len(guardar_en) - 4]
    #GlobalModule.GUI.update_values_GlobalModule.GUI(data)
    print("Guardado como: ", GlobalModule.GUI.trabajando_sobre)
    GlobalModule.GUI.config_buttons(buttons=["Select_F"], state="normal")
    GlobalModule.GUI.guardo = True
