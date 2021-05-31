# -*- coding: utf-8 -*-
from PIL import Image, ImageTk
import PIL.ImageOps
import numpy as np
from skimage.measure import label, regionprops
from skimage import io
import os
import scipy.ndimage as ndimage

import GlobalModule
from SaveModule import save, save_as
from SelectCellModule import clic_cell
from SelectGuttaeModule import Seleccionar_gutta
from DeletePixelModule import clic_DeletePixel
from DrawPixelModule import clic_DrawPixel
from DeleteBorderModule import clic_DeleteBorder
from DrawBorderModule import clic_DBorder

import DrawBorderModule
import GuttaeSeedModule


def guttae_S():
    GlobalModule.GUI.enable_blink = 1
    if GlobalModule.did_something:
        recalcularTodo()
    GlobalModule.GUI.Introduce_CD_entry.config(state="disabled")
    GlobalModule.GUI.disable_buttons(
        to_disable=["Back", "Forward", "Reset", "Previous", "Next"])
    GlobalModule.GUI.image.bind("<Enter>", sobre_imagen_Guttae_S)
    GlobalModule.GUI.image.bind("<Leave>", no_sobre_imagen)
    GlobalModule.GUI.image.config(cursor="tcross")
    GlobalModule.ventana.bind("<Return>", unbind)


temp_folder = "tmp"

##Setting up temp folder###
dir_path = os.path.dirname(os.path.realpath(__file__))
os.makedirs(os.path.join(dir_path, temp_folder), exist_ok=True)
temp_folder = temp_folder + "/"

historial = {}
variables = [
    "count", "NCG", "NL", "NLG", "NG", "NC", "CD", "guttas",
    "Imagen_Segmentacion", "LG", "CG", "FC", "GD", "Ax", "Area_min",
    "Area_max", "Avg_C", "Area_min_G", "Area_max_G", "Avg_G", "imagen_actual",
    "imagen_actual0", "imagen_actual2", "inverted_image","Area_celulas","Area_guttas","Area_ratio","Area_ratio_G"
]

for var in variables:
    historial[var] = []

NC = 0
FC = 0
CG = 1
NCG = 0
NL = 0
NLG = 0
NG = 0
LG = 0
guttas = 0
ju = 0
Ax = 0
Area_min = 0
Area_max = 0
Avg_C = 0
Area_min_G = 0
Area_max_G = 0
Avg_G = 0
GD = 0
CD = 0  #NC/mm2
count = 0


def sobre_imagen_DB(event):
    global guttas
    GlobalModule.ventana.bind("<Button-1>", clic_con_zoom(event,7))
    GlobalModule.ventana.bind("<MouseWheel>", redraw)
    if GlobalModule.GUI.zoom_enabled==1:
        sobre_imagen_zoom(event)
        

def clic_con_zoom(event,clic):
    if clic==1:
        GlobalModule.ventana.bind("<Button-1>", clic_DeleteP)
    elif clic==2:
        GlobalModule.ventana.bind("<Button-1>", clic_DP)
    elif clic==3:
        GlobalModule.ventana.bind("<Button-1>", clic_DeleteB)
    elif clic==4:
        GlobalModule.ventana.bind("<Button-1>", Guttae_and_update)
	   
    elif clic==5:
        GlobalModule.ventana.bind("<Button-1>", clic_gutta)
	 
    elif clic==6:
        GlobalModule.ventana.bind("<Button-1>", clic_cell)
    
    elif clic==7:
        GlobalModule.ventana.bind("<Button-1>", clic_DB)	 
    
    if GlobalModule.GUI.zoom_enabled==1:
        calcular_zoom(event)
    GlobalModule.GUI.zoom_image.update()
		

    
    
def sobre_imagen_DeleteP(event):
    global guttas
    GlobalModule.ventana.bind("<Button-1>", clic_con_zoom(event,1))
    GlobalModule.ventana.bind("<MouseWheel>", redraw)
    if GlobalModule.GUI.zoom_enabled==1:
        sobre_imagen_zoom(event)
        

def sobre_imagen_DP(event):
    global guttas, en_DP
    GlobalModule.ventana.bind("<Button-1>", clic_con_zoom(event,2))
    #GlobalModule.ventana.bind("<Motion>",mostrar_coordenadas_clic)
    en_DP = 1
    #GlobalModule.ventana.bind("<MouseWheel>",redraw)
    if GlobalModule.GUI.zoom_enabled==1:
        sobre_imagen_zoom(event)
        

def sobre_imagen_zoom(event):
    #GlobalModule.ventana.bind("<MouseWheel>",redraw)
    GlobalModule.ventana.bind("<Motion>", calcular_zoom)

        

def sobre_imagen_DeleteB(event):
    global guttas
    GlobalModule.ventana.bind("<Button-1>", clic_con_zoom(event,3))
    #GlobalModule.ventana.bind("<MouseWheel>",redraw)
    if GlobalModule.GUI.zoom_enabled==1:
        sobre_imagen_zoom(event)
    
    

viejas = 0, 0


def mostrar_coordenadas_clic(event):
    global x, y, viejas
    nuevas = event.x, event.y
    if nuevas[0] == viejas[0] and nuevas[1] == viejas[1]:
        return
    else:
        print("x,y:", nuevas[0], ",", nuevas[1])
        viejas = event.x, event.y


def Guttae_and_update(event):
    GuttaeSeedModule.clic_Guttae_S(event)
    redraw()
    unbind(None, from_guttae_seed=True)


def sobre_imagen_Guttae_S(event):
    GlobalModule.ventana.bind("<Button-1>", clic_con_zoom(event,4))
    #GlobalModule.ventana.bind("<MouseWheel>",redraw)
    if GlobalModule.GUI.zoom_enabled==1:
        sobre_imagen_zoom(event)
        

def no_sobre_imagen(event):
    global guttas, en_DP
    GlobalModule.ventana.bind("<Button-1>", lambda e: None)
    GlobalModule.ventana.bind("<Motion>", lambda e: None)
    #GlobalModule.ventana.bind("<MouseWheel>",lambda e: None)
    en_DP = 0


inverted_image = None

coordenadas = None
imgInterseccion = 0


def clic_DeleteB(event=None, coords=None):
    x = clic_DeleteBorder(imgInterseccion, event)
    if GlobalModule.GUI.zoom_enabled==1:
        calcular_zoom(event)
    if x == 1:
        unbind(None)
    else:
        redraw()


data = {}
Ax = 0


def redraw(event=None):  #,otro=None
    global Imagen_escala, crop_d, Ax, imagen_actual, en_DP, yaCalculo
    #Ax=GlobalModule.GUI.data["Ax"]
    Imagen_escala = Image.fromarray(Ax)
    imagen_actual = Image.fromarray(Ax)
    iw, ih = Imagen_escala.size
    size = int(iw * GlobalModule.GUI.escala_P), int(
        ih * GlobalModule.GUI.escala_P)
    imagen_actual = Imagen_escala.resize(size, Image.ANTIALIAS)
    #paracount=Image.fromarray(np.uint8(count),"L")
    data["imagen_actual"] = imagen_actual


def clic_DB(event):
    clic_DBorder(event)
    if GlobalModule.GUI.zoom_enabled==1:
        calcular_zoom(event)
    redraw()


yaCalculo = 0


def finalDP(event=None):
    global guttas, Ax, imagen_actual, ju, Imagen_Segmentacion, count, coordenadas, inverted_image, x, y, imagen_total_escala, image, imagen_actual2, escala, yaCalculo

    imagen_actual = np.array(GlobalModule.GUI.data["imagen_actual"])

    for i in range(len(Ax)):
        for j in range(len(Ax[0])):
            if imagen_actual[i][j] == 0:
                count[i][j] = 0
                Ax[i][j] = 0
                CG[i][j] = 0
    if yaCalculo == 0:
        redraw()
    if event == 1:
        unbind(None)


def clic_DP(event):
    clic_DrawPixel(event)
    if GlobalModule.GUI.zoom_enabled==1:
        calcular_zoom(event)
    redraw()


def clic_DeleteP(event):
    clic_DeletePixel(event)
    if GlobalModule.GUI.zoom_enabled==1:
        calcular_zoom(event)
    redraw()


def unbind(event, from_guttae_seed=False, by_DB=False, append_to=None):
    global ju, coordenadas, LG, enable_blink
    GlobalModule.GUI.enable_blink = 0
    GlobalModule.GUI.mensajes.config(fg="#F0F0F0")
    #GlobalModule.GUI.config_buttons(buttons=["Select_F"],state="normal")
    GlobalModule.GUI.image.bind("<Enter>", lambda e: None)
    if GlobalModule.GUI.zoom_enabled==1:
        GlobalModule.GUI.image.bind("<Enter>", sobre_imagen_zoom)
    #GlobalModule.GUI.image.bind("<Leave>", lambda e: None)
    #GlobalModule.ventana.bind("<Motion>", lambda e: None)
    GlobalModule.GUI.image.config(cursor="arrow")
    GlobalModule.ventana.bind("<Return>", lambda e: None)
    GlobalModule.ventana.bind("<Button-1>", lambda e: None)
    ju = Image.fromarray(np.uint8(CG), 'L')
    ju = Image.fromarray(np.uint8(LG), 'L')
    ju = Image.fromarray(guttas.astype(np.uint8) * 255)
    ju = ju.point(lambda p: (p > 0) and 255)
    ju.save(GlobalModule.dir_path + "/" + temp_folder + "guttas.png")
    inverted_image = GlobalModule.GUI.data["inverted_image"]
    inverted_image.save(
        GlobalModule.dir_path + "/" + temp_folder + "SegmentacionInversa.png")
    if GlobalModule.did_something:
        recalcularTodo()
    coordenadas = None
    data = GlobalModule.GUI.data

    GlobalModule.GUI.enable_buttons(but=["Next",'Forward'])
    if GlobalModule.did_something:
        recalcularTodo(by_DB=by_DB)
        if from_guttae_seed:
            pass
            #delete_small_cells(append_to)
    GlobalModule.GUI.update_values_GUI(data)


def draw_B():
    GlobalModule.GUI.enable_blink = 1
    GlobalModule.GUI.timeout, GlobalModule.GUI.color = 500, "black"
    GlobalModule.GUI.disable_buttons(but=["Next"])
    GlobalModule.GUI.Introduce_CD_entry.config(state="disabled")
    if GlobalModule.did_something:
        recalcularTodo()
    GlobalModule.GUI.image.bind("<Enter>", sobre_imagen_DB)
    GlobalModule.GUI.image.bind("<Leave>", no_sobre_imagen)
    GlobalModule.GUI.image.config(cursor="tcross")
    GlobalModule.ventana.bind("<Return>",
                              lambda e: unbind(event=e, by_DB=True))


def delete_B():
    global enable_blink
    enable_blink = 1
    GlobalModule.GUI.enable_blink = 1
    GlobalModule.GUI.disable_buttons(but=["Next"])
    GlobalModule.GUI.Introduce_CD_entry.config(state="disabled")
    if GlobalModule.did_something:
        recalcularTodo()
    GlobalModule.GUI.image.bind("<Enter>", sobre_imagen_DeleteB)
    GlobalModule.GUI.image.bind("<Leave>", no_sobre_imagen)
    GlobalModule.GUI.image.config(cursor="tcross")
    GlobalModule.ventana.bind("<Return>", unbind)


def draw_P():
    global enable_blink
    GlobalModule.GUI.enable_blink = 1
    GlobalModule.GUI.disable_buttons(but=["Next"])
    GlobalModule.GUI.Introduce_CD_entry.config(state="disabled")
    #GlobalModule.did_something=False
    if GlobalModule.did_something:
        recalcularTodo()
    GlobalModule.GUI.image.bind("<Enter>", sobre_imagen_DP)
    GlobalModule.GUI.image.bind("<Leave>", no_sobre_imagen)
    GlobalModule.GUI.image.config(cursor="tcross")
    GlobalModule.ventana.bind("<Return>", unbind)  #finalDP(1))


def delete_P():
    global enable_blink
    enable_blink = 1
    GlobalModule.GUI.Introduce_CD_entry.config(state="disabled")
    GlobalModule.GUI.disable_buttons(but=["Next"])
    if GlobalModule.did_something:
        recalcularTodo()
    GlobalModule.GUI.image.bind("<Enter>", sobre_imagen_DeleteP)
    GlobalModule.GUI.image.bind("<Leave>", no_sobre_imagen)
    GlobalModule.GUI.image.config(cursor="tcross")
    GlobalModule.ventana.bind("<Return>", unbind)


NuevoTIFF = 0
NuevoTIFF2 = 0
NuevoTIFFRGB = 0


def Validate_CD(x):
    try:
        x = str(x).replace(',', '.')
        x = float(x)
        if x != 0:
            return x
        else:
            return -1
    except:
        return -1


def actualizarCD(event):
    global CD, CDvalido, nombre_archivo, image, imagen_CD, im, imgCD, imageCD, count, imagen_actual, guttas, LG, FC, NC, CD, enable_blink, texto, timeout, color, after_id, yapaso
    GlobalModule.GUI.mensajes.config(fg="#F0F0F0")
    CDvalido = Validate_CD(GlobalModule.GUI.Introduce_CD_entry.get())
    if CDvalido == -1:
        GlobalModule.GUI.image.focus_set()
        GlobalModule.GUI.Introduce_CD_entry.delete(0, 'end')
        GlobalModule.GUI.texto = "INVALID VALUE! It must be a real number. "
        if GlobalModule.GUI.timeout == 3000:
            GlobalModule.GUI.color = "red"
            GlobalModule.GUI.yapaso = 0
            GlobalModule.GUI.ventana.after_cancel(GlobalModule.GUI.after_id)
            GlobalModule.GUI.after_id = GlobalModule.ventana.after(
                0, GlobalModule.GUI.update_GUI_messages)
        else:
            GlobalModule.GUI.timeout, GlobalModule.GUI.color = 3000, "red"
        return
    #goto(historial,0)
    GlobalModule.GUI.enable_blink = 0
    CD = CDvalido
    suma = 0
    NC = 0
    for region in regionprops(LG):
        NC = NC + 1
        suma = suma + region.area

    FC = 0
    if suma != 0:
        FC = NC / (suma * float(CD))

    GlobalModule.GUI.image.focus_set()
    ###Reactivate all buttons###
    GlobalModule.GUI.enable_buttons(to_enable=[
        "Select_C", "Select_G", "Draw_Border", "Delete_Border", "Draw_Pixel",
        "Delete_Pixel", "Save", "Save_As", "Guttae_S","Zoom"
    ])
    recalcularTodo()


GlobalModule.did_something = False


def recalcularTodo(by_button=False, by_DB=False, by_gutta=False):
    global pos_his_actual, CD
    #GlobalModule.ventana.configure(cursor=cursor_wait)
    guttas = GlobalModule.GUI.data["guttas"]

    LG = GlobalModule.GUI.data["LG"]
    Ax = GlobalModule.GUI.data["Ax"]
    count = GlobalModule.GUI.data["count"]
    DrawBorderModule.coordenadas = None
    if GlobalModule.did_something:
        GlobalModule.did_something = False
    if pos_his_actual > 0:
        GlobalModule.GUI.buttons["Back"].config(state="normal")
    if pos_his_actual < len(historial["CD"]) - 1 and not by_button:
        GlobalModule.GUI.buttons["Forward"].config(state="disabled")
        delete_his_from(pos_his_actual+1)

    GlobalModule.GUI.buttons["Reset"].config(state="normal")
    if CD == 0:
        GlobalModule.ventana.configure(cursor="arrow")
        return 0

    Imagen_Segmentacion_Inversa = io.imread(
        GlobalModule.dir_path + "/" + temp_folder + "SegmentacionInversa.png",
        as_gray=True)

    ju = Image.fromarray(guttas.astype(np.uint8) * 255)

    ju = ju.point(lambda p: (p > 0) and 255)
    SA = np.zeros((3, 3), dtype=np.int)
    SA[1, 0:3] = 1
    SA[0, 1] = 1
    SA[2, 1] = 1
    ju_close = ju.copy()
    ju_close = np.array(ju_close)
    if not by_DB:
        ju_close = ndimage.binary_closing(ju, SA).astype(np.uint8)
    ju_array = ju_close.astype(np.uint8) * 255
    guttas = ju_close.copy()
    ju_close = Image.fromarray(ju_close.astype(np.uint8) * 255)
    ju_close = ju_close.point(lambda p: (p > 0) and 255)
    guttas= np.array(ju_close)
    GlobalModule.GUI.data["guttas"] =guttas
    ju_close = ju_close.convert("RGB")
    ju_close.save(GlobalModule.dir_path + "/" + temp_folder + "guttas.png")
    seg = Image.open(GlobalModule.dir_path + "/" + temp_folder +
                     "SegmentacionInversa.png")  #
    haber = np.array(seg)
    im.seek(0)
    im_to_crop = im.crop((12, 0, 256, 477))
    im_to_crop = im_to_crop.convert("L")
    im_array = np.array(im_to_crop)

    for i in range(len(guttas)):
        for j in range(len(guttas[0])):
            if ju_array[i][j] != 0 and haber[i, j] != 255:
                haber[i][j] = 255
                aux = im_array[i][j] - 30
                if aux < 0:
                    aux = 0
                Ax[i][j] = aux

    inverted_image = Image.fromarray(haber)
    inverted_image.save(
        GlobalModule.dir_path + "/" + temp_folder + "SegmentacionInversa.png")
    Imagen_Segmentacion_Inversa = io.imread(
        GlobalModule.dir_path + "/" + temp_folder + "SegmentacionInversa.png",
        as_gray=True)

    NG = 0
    Area_min_G = 0
    Area_max_G = 0
    suma_G = 0
    pixels_in_segmentation=np.array(Imagen_Segmentacion_Inversa)
    pixels_in_segmentation=np.where( pixels_in_segmentation < 255 )[0]
    #print ("NC CALCULADO:",NC)
    count = label(Imagen_Segmentacion_Inversa, 4)
    label2D = np.array(
        [[0 for i in range(len(count[0]))] for j in range(len(count))])

    for i in range(len(count)):
        for j in range(len(count[0])):
            if (count[i][j] - 1) < 1:
                #label_image[i][j]=[0,0,0]
                label2D[i][j] = 0
            else:
                label2D[i][j] = count[i][j] - 1

    im.seek(1)
    label_G = label(
        io.imread(
            GlobalModule.dir_path + "/" + temp_folder + "guttas.png",
            as_gray=True), 4)
    try:
        Area_min_G = regionprops(label_G)[0].area
    except (IndexError):
        Area_min_G = 0

    for region in regionprops(label_G):
        if region.area > Area_max_G:
            #region_max_G=region.label
            Area_max_G = region.area

        if region.area < Area_min_G:
            #region_min_G=region.label
            Area_min_G = region.area
        suma_G = suma_G + region.area
        NG = NG + 1

    CG = count.copy()
    for i in range(len(count)):
        for j in range(len(count[0])):
            if guttas[i][j] != 0:

                CG[i][j] = 0

    LG = label2D.copy()
    for i in range(len(count)):
        for j in range(len(count[0])):
            if guttas[i][j] != 0:
                LG[i][j] = 0

    NC = len(regionprops(LG))
    NL = NC
    NLG = NC - NG
    NCG = NC - NG
    temporal = Image.fromarray(np.uint8(LG), 'L')
    temporal.save(GlobalModule.dir_path + "/" + temp_folder + "LG.png")
    LG = label(
        io.imread(
            GlobalModule.dir_path + "/" + temp_folder + "LG.png",
            as_gray=True), 4)
    NLG = len(regionprops(LG))
    Area_min = 99999999999
    try:
        Area_min = regionprops(LG)[0].area
    except IndexError:
        pass
    Area_max = 0
    suma = 0
    Area_celulas=0
    
    for region in regionprops(LG):
         #print (dir(region))
        
        Area_celulas=Area_celulas+region.area
        if region.area > Area_max:
            #region_max=region.label
            Area_max = region.area

        if region.area < Area_min:
            #region_min=region.label
            Area_min = region.area
        suma = suma + region.area

    prom_A_c=suma/NC
    try:
        prom_A_g=suma_G/NG
    except ZeroDivisionError:
        prom_A_g=prom_A_c
    porcentaje_eliminacion=10
    min_size=min(prom_A_c,prom_A_g)/100*porcentaje_eliminacion
    min_size=10
    Area_min = 99999999999
    Area_max = 0
    suma = 0
    NC=0
    Area_celulas=0
    
    
    for region in regionprops(LG):
        #if region.area>min_size:
        if len(region.coords)>min_size:
            Area_celulas=Area_celulas+region.area
            if region.area > Area_max:
                #region_max=region.label
                Area_max = region.area
    
            if region.area < Area_min:
                #region_min=region.label
                Area_min = region.area
            suma = suma + region.area
            NC=NC+1

    
    
    NG = 0
    Area_min_G = 99999999999
    Area_max_G = 0
    suma_G = 0
    

    for region in regionprops(label_G):
        
        if region.area>min_size:
            if region.area > Area_max_G:
                #region_max_G=region.label
                Area_max_G = region.area
    
            if region.area < Area_min_G:
                #region_min_G=region.label
                Area_min_G = region.area
            suma_G = suma_G + region.area
            NG = NG + 1
    
    
    if Area_min_G == 99999999999:
        Area_min_G =0
    Area_guttas=suma_G
    Area_celulas=suma
    suma = suma + suma_G
    GD=0
    #Area_ratio_G=Area_guttas/(Area_guttas+Area_celulas)*100
    #Area_ratio=Area_celulas/(Area_guttas+Area_celulas)*100
    pixels=Ax_Original.size
    Area_ratio_G=Area_guttas/(Area_celulas + Area_guttas)*100
    Area_ratio=Area_celulas/(Area_celulas + Area_guttas)*100
    imagen_actual = Image.fromarray(Ax)
    iw, ih = imagen_actual.size
    size = int(iw * GlobalModule.GUI.escala_P), int(
        ih * GlobalModule.GUI.escala_P)
    imagen_actual = imagen_actual.resize(size, Image.ANTIALIAS)
    if suma != 0:
#         CD = NLG / (suma * FC)
        CD = NC / (suma * FC)
    GlobalModule.ventana.configure(cursor="arrow")
    if NC != 0:
        Avg_C = float(Area_celulas) / NC * FC * 10**6
    else:
        Avg_C = 0
    if suma_G != 0:
        GD = NG / (suma * FC)
    if NG != 0:
        Avg_G = float(Area_guttas) / NG * FC * 10**6
    else:
        Avg_G = 0

    if pos_his_actual > 1:
        GlobalModule.GUI.buttons["Back"].config(state="normal")
    if not by_button:
        pos_his_actual += 1
        historial[variables[0]].append(count.copy())
        historial[variables[1]].append(NCG)
        historial[variables[2]].append(NL)
        historial[variables[3]].append(NLG)
        historial[variables[4]].append(NG)
        historial[variables[5]].append(NC)
        historial[variables[6]].append(CD)
        historial[variables[7]].append(guttas.copy())
        historial[variables[8]].append(Imagen_Segmentacion.copy())
        historial[variables[9]].append(LG)
        historial[variables[10]].append(CG)
        historial[variables[11]].append(FC)
        historial[variables[12]].append(GD)
        historial[variables[13]].append(Ax.copy())
        historial[variables[14]].append(Area_min)
        historial[variables[15]].append(Area_max)
        historial[variables[16]].append(Avg_C)
        historial[variables[17]].append(Area_min_G)
        historial[variables[18]].append(Area_max_G)
        historial[variables[19]].append(Avg_G)
        historial[variables[20]].append(imagen_actual)
        historial[variables[21]].append(imagen_actual0)
        historial[variables[22]].append(guttas.copy())
        historial[variables[23]].append(inverted_image.copy())
        historial[variables[24]].append(Area_celulas)
        historial[variables[25]].append(Area_guttas)
        historial[variables[26]].append(Area_ratio)
        historial[variables[27]].append(Area_ratio_G)

    data["New_CD"] = CD
    data["NC"] = NC
    data["Min_Size"] = Area_min * FC * 10**6
    data["Max_Size"] = Area_max * FC * 10**6
    data["Average"] = Avg_C
    data["GD"] = GD
    data["NG"] = NG
    data["Min_Size_G"] = Area_min_G * FC * 10**6
    data["Max_Size_G"] = Area_max_G * FC * 10**6
    data["Total_Area"] = float(Area_celulas + Area_guttas) * FC * 10**6
    data["Guttae_area"]= Area_guttas* FC * 10**6
    data["cell_area"]= Area_celulas* FC * 10**6
    data["Average_G"] = Avg_G
    data["Ax"] = Ax
    data["count"] = count
    data["CG"] = CG
    data["LG"] = LG
    data["Imagen_Segmentacion"] = Imagen_Segmentacion
    data["imagen_actual"] = imagen_actual
    data["inverted_image"] = inverted_image
    data["guttas"] = guttas
    data["Area_guttas"] = Area_guttas
    data["Area_celulas"] = Area_celulas
    data["Area_ratio"] = Area_ratio
    data["Area_ratio_G"] = Area_ratio_G
    
    GlobalModule.GUI.data["New_CD"] = CD
    GlobalModule.GUI.data["NC"] = NC
    GlobalModule.GUI.data["Min_Size"] = Area_min * FC * 10**6
    GlobalModule.GUI.data["Max_Size"] = Area_max * FC * 10**6
    GlobalModule.GUI.data["Average"] = Avg_C
    GlobalModule.GUI.data["GD"] = GD
    GlobalModule.GUI.data["NG"] = NG
    GlobalModule.GUI.data["Min_Size_G"] = Area_min_G * FC * 10**6
    GlobalModule.GUI.data["Max_Size_G"] = Area_max_G * FC * 10**6
    GlobalModule.GUI.data["Average_G"] = Avg_G
    GlobalModule.GUI.data["Ax"] = Ax
    GlobalModule.GUI.data["count"] = count
    GlobalModule.GUI.data["CG"] = CG
    GlobalModule.GUI.data["LG"] = LG
    GlobalModule.GUI.data["Imagen_Segmentacion"] = Imagen_Segmentacion
    GlobalModule.GUI.data["imagen_actual"] = imagen_actual
    GlobalModule.GUI.data["count"] = count
    GlobalModule.GUI.data["inverted_image"] = inverted_image
    GlobalModule.GUI.data["guttas"] = guttas
    GlobalModule.GUI.data["Area_guttas"] = Area_guttas
    GlobalModule.GUI.data["Area_celulas"] = Area_celulas
    GlobalModule.GUI.data["Area_ratio"] = Area_ratio
    GlobalModule.GUI.data["Area_ratio_G"] = Area_ratio_G
    GlobalModule.GUI.data["Total_Area"]=data["Total_Area"]
    

    GlobalModule.GUI.update_values_GUI(data)
    redraw()


rep = 0
Ax_Original = 0


def goto(historial, pos):
    global count, NCG, NL, NLG, NG, NC, CD, guttas, Imagen_Segmentacion, LG, CG, FC, GD, Ax, Area_min, Area_max, Avg_C, Area_min_G, Area_max_G, Avg_G, imagen_actual, imagen_actual0, imagen_actual2, inverted_image, data
    count = historial[variables[0]][pos].copy()
    NCG = historial[variables[1]][pos]
    NL = historial[variables[2]][pos]
    NLG = historial[variables[3]][pos]
    NG = historial[variables[4]][pos]
    NC = historial[variables[5]][pos]
    CD = historial[variables[6]][pos]
    guttas = historial[variables[7]][pos].copy()
    Imagen_Segmentacion = historial[variables[8]][pos].copy()
    LG = historial[variables[9]][pos]
    CG = historial[variables[10]][pos]
    FC = historial[variables[11]][pos]
    GD = historial[variables[12]][pos]
    Ax = historial[variables[13]][pos].copy()
    Area_min = historial[variables[14]][pos]
    Area_max = historial[variables[15]][pos]
    Avg_C = historial[variables[16]][pos]
    Area_min_G = historial[variables[17]][pos]
    Area_max_G = historial[variables[18]][pos]
    Avg_G = historial[variables[19]][pos]
    imagen_actual = historial[variables[20]][pos]
    imagen_actual0 = historial[variables[21]][pos]
    imagen_actual2 = historial[variables[22]][pos]
    
    inverted_image = historial[variables[23]][pos].copy()
    Area_celulas= historial[variables[24]][pos]
    Area_guttas= historial[variables[25]][pos]
    Area_ratio= historial[variables[26]][pos]
    Area_ratio_G= historial[variables[27]][pos]
    inverted_image.save(
        GlobalModule.dir_path + "/" + temp_folder + "SegmentacionInversa.png")

    data["Count"] = count
    data["NCG"] = NCG
    data["NL"] = NL
    data["NLG"] = NLG
    data["NG"] = NG
    data["NC"] = NC
    data["CD"] = CD
    data["guttas"] = guttas
    data["Imagen_Segmentacion"] = Imagen_Segmentacion
    data["LG"] = LG
    data["CG"] = CG
    data["FC"] = FC
    data["GD"] = GD
    data["Ax"] = Ax
    data["Area_min"] = Area_min
    data["Area_max"] = Area_max
    data["Avg_C"] = Avg_C
#    data["Area_min_G"] = Area_min_G
#    data["Area_max_G"] = Area_max_G
#    data["Avg_G"] = Avg_G
    data["Min_Size_G"] = Area_min_G 
    data["Max_Size_G"] = Area_max_G
    data["Average_G"]= Avg_G
    data["imagen_actual"] = imagen_actual
    data["imagen_actual0"] = imagen_actual0
    data["imagen_actual2"] = imagen_actual2
    data["inverted_image"] = inverted_image
    data["Area_guttas"] = Area_guttas
    data["Area_celulas"] = Area_celulas
    data["Area_ratio"] = Area_ratio
    data["Area_ratio_G"] = Area_ratio_G
    GlobalModule.GUI.update_values_GUI(data)

    if pos == 0:
        GlobalModule.GUI.Introduce_CD_entry.config(state="normal")
        GlobalModule.GUI.disable_buttons(
            to_disable=["Select_G", "Select_C", "Draw_Border", "Draw_Pixel"])
        GlobalModule.GUI.disable_buttons(to_disable=[
            "Delete_Border", "Delete_Pixel", "Save", "Save_As", "Guttae_S"
        ])

    else:
        GlobalModule.GUI.enable_buttons(
            to_enable=["Select_G", "Select_C", "Draw_Border", "Draw_Pixel"])
        GlobalModule.GUI.enable_buttons(to_enable=[
            "Delete_Border", "Delete_Pixel", "Save", "Save_As", "Guttae_S"
        ])


def next_image():
    global index_image_actual, image, historial, imagen_actual, imagen_actual2

    if index_image_actual == 1:

        GlobalModule.GUI.disable_buttons(to_disable=[
            "Select_G", "Select_C", "Draw_Border", "Draw_Pixel", "Next_image"
        ])
        GlobalModule.GUI.disable_buttons(to_disable=[
            "Delete_Border", "Delete_Pixel", "Save", "Save_As", "Guttae_S"
        ])
        GlobalModule.GUI.imagen_actual = Image.fromarray(
            guttas.astype(np.uint8) * 255)
        GlobalModule.GUI.imagen_actual = imagen_actual.point(
            lambda p: (p > 0) and 255)
        GlobalModule.GUI.imagen_actual = ImageTk.PhotoImage(
            imagen_actual.resize(size))
        GlobalModule.GUI.image["image"] = imagen_actual

    if index_image_actual == 0:
        if CD != 0:
            GlobalModule.GUI.enable_buttons(to_enable=[
                "Select_G", "Select_C", "Draw_Border", "Draw_Pixel",
                "Previous_image"
            ])
            GlobalModule.GUI.enable_buttons(to_enable=[
                "Delete_Border", "Delete_Pixel", "Save", "Save_As", "Guttae_S"
            ])

        GlobalModule.GUI.imagen_actual = historial["imagen_actual"][
            pos_his_actual]
        GlobalModule.GUI.image["image"] = imagen_actual

    index_image_actual += 1


def previous_image():
    global index_image_actual, image, imagen_actual, imagen_actual2

    if index_image_actual == 1:
        GlobalModule.GUI.disable_buttons(to_disable=[
            "Select_G", "Select_C", "Draw_Border", "Draw_Pixel",
            "Previous_image"
        ])
        GlobalModule.GUI.disable_buttons(to_disable=[
            "Delete_Border", "Delete_Pixel", "Save", "Save_As", "Guttae_S"
        ])
        GlobalModule.GUI.imagen_actual = ImageTk.PhotoImage(
            historial["imagen_actual0"][pos_his_actual].resize(size))
        GlobalModule.GUI.image["image"] = imagen_actual

    if index_image_actual == 2:
        if CD != 0:
            GlobalModule.GUI.enable_buttons(to_enable=[
                "Select_G", "Select_C", "Draw_Border", "Draw_Pixel",
                "Next_image"
            ])
            GlobalModule.GUI.enable_buttons(to_enable=[
                "Delete_Border", "Delete_Pixel", "Save", "Save_As", "Guttae_S"
            ])
        GlobalModule.GUI.imagen_actual = historial["imagen_actual"][
            pos_his_actual]
        GlobalModule.GUI.image["image"] = imagen_actual

    index_image_actual -= 1


def back():
    global pos_his_actual
    goto(historial, pos_his_actual - 1)
    pos_his_actual -= 1
    #recalcularTodo(by_button=True)
    GlobalModule.GUI.update_values_GUI(data)

    GlobalModule.GUI.enable_buttons(to_enable=["Forward"])
    if pos_his_actual == 1:
        GlobalModule.GUI.disable_buttons(to_disable=["Back"])


def forward():
    global pos_his_actual
    #recalcularTodo(by_button=True)
    goto(historial, pos_his_actual + 1)
    pos_his_actual += 1
    if pos_his_actual == len(historial["CD"]) - 1:
        GlobalModule.GUI.disable_buttons(to_disable=["Forward"])

    GlobalModule.GUI.enable_buttons(to_enable=["Back"])
    GlobalModule.GUI.update_values_GUI(data)


def delete_his_from(pos):
    for var in variables:
        historial[var] = historial[var][0:pos]


def reset():
    global Ax, guttas, CG, L, LG, NLG, NC, ju, Area_min, Area_max, Area_min_G, Area_max_G, Avg_C, Avg_G
    global count, NCG, NL, NLG, NG, guttas, LG, CG, FC, GD, CD, timeout, color, texto
    NC = 0
    FC = 0
    CG = 1
    NCG = 0
    NL = 0
    NLG = 0
    NG = 0
    LG = 0
    guttas = 0
    ju = 0
    Ax = 0
    goto(historial, 0)
    delete_his_from(1)
    Area_min = 0
    Area_max = 0
    Avg_C = 0
    Area_min_G = 0
    Area_max_G = 0
    Avg_G = 0
    GD = 0
    CD = 0  #NC/mm2
    #GlobalModule.GUI.buscar(resetear=1)
    calcular_imagen_inicial()

    GlobalModule.GUI.update_values_GUI(data)
    GlobalModule.GUI.nombre_archivo.config(
        text=GlobalModule.GUI.trabajando_sobre)
    GlobalModule.GUI.Introduce_CD_entry.config(state="normal")
    GlobalModule.GUI.disable_buttons(to_disable=[
        "Select_G", "Select_C", "Draw_Border", "Draw_Pixel", "Previous_image",
        "Next_image"
    ])
    GlobalModule.GUI.disable_buttons(to_disable=[
        "Delete_Border", "Delete_Pixel", "Save", "Save_As", "Guttae_S"
    ])
    GlobalModule.ventana.update_idletasks()
    GlobalModule.GUI.Introduce_CD_entry.delete(0, 'end')
    GlobalModule.GUI.timeout, GlobalModule.GUI.color = 500, "black"
    GlobalModule.GUI.texto = "Press <INTRO> to finish"


imgOriginal = 0
imagen_actual0 = 0
imagen_actual2 = 0

Imagen_Segmentacion = 0
size = 0


def calcular_imagen_inicial(resetear=None):
    global Ax, historial, LG, imgOriginal, size
    global im, New_CD_v, CD, count, guttas, inverted_image, Imagen_Segmentacion_Inversa, Ax, imagen_actual, nombre_archivo, image, imagen_CD, imgCD, imageCD, ju, NG, NCG, LG, FC, GD, L, NL, size, crop_d, Avg_C, Avg_G, Area_min, Area_max, Area_min_G, Area_max_G, label_G, pos_his_actual, NLG
    global CG, Ax_Original, Imagen_Segmentacion, data, imgInterseccion

    im = Image.open(GlobalModule.GUI.file_path)

    Ax = im.crop((12, 0, 256, 476))
    Ax_Original = Ax.copy()
    GlobalModule.GUI.Ax_Original = Ax_Original
    
    imagen_actual0 = Ax.copy()
    im.seek(1)

    im.seek(1)
    A, B = im.size
    size = im.size
    imgGris = im.convert('L')
    imgBinaria = imgGris.point(lambda p: (p > 130) and 255)
    imgSegmentacion = imgBinaria.copy()
    imgSegmentacion = imgSegmentacion.crop((12, 0, 256, 476))
    imgInterseccion = imgGris.point(lambda p: (p > 200) and 255)
    Solo_guttas = imgGris.point(lambda p: (p < 130 and p > 100) and 255)
    Solo_guttas = Solo_guttas.crop((12, 0, 256, 476))
    Solo_guttas.save(
        GlobalModule.dir_path + "/" + temp_folder + "solo_guttas.png")
    imgInterseccion = imgInterseccion.crop((12, 0, 256, 476))
    imgSegmentacionBinaria = imgSegmentacion.copy()
    inverted_image = PIL.ImageOps.invert(imgSegmentacionBinaria)
    inverted_image.save(
        GlobalModule.dir_path + "/" + temp_folder + 'SegmentacionInversa.png')
    Imagen_Segmentacion_Inversa = io.imread(
        GlobalModule.dir_path + "/" + temp_folder + "SegmentacionInversa.png",
        as_gray=True)
    count = label(Imagen_Segmentacion_Inversa, 4)
    label_G = label(
        io.imread(
            GlobalModule.dir_path + "/" + temp_folder + "solo_guttas.png",
            as_gray=True), 4)
    CG = count.copy()
    Ax = Ax.convert("L")
    Ax = np.array(Ax)
    for i in range(len(Imagen_Segmentacion_Inversa)):
        for j in range(len(Imagen_Segmentacion_Inversa[0])):
            if ((Imagen_Segmentacion_Inversa[i][j] != 255)):
                Ax[i][j] = 0

    Ax_Original = Ax.copy()
    GlobalModule.GUI.Ax_Inicial = Ax_Original
    
    Area_max = 0
    NC = 0
    Area_max = 0
    region_max = 0
    min_area = 1234567890
    guttas = np.array(
        [[0 for i in range(len(count[0]))] for j in range(len(count))])

    for region in regionprops(count):
        if region.area > Area_max:
            region_max = region.label
            Area_max = region.area
        if region.area < min_area:
            min_area = region.area
        NC = NC + 1

    for region in regionprops(label_G):
        NG = NG + 1

    t = Image.fromarray(Ax)
    Imagen_Segmentacion = t.copy()

    for i in range(len(count)):
        for j in range(len(count[0])):
            if label_G[i][j] != 0:
                #label_image[i][j]=[0,0,0]
                aux = Ax_Original[i][j] - 30
                if aux < 0:
                    aux = 0
                Ax[i][j] = aux
                guttas[i][j] = 255

    NC -= 1
    label2D = np.array(
        [[0 for i in range(len(count[0]))] for j in range(len(count))])

    for i in range(len(count)):
        for j in range(len(count[0])):
            if count[i][j] <= region_max:
                label2D[i][j] = 0
            else:
                label2D[i][j] = count[i][j] - 1

    L = Image.fromarray(np.uint8(label2D), 'L')
    LG = label2D.copy()
    for i in range(len(LG)):
        for j in range(len(LG[0])):
            if guttas[i][j] == 255:
                LG[i][j] = 0

    NLG = len(regionprops(LG))
    ju = Image.fromarray(guttas.astype(np.uint8) * 255)
    ju = ju.point(lambda p: (p > 0) and 255)
    ju.save(GlobalModule.dir_path + "/" + temp_folder + "guttas.png")
    Area_max = 0
    imagen_actual = Image.fromarray(Ax)
    iw, ih = imagen_actual.size
    imgOriginal = imagen_actual
    GlobalModule.GUI.imgOriginal = imgOriginal
    imagen_actual = imagen_actual.resize(size, Image.ANTIALIAS)
    crop_d = size
    pos_his_actual = 0

    Area_celulas= 0
    Area_guttas= 0
    Area_ratio= 0
    Area_ratio_G= 0
    historial[variables[0]].append(count)
    historial[variables[1]].append(NCG)
    historial[variables[2]].append(NL)
    historial[variables[3]].append(NLG)
    historial[variables[4]].append(NG)
    historial[variables[5]].append(NC)
    historial[variables[6]].append(CD)
    historial[variables[7]].append(guttas.copy())
    historial[variables[8]].append(Imagen_Segmentacion.copy())
    historial[variables[9]].append(LG)
    historial[variables[10]].append(CG)
    historial[variables[11]].append(FC)
    historial[variables[12]].append(GD)
    historial[variables[13]].append(Ax)
    historial[variables[14]].append(Area_min)
    historial[variables[15]].append(Area_max)
    historial[variables[16]].append(Avg_C)
    historial[variables[17]].append(Area_min_G)
    historial[variables[18]].append(Area_max_G)
    historial[variables[19]].append(Avg_G)
    historial[variables[20]].append(imagen_actual)
    historial[variables[21]].append(imagen_actual0)
    historial[variables[22]].append(guttas.copy())
    historial[variables[23]].append(inverted_image.copy())
    historial[variables[24]].append(Area_celulas)
    historial[variables[25]].append(Area_guttas)
    historial[variables[26]].append(Area_ratio)
    historial[variables[27]].append(Area_ratio_G)

    GlobalModule.GUI.config_buttons(["Previous", "Next"], state="normal")
    GlobalModule.GUI.Introduce_CD_entry.config(state="normal")
    GlobalModule.GUI.Introduce_CD_entry.delete(0, 'end')

    data["New_CD"] = 0
    data["NC"] = NC
    data["Min_Size"] = 0
    data["Max_Size"] = 0
    data["Average"] = 0
    data["GD"] = 0
    data["NG"] = 0
    data["Min_Size_G"] = 0
    data["Max_Size_G"] = 0
    data["Average_G"] = 0
    data["Nombre_Archivo"] = ""
    data["inverted_image"] = inverted_image
    data["guttas"] = guttas
    data["Ax"] = Ax
    data["LG"] = LG
    data["CG"] = CG
    data["count"] = count
    data["Total_Area"] = 0
    data["Area_ratio"] = Area_ratio
    data["Area_ratio_G"] = Area_ratio_G
    data["Imagen_Segmentacion"] = Imagen_Segmentacion
    redraw()


##Create GUI Window###
GlobalModule.start()


def clic_gutta(event):
    global x, y
    x, y = event.x, event.y
    GlobalModule.did_something = True
    Seleccionar_gutta(x, y)
    if GlobalModule.GUI.zoom_enabled==1:
        calcular_zoom(event)


def sobre_imagen_SG(event):
    GlobalModule.ventana.bind("<Button-1>", clic_con_zoom(event,5))
    #ventana.bind("<Motion>",mostrar_coordenadas_clic)
    #ventana.bind("<MouseWheel>",redraw)
    if GlobalModule.GUI.zoom_enabled==1:
        sobre_imagen_zoom(event)
        

def calcular_zoom(event):
    global x, y
    x, y = event.x, event.y
    
    copia_imagen=GlobalModule.GUI.data["imagen_actual"].copy()
    max_x , max_y=imagen_actual.size
    max_x=max_x-20
    max_y=max_y-20
    copia_imagen=copia_imagen.convert("RGB")

    pix = copia_imagen.load()
    #print ("x:",x,"  y:",y)
    try:
        pix[x, y] = (255,0,0) 
        #pix[x+1, y] = (255,0,0) 
        #pix[x, y+1] = (255,0,0) 
        #pix[x+1, y+1] = (255,0,0) 
        x0=max(x-50,0)
        if x0==0:
            x1=100
        else:
            x1=min(max_x,x+50)
            if x1==max_x:
                x0=max_x-100
        y0=max(y-50,0)
        
        if y0==0:
            y1=100
        else:
            y1=min(max_y,y+50)
            if y1==max_y:
                y0=max_y-100
        
        coors_to_crop=[x0,y0,x1,y1]
        
        imagen_de_zoom=copia_imagen.crop(coors_to_crop)
        imagen_de_zoom = imagen_de_zoom.resize([500,500], Image.ANTIALIAS)
        GlobalModule.GUI.update_zoom_image(imagen_de_zoom)
    except IndexError:
        pass

def sobre_imagen_SC(event):
    GlobalModule.ventana.bind("<Button-1>", clic_con_zoom(event,6))
    #GlobalModule.ventana.bind("<MouseWheel>",redraw)
    if GlobalModule.GUI.zoom_enabled==1:
        sobre_imagen_zoom(event)
        

def com(num):
    if GlobalModule.did_something:
        recalcularTodo()
    if num == 1:
        reset

    elif num == 8:

        GlobalModule.ventana.bind("<Return>", unbind)
        GlobalModule.GUI.image.bind("<Leave>", no_sobre_imagen)
        GlobalModule.GUI.enable_blink = 1
        GlobalModule.GUI.disable_buttons(but=["Next"])
        GlobalModule.GUI.Introduce_CD_entry.config(state="disabled")
        GlobalModule.GUI.image.bind("<Enter>", sobre_imagen_SG)
        GlobalModule.GUI.image.config(cursor="tcross")

    elif num == 9:
        GlobalModule.GUI.enable_blink = 1
        GlobalModule.GUI.disable_buttons(but=["Next"])
        GlobalModule.GUI.Introduce_CD_entry.config(state="disabled")
        GlobalModule.GUI.image.bind("<Enter>", sobre_imagen_SC)
        GlobalModule.GUI.image.bind("<Leave>", no_sobre_imagen)
        GlobalModule.GUI.image.config(cursor="tcross")
        GlobalModule.ventana.bind("<Return>", unbind)

    elif num == 10:
        guttae_S()
        
    elif num == 11:
        if GlobalModule.GUI.zoom_enabled==1:
            GlobalModule.GUI.zoom_enabled=0
            GlobalModule.GUI.zoom_image.destroy()
        else:
            GlobalModule.GUI.zoom_enabled=1
            GlobalModule.GUI.ventana_zoom()
            GlobalModule.GUI.image.bind("<Enter>", sobre_imagen_zoom)
            GlobalModule.GUI.image.bind("<Leave>", no_sobre_imagen)




def funcion_inicial():

    GlobalModule.GUI.buscar()
    if not GlobalModule.GUI.file_path:
        return
    calcular_imagen_inicial()
    data["Nombre_Archivo"] = GlobalModule.GUI.trabajando_sobre
    GlobalModule.GUI.Introduce_CD_entry.bind("<Return>", actualizarCD)
    GlobalModule.GUI.update_values_GUI(data)
    GlobalModule.GUI.config_buttons(buttons=["Reset"], command=reset)
    GlobalModule.GUI.config_buttons(buttons=["Forward"], command=forward)
    GlobalModule.GUI.config_buttons(buttons=["Back"], command=back)
    GlobalModule.GUI.config_buttons(buttons=["Next"], command=next_image)
    GlobalModule.GUI.config_buttons(
        buttons=["Previous"], command=previous_image)

    GlobalModule.GUI.config_buttons(buttons=["Save"], command=save)
    GlobalModule.GUI.config_buttons(buttons=["Save_As"], command=save_as)

    GlobalModule.GUI.config_buttons(
        buttons=["Select_G"], command=lambda: com(8))
    GlobalModule.GUI.config_buttons(
        buttons=["Select_C"], command=lambda: com(9))
    GlobalModule.GUI.config_buttons(
        buttons=["Zoom"], command=lambda: com(11))
    #GlobalModule.GUI.config_buttons(
        #buttons=["Guttae_S"], command=lambda: com(10))

    GlobalModule.GUI.config_buttons(buttons=["Draw_Border"], command=draw_B)
    GlobalModule.GUI.config_buttons(
        buttons=["Delete_Border"], command=delete_B)
    #GlobalModule.GUI.config_buttons(buttons=["Draw_Pixel"], command=draw_P)
    #GlobalModule.GUI.config_buttons(buttons=["Delete_Pixel"], command=delete_P)


GlobalModule.GUI.config_buttons(
    buttons=["Select_F"], state="normal", command=funcion_inicial)
GlobalModule.GUI.after_id = GlobalModule.GUI.master.after(
    0, GlobalModule.GUI.update_GUI_messages)
GlobalModule.GUI.raise_above_all()
GlobalModule.ventana.mainloop()
