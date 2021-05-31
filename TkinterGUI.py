# -*- coding: utf-8 -*-

import ctypes  
from tkinter import Tk, Toplevel, Canvas, Label, Button, Entry, filedialog, \
    messagebox, BOTH
import tkinter.font as tkFont
from PIL import Image, ImageTk
import os
import platform
import subprocess  #For Linux#
import csv

cwd = os.getcwd()
dir_path = os.path.dirname(os.path.realpath(__file__))
#micro = 'um2'
micro = 'μm2'

class SecCorrectorGUI:

    '''Clase para el GUI'''

    def __init__(self, master):
        self.master = master
        self.normal_update = False
        self.trabajando_sobre = ''
        self.guardo = False
        self.imgOriginal = None
        self.Ax_Original = None
        self.Ax_Inicial= None
        self.file_path = None
        self.zoom_enabled=0

        self.trabajando_sobre=""
        self.file_path=""

        try:
            master.title('Segmentation Corrector '
                         + master.soft_version)
        except AttributeError:
            master.title('Segmentation Corrector NO VERSION SPECIFIED')

        self.OS = platform.platform()
        if 'Windows' not in self.OS:
            if 'Linux' not in self.OS:
                self.OS = 'Mac'
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        (self.timeout, self.color) = (500, 'black')
        self.texto = 'Press <INTRO> to finish'
        (self.ancho, self.alto) = (0, 0)
        self.anchoCanvas = 1011
        self.altura = 690
        self.anchoR_Imagen = [958, 644]

        if 'Windows' in self.OS:
            print ('Running on Windows...')
            user32 = ctypes.windll.user32
            user32.SetProcessDPIAware()
            (self.ancho, self.alto) = (user32.GetSystemMetrics(0),
                    user32.GetSystemMetrics(1))
            self.font_default = 'Arial 12 bold italic'
            self.font_default_small = 'Arial 10'
            self.cursor_wait = 'wait'
        elif 'Linux' in self.OS:

            print ('Running on Linux...')
            self.font_default = tkFont.Font(family='courier 10 pitch',
                    size=16, weight=tkFont.BOLD, slant=tkFont.ITALIC)
            self.font_default_small = 'Helvetica 10'
            self.cursor_wait = 'watch'
            output = \
                subprocess.Popen('xrandr | grep "\*" | cut -d" " -f4',
                                 shell=True,
                                 stdout=subprocess.PIPE).communicate()[0].decode('utf-8'
                    )
            resolution = output.split()[0].split('x')
            (self.ancho, self.alto) = (int(resolution[0]),
                    int(resolution[1]))
        else:

            print ('Running on MacOS is NOT supported...')
            self.font_default = tkFont.Font(family='courier 10 pitch',
                    size=16, weight=tkFont.BOLD, slant=tkFont.ITALIC)
            self.font_default_small = 'Helvetica 14'
            self.cursor_wait = 'watch'
            (self.ancho, self.alto) = (self.master.winfo_screenwidth(),
                    self.master.winfo_screenheight())

        self.escala = 1
        (self.x, self.y) = (0, 0)
        self.escala_P = 1.25  # For screens with low resolution (<1920x1080)
        self.crop_d = [244 * self.escala_P, 476 * self.escala_P]  # Default crop size
        self.centro = [self.crop_d[0] / 2, self.crop_d[1] / 2]  # Default center coordinates
        self.centro_O = [self.crop_d[0] / 2, self.crop_d[1] / 2]  # Absolute center coordinates for image

        if self.alto >= 1080:
            self.escala_P = 1.5
            self.crop_d = [244 * self.escala_P, 476 * self.escala_P]  # Default crop size
            self.anchoCanvas = 1060
            self.anchoR_Imagen = [1020, 763]
            self.altura = 800

        self.Recorte = [0, 0, self.crop_d[0], self.crop_d[1]]
        self.size_O = (244, 477)
        self.imagen_actual = 0
        windowGeometry = str(self.anchoCanvas - 6).encode('utf-8',
                'ignore').decode('utf-8') + 'x' \
            + str(self.altura).encode('utf-8', 'ignore').decode('utf-8'
                ) + '+' + str(int(self.ancho / 2 - self.anchoCanvas/2)).encode('utf-8'
                , 'ignore').decode('utf-8') + '+' + str(int(self.alto / 2 - self.altura/2)).encode('utf-8'
                , 'ignore').decode('utf-8')

        master.geometry(windowGeometry)
        master.config(bg='#F0F0F0')

        alt = int(self.alto - 78)

        self.canvas = Canvas(self.master, width=self.anchoCanvas,
                             height=alt, bg='#F0F0F0')
        self.canvas.pack()
        self.canvas.create_rectangle(40, 30, 630, 120+40, outline='#476042'
                )

        if 'Windows' in self.OS:
            self.canvas.create_rectangle(550, 40, 620, 110,
                    outline='#476042')
        elif 'Linux' in self.OS:

            self.canvas.create_rectangle(550 - 2, 40, 620 - 2, 110,
                    outline='#476042')
        else:

            self.canvas.create_rectangle(550 - 2, 40, 620 - 2, 110,
                    outline='#476042')

        self.canvas.create_rectangle(40, 142+40, 330, 350+60+40,
                outline='#476042')
        self.canvas.create_rectangle(340, 142+40, 630, 350+60+40,
                outline='#476042')
        self.canvas.create_rectangle(40, 372+60+40, 630, 540+40+30,
                outline='#476042')
        self.canvas.create_rectangle(640, 30, self.anchoR_Imagen[0],
                self.anchoR_Imagen[1], outline='#476042')
        self.mensajes = Label(
            self.master,
            bg='#F0F0F0',
            fg='#F0F0F0',
            font=self.font_default,
            width=40,
            height=1,
            justify='center',
            text='Press <INTRO> to finish',
            )
        self.mensajes.pack()
        self.mensajes.place(x=130, y=600+40)
        self.widget_actual = 0
        self.enable_blink = 0
        (self.timeout, self.color) = (500, 'black')
        self.yapaso = 0
        self.count = 0

        # #READ MESSSAGES TO DISPLAY WHEN CLICKING HELP BUTTONS##

        self.mensajes_botones = {}
        csv.register_dialect('myDialect', delimiter=';',
                             skipinitialspace=True)
        with open(dir_path + '/files/help_butttons.csv', 'r') as \
            csvFile:
            reader = csv.reader(csvFile, dialect='myDialect')
            for texto in reader:
                self.mensajes_botones[texto[0]] = texto[1]
        csvFile.close()

        # ###LABELS###

        if 'Windows' in self.OS:
            labels_width = [
                20,
                16,
                7,
                10,
                5,
                3,
                10,
                10,
                ]
        elif 'Linux' in self.OS:
            labels_width = [
                25,
                21,
                11,
                15,
                10,
                8,
                15,
                15,
                ]
        else:
            labels_width = [
                20,
                16,
                7,
                10,
                5,
                3,
                10,
                10,
                ]

        segmentation_correction_l = Label(
            self.master,
            bg='#F0F0F0',
            fg='black',
            font=self.font_default,
            width=labels_width[0],
            height=1,
            justify='center',
            text='Segmentation Correction',
            )
        segmentation_correction_l.pack()
        segmentation_correction_l.place(x=50, y=15)
        image_segmentation_l = Label(
            self.master,
            bg='#F0F0F0',
            fg='black',
            font=self.font_default,
            width=labels_width[1],
            height=1,
            justify='center',
            text='Image Segmentation',
            )
        image_segmentation_l.pack()
        image_segmentation_l.place(x=650, y=15)
        cell_info_l = Label(
            self.master,
            bg='#F0F0F0',
            fg='black',
            font=self.font_default,
            width=labels_width[2],
            height=1,
            justify='center',
            text='Cells info',
            )
        cell_info_l.pack()
        cell_info_l.place(x=50, y=170)
        guttaes_info_l = Label(
            self.master,
            bg='#F0F0F0',
            fg='black',
            font=self.font_default,
            width=labels_width[3],
            height=1,
            justify='center',
            text='Guttae info',
            )
        guttaes_info_l.pack()
        guttaes_info_l.place(x=350, y=170)
        tools_l = Label(
            self.master,
            bg='#F0F0F0',
            fg='black',
            font=self.font_default,
            width=labels_width[4],
            height=1,
            justify='center',
            text='Tools',
            )
        tools_l.pack()
        tools_l.place(x=50, y=360+60+40)
        files_l = Label(
            self.master,
            bg='#F0F0F0',
            fg='black',
            font=self.font_default_small,
            width=labels_width[5],
            height=1,
            justify='center',
            text='File',
            )
        files_l.pack()
        files_l.place(x=50 + 23 - 5, y=385+60+40)
        segmentation_l = Label(
            self.master,
            bg='#F0F0F0',
            fg='black',
            font=self.font_default_small,
            width=labels_width[6],
            height=1,
            justify='center',
            text='Segmentation',
            )
        segmentation_l.pack()
        segmentation_l.place(x=400 + 69 - 25 + 2, y=385+60+40)
        guttae_cell_l = Label(
            self.master,
            bg='#F0F0F0',
            fg='black',
            font=self.font_default_small,
            width=labels_width[6],
            height=1,
            justify='center',
            text='Guttaes/Cells',
            )
        guttae_cell_l.pack()
        guttae_cell_l.place(x=225 + 46 - 15 + 1, y=385+60+40)

        # ##Rectangulos Botones###

        self.canvas.create_rectangle(63, 395+60+40, 210 + 23 - 5 + 1, 530+40+30,
                outline='#476042')
        self.canvas.create_rectangle(220 + 46 - 15 + 1, 395+60+40, 385 + 46
                - 15 + 2, 530+40, outline='#476042')
        self.canvas.create_rectangle(395 + 69 - 25 + 2, 395+60+40, 560 + 69
                - 25 + 3, 530+40, outline='#476042')

        # ##Get icons###

        self.icons = {}
        self.icons_name = [
            'undo',
            'redo',
            'question',
            'reset',
            'next',
            'previous',
            ]
        for name in self.icons_name:
            icon = Image.open(dir_path + '/files/icons/' + name + '.png'
                              )
            icon = icon.resize((15, 15), Image.ANTIALIAS)
            icon = ImageTk.PhotoImage(icon)
            self.icons[name] = icon

        # ##Main Buttons###

        if 'Windows' in self.OS:
            buttons_width = [
                15,
                53,
                20,
                20,
                20,
                20,
                ]
        elif 'Linux' in self.OS:
            buttons_width = [
                10,
                58,
                20,
                20,
                20,
                20,
                ]
        else:
            buttons_width = [
                10,
                53,
                20,
                20,
                20,
                20,
                ]

        self.buttons = {}
        Select_F_button = Button(
            self.master,
            fg='black',
            bg='#E0E0E0',
            width=buttons_width[0],
            height=1,
            text='Select File:',
            command=lambda : None,
            )
        Select_F_button.pack()
        Select_F_button.place(x=50, y=40)
        self.buttons['Select_F'] = Select_F_button

        Reset_button = Button(
            self.master,
            fg='black',
            bg='#E0E0E0',
            width=buttons_width[1],
            height=20,
            image=self.icons['reset'],
            text='Reset ',
            compound='right',
            padx=1,
            command=lambda : None,
            )
        Reset_button.pack()
        Reset_button.place(x=555, y=45)
        self.buttons['Reset'] = Reset_button

        forward_button = Button(
            self.master,
            fg='black',
            bg='#E0E0E0',
            width=buttons_width[2],
            height=20,
            text='->',
            image=self.icons['redo'],
            command=lambda : None,
            )
        forward_button.pack()
        forward_button.place(x=590, y=80)
        self.buttons['Forward'] = forward_button

        back_button = Button(
            self.master,
            fg='black',
            bg='#E0E0E0',
            width=buttons_width[3],
            height=20,
            text='<-',
            image=self.icons['undo'],
            command=lambda : None,
            )
        back_button.pack()
        back_button.place(x=555, y=80)
        self.buttons['Back'] = back_button

        # next_button=Button(self.master,fg="black",bg="#E0E0E0",width=buttons_width[4],height=20,text="->",image=self.icons["next"],command=lambda : None)
        # next_button.pack()
        # previous_button=Button(self.master,fg="black",bg="#E0E0E0",width=buttons_width[5],height=20,text="<-",image=self.icons["previous"],command=lambda : None)
        # previous_button.pack()

#        if self.alto>=1080:
#          #next_button.place(x=830,y=767)
#          #previous_button.place(x=795,y=767)
#        else:
#          #next_button.place(x=805,y=650)
#          #previous_button.place(x=770,y=650)

        # self.buttons["Next"]=next_button
        # self.buttons["Previous"]=previous_button

        # ##MODIFICATION BUTTONS###

        if 'Windows' in self.OS:
            m_buttons_width = [
                15,
                15,
                15,
                15,
                15,
                15,
                15,
                15,
                15,
                15,
                ]
        elif 'Linux' in self.OS:
            m_buttons_width = [
                10,
                10,
                10,
                10,
                10,
                10,
                10,
                10,
                10,
                10,
                ]
        else:
            m_buttons_width = [
                10,
                10,
                10,
                10,
                10,
                10,
                10,
                10,
                10,
                10,
                ]

        # ##Botones 1###

        Save_button = Button(
            self.master,
            fg='black',
            bg='#E0E0E0',
            width=m_buttons_width[0],
            height=1,
            text='Save',
            command=lambda : None,
            )
        Save_button.pack()
        Save_button.place(x=104, y=410+60+40)
        self.buttons['Save'] = Save_button

        Save_as_button = Button(
            self.master,
            fg='black',
            bg='#E0E0E0',
            width=m_buttons_width[1],
            height=1,
            text='Save As...',
            command=lambda : None,
            )
        Save_as_button.pack()
        Save_as_button.place(x=85 + 23 - 5 + 1, y=440+60+40)
        self.buttons['Save_As'] = Save_as_button

        Zoom_button=Button(self.master,fg="black",bg="#E0E0E0",width=m_buttons_width[2],height=1,text="Zoom",command= lambda :self.ventana_zoom())
        Zoom_button.pack()
        Zoom_button.place(x=85+23-5+1,y=470+60+40)
        self.buttons["Zoom"]=Zoom_button

        # ##Botones 2###

        Select_G_button = Button(
            self.master,
            fg='black',
            bg='#E0E0E0',
            width=m_buttons_width[3],
            height=1,
            text='Select Guttae',
            command=lambda : None,
            )
        Select_G_button.pack()
        Select_G_button.place(x=260 + 46 - 15 + 2, y=410+60+40)
        self.buttons['Select_G'] = Select_G_button

        Select_C_button = Button(
            self.master,
            fg='black',
            bg='#E0E0E0',
            width=m_buttons_width[4],
            height=1,
            text='Select Cell',
            command=lambda : None,
            )
        Select_C_button.pack()
        Select_C_button.place(x=260 + 46 - 15 + 2, y=440+60+40)
        self.buttons['Select_C'] = Select_C_button

        # Guttae_S_button=Button(self.master,fg="black",bg="#E0E0E0",width=m_buttons_width[5],height=1,text="Guttae Seed",command=lambda : None)
        # Guttae_S_button.pack()
        # Guttae_S_button.place(x=260+46-15+2,y=470)
        # self.buttons["Guttae_S"]=Guttae_S_button

        # ##Botones 3###

        Draw_border_button = Button(
            self.master,
            fg='black',
            bg='#E0E0E0',
            width=m_buttons_width[6],
            height=1,
            text='Draw Border',
            command=lambda : None,
            )
        Draw_border_button.pack()
        Draw_border_button.place(x=435 + 69 - 25 + 3, y=410+60+40)
        self.buttons['Draw_Border'] = Draw_border_button

#        Draw_pixel_button = Button(
#            self.master,
#            fg='black',
#            bg='#E0E0E0',
#            width=m_buttons_width[7],
#            height=1,
#            text='Draw Pixel',
#            command=lambda : None,
#            )
#        Draw_pixel_button.pack()
#        Draw_pixel_button.place(x=435 + 69 - 25 + 3, y=440)
#        self.buttons['Draw_Pixel'] = Draw_pixel_button

        Delete_border_button = Button(
            self.master,
            fg='black',
            bg='#E0E0E0',
            width=m_buttons_width[8],
            height=1,
            text='Delete Border',
            command=lambda : None,
            )
        Delete_border_button.pack()
        Delete_border_button.place(x=435 + 69 - 25 + 3, y=470-30+60+40)
        self.buttons['Delete_Border'] = Delete_border_button

#        Delete_pixel_button = Button(
#            self.master,
#            fg='black',
#            bg='#E0E0E0',
#            width=m_buttons_width[9],
#            height=1,
#            text='Delete Pixel',
#            command=lambda : None,
#            )
#        Delete_pixel_button.pack()
#        Delete_pixel_button.place(x=435 + 69 - 25 + 3, y=500)
#        self.buttons['Delete_Pixel'] = Delete_pixel_button

        # ##Question buttons###

        Q_ico = self.icons['question']
        Question_button = Button(
            self.master,
            fg='black',
            bg='#E0E0E0',
            width=20,
            height=20,
            image=Q_ico,
            command=lambda : self.show_help('save'),
            )
        Question_button.image = Q_ico
        Question_button2 = Button(
            self.master,
            fg='black',
            bg='#E0E0E0',
            width=20,
            height=20,
            image=Q_ico,
            command=lambda : self.show_help('save_as'),
            )

        Question_button3=Button(self.master,fg="black",bg="#E0E0E0",width=20,height=20,image=Q_ico,command=lambda :self.show_help("zoom"))

        Question_button4 = Button(
            self.master,
            fg='black',
            bg='#E0E0E0',
            width=20,
            image=Q_ico,
            height=20,
            command=lambda : self.show_help('select_guttae'),
            )
        Question_button5 = Button(
            self.master,
            fg='black',
            bg='#E0E0E0',
            width=20,
            height=20,
            image=Q_ico,
            command=lambda : self.show_help('select_cell'),
            )

        # Question_button6=Button(self.master,fg="black",bg="#E0E0E0",width=20,height=20,image=Q_ico,command=lambda :self.show_help("guttae_seed"))

        Question_button7 = Button(
            self.master,
            fg='black',
            bg='#E0E0E0',
            width=20,
            image=Q_ico,
            height=20,
            command=lambda : self.show_help('draw_border'),
            )
        Question_button8 = Button(
            self.master,
            fg='black',
            bg='#E0E0E0',
            width=20,
            height=20,
            image=Q_ico,
            command=lambda : self.show_help('delete_border'),
            )
#        Question_button9 = Button(
#            self.master,
#            fg='black',
#            bg='#E0E0E0',
#            width=20,
#            height=20,
#            image=Q_ico,
#            command=lambda : self.show_help('draw_pixel'),
#            )
#        Question_button10 = Button(
#            self.master,
#            fg='black',
#            bg='#E0E0E0',
#            width=20,
#            height=20,
#            image=Q_ico,
#            command=lambda : self.show_help('delete_pixel'),
#            )
        Question_button.pack()
        Question_button2.pack()

        Question_button3.pack()

        Question_button4.pack()
        Question_button5.pack()

        # Question_button6.pack()

        Question_button7.pack()
        Question_button8.pack()
        #Question_button9.pack()
        #Question_button10.pack()
        Question_button.place(x=55 + 23 - 5, y=410+60+40)
        Question_button2.place(x=55 + 23 - 5, y=440+60+40)

        Question_button3.place(x=55+23-5,y=470+100)

        Question_button4.place(x=230 + 46 - 15 + 1, y=410+60+40)
        Question_button5.place(x=230 + 46 - 15 + 1, y=440+60+40)

        # Question_button6.place(x=230+46-15+1,y=470)

        Question_button7.place(x=405 + 69 - 25 + 2, y=410+60+40)
        Question_button8.place(x=405 + 69 - 25 + 2, y=440+60+40)
       # Question_button9.place(x=405 + 69 - 25 + 2, y=470)
        #Question_button10.place(x=405 + 69 - 25 + 2, y=500)

        master.resizable(0, 0)
        self.nombre_archivo = Label(
            self.master,
            bg='white',
            font=self.font_default_small,
            width=44,
            wraplength=500,
            height=1,
            borderwidth=1,
            relief='solid',
            justify='center',
            text='',
            )
        self.nombre_archivo.pack()
        self.nombre_archivo.place(x=180, y=42)

        self.image = Label(self.master, bg='#F0F0F0')
        self.image.pack()
        self.image.place(x=645, y=40)
        self.imageCD = Label(self.master, bg='#F0F0F0')
        self.imageCD.pack(fill=BOTH, expand=1)
        self.imageCD.place(x=385, y=80)

        # ##LABELS FOR INFO###

        Introduce_CD_l = Label(  # ,wraplength=500
            self.master,
            bg='#F0F0F0',
            fg='black',
            font=self.font_default_small,
            width=14,
            height=1,
            anchor='w',
            justify='left',
            text='Introduce CD:',
            )
        Introduce_CD_l.pack()
        New_CD_l = Label(  # ,wraplength=500
            self.master,
            bg='#F0F0F0',
            fg='black',
            font=self.font_default_small,
            width=12,
            height=1,
            anchor='w',
            justify='left',
            text='New CD:',
            )
        New_CD_l.pack()
        NC_l = Label(  # ,wraplength=500
            self.master,
            bg='#F0F0F0',
            fg='black',
            font=self.font_default_small,
            width=12,
            height=1,
            anchor='w',
            justify='left',
            text='NC:',
            )
        NC_l.pack()
        Min_size_l = Label(  # ,wraplength=500
            self.master,
            bg='#F0F0F0',
            fg='black',
            font=self.font_default_small,
            width=12,
            height=1,
            anchor='w',
            justify='left',
            text='Min Size:',
            )
        Min_size_l.pack()
        Max_size_l = Label(  # ,wraplength=500
            self.master,
            bg='#F0F0F0',
            fg='black',
            font=self.font_default_small,
            width=12,
            height=1,
            anchor='w',
            justify='left',
            text='Max Size:',
            )
        Max_size_l.pack()
        Average_l = Label(  # ,wraplength=500
            self.master,
            bg='#F0F0F0',
            fg='black',
            font=self.font_default_small,
            width=12,
            height=1,
            anchor='w',
            justify='left',
            text='Average size:',
            )
        Average_l.pack()
        GD_l = Label(  # ,wraplength=500
            self.master,
            bg='#F0F0F0',
            fg='black',
            font=self.font_default_small,
            width=12,
            height=1,
            anchor='w',
            justify='left',
            text='GD:',
            )
        GD_l.pack()
        NG_l = Label(  # ,wraplength=500
            self.master,
            bg='#F0F0F0',
            fg='black',
            font=self.font_default_small,
            width=12,
            height=1,
            anchor='w',
            justify='left',
            text='NG:',
            )
        NG_l.pack()
        Min_size_G = Label(  # ,wraplength=500
            self.master,
            bg='#F0F0F0',
            fg='black',
            font=self.font_default_small,
            width=12,
            height=1,
            anchor='w',
            justify='left',
            text='Min size:',
            )
        Min_size_G.pack()
        Max_size_G = Label(  # ,wraplength=500
            self.master,
            bg='#F0F0F0',
            fg='black',
            font=self.font_default_small,
            width=12,
            height=1,
            anchor='w',
            justify='left',
            text='Max size:',
            )
        Max_size_G.pack()
        Average_G = Label(  # ,wraplength=500
            self.master,
            bg='#F0F0F0',
            fg='black',
            font=self.font_default_small,
            width=12,
            height=1,
            anchor='w',
            justify='left',
            text='Average size:',
            )
        Average_G.pack()
        
        Area_ratio = Label(  # ,wraplength=500
            self.master,
            bg='#F0F0F0',
            fg='black',
            font=self.font_default_small,
            width=12,
            height=1,
            anchor='w',
            justify='left',
            text='Area ratio:',
            )
        Area_ratio.pack()
        
        Area_ratio_G = Label(  # ,wraplength=500
            self.master,
            bg='#F0F0F0',
            fg='black',
            font=self.font_default_small,
            width=12,
            height=1,
            anchor='w',
            justify='left',
            text='Area ratio:',
            )
        Area_ratio_G.pack()
        
        Introduce_CD_l.place(x=50, y=80)
        New_CD_l.place(x=50, y=160+40)
        NC_l.place(x=50, y=200+40)
        Min_size_l.place(x=50, y=240+40)
        Max_size_l.place(x=50, y=280+40)
        Average_l.place(x=50, y=320+40)
        GD_l.place(x=370, y=160+40)
        NG_l.place(x=370, y=200+40)
        Min_size_G.place(x=370, y=240+40)
        Max_size_G.place(x=370, y=280+40)
        Average_G.place(x=370, y=320+40)
        Area_ratio.place(x=50, y=360+40)
        Area_ratio_G.place(x=370, y=360+40)
        

        self.data = {}

        # #Labels for values##

        self.value_labels = {}
        New_CD_v = Label(  # ,wraplength=500
            self.master,
            bg='white',
            font=self.font_default_small,
            width=10,
            wraplength=500,
            height=1,
            justify='center',
            text='0',
            )
        New_CD_v.pack()
        NC_v = Label(  # ,wraplength=500
            self.master,
            bg='white',
            font=self.font_default_small,
            width=10,
            wraplength=500,
            height=1,
            justify='center',
            text='0',
            )
        NC_v.pack()
        Min_size_v = Label(  # ,wraplength=500
            self.master,
            bg='white',
            font=self.font_default_small,
            width=10,
            wraplength=500,
            height=1,
            justify='center',
            text='0',
            )
        Min_size_v.pack()
        Max_size_v = Label(  # ,wraplength=500
            self.master,
            bg='white',
            font=self.font_default_small,
            width=10,
            wraplength=500,
            height=1,
            justify='center',
            text='0',
            )
        Max_size_v.pack()
        Average_v = Label(  # ,wraplength=500
            self.master,
            bg='white',
            font=self.font_default_small,
            width=10,
            wraplength=500,
            height=1,
            justify='center',
            text='0',
            )
        Average_v.pack()
        GD_v = Label(  # ,wraplength=500
            self.master,
            bg='white',
            font=self.font_default_small,
            width=10,
            wraplength=500,
            height=1,
            justify='center',
            text='0',
            )
        GD_v.pack()
        NG_v = Label(  # ,wraplength=500
            self.master,
            bg='white',
            font=self.font_default_small,
            width=10,
            wraplength=500,
            height=1,
            justify='center',
            text='0',
            )
        NG_v.pack()
        Min_size_G_v = Label(  # ,wraplength=500
            self.master,
            bg='white',
            font=self.font_default_small,
            width=10,
            wraplength=500,
            height=1,
            justify='center',
            text='0',
            )
        Min_size_G_v.pack()
        Max_size_G_v = Label(  # ,wraplength=500
            self.master,
            bg='white',
            font=self.font_default_small,
            width=10,
            wraplength=500,
            height=1,
            justify='center',
            text='0',
            )
        Max_size_G_v.pack()
        Average_G_v = Label(  # ,wraplength=500
            self.master,
            bg='white',
            font=self.font_default_small,
            width=10,
            wraplength=500,
            height=1,
            justify='center',
            text='0',
            )
        Average_G_v.pack()
        
        Area_ratio_v = Label(  # ,wraplength=500
            self.master,
            bg='white',
            font=self.font_default_small,
            width=10,
            wraplength=500,
            height=1,
            justify='center',
            text='0',
            )
        Area_ratio_v.pack()
        
        Area_ratio_G_v = Label(  # ,wraplength=500
            self.master,
            bg='white',
            font=self.font_default_small,
            width=10,
            wraplength=500,
            height=1,
            justify='center',
            text='0',
            )
        Area_ratio_G_v.pack()


        New_CD_v.place(x=135, y=160+40)
        NC_v.place(x=135, y=200+40)
        Min_size_v.place(x=135, y=240+40)
        Max_size_v.place(x=135, y=280+40)
        Average_v.place(x=135, y=320+40)
        GD_v.place(x=455, y=160+40)
        NG_v.place(x=455, y=200+40)
        Min_size_G_v.place(x=455, y=240+40)
        Max_size_G_v.place(x=455, y=280+40)
        Average_G_v.place(x=455, y=320+40)
        Area_ratio_v.place(x=135, y=360+40)
        Area_ratio_G_v.place(x=455, y=360+40)
        
        
        Total_Area_l = Label(  # ,wraplength=500
            self.master,
            bg='#F0F0F0',
            fg='black',
            font=self.font_default_small,
            width=12,
            height=1,
            anchor='w',
            justify='left',
            text='Analyzed Area:',
            )
        Total_Area_l.pack()
        
        Total_Area_v = Label(  # ,wraplength=500
            self.master,
            bg='white',
            font=self.font_default_small,
            width=10,
            wraplength=500,
            height=1,
            justify='center',
            text='0',
            )
        
        Total_Area_U= Label(  # ,wraplength=700
                self.master,
                bg='#F0F0F0',
                font=self.font_default_small,
                fg='black',
                width=7,
                height=1,
                anchor='w',
                justify='left',
                text=micro,
                )
        Total_Area_U.pack()
        Total_Area_v.pack()
        Total_Area_v.place(x=180, y=120)
        Total_Area_l.place(x=50, y=120)
        Total_Area_U.place(x=300, y=120)
        
        self.value_labels['Total_Area'] = Total_Area_v
        self.value_labels['New_CD'] = New_CD_v
        self.value_labels['NC'] = NC_v
        self.value_labels['Min_Size'] = Min_size_v
        self.value_labels['Max_Size'] = Max_size_v
        self.value_labels['Average'] = Average_v
        self.value_labels['GD'] = GD_v
        self.value_labels['NG'] = NG_v
        self.value_labels['Min_Size_G'] = Min_size_G_v
        self.value_labels['Max_Size_G'] = Max_size_G_v
        self.value_labels['Average_G'] = Average_G_v
        self.value_labels['Area_ratio'] = Area_ratio_v
        self.value_labels['Area_ratio_G'] = Area_ratio_G_v

        self.data['New_CD'] = 0
        self.data['NC'] = 0
        self.data['Min_Size'] = 0
        self.data['Max_Size'] = 0
        self.data['Average'] = 0
        self.data['GD'] = 0
        self.data['NG'] = 0
        self.data['Min_Size_G'] = 0
        self.data['Max_Size_G'] = 0
        self.data['Average_G'] = 0
        self.data['guttas'] = 0
        self.data['Ax'] = 0
        self.data['count'] = 0
        self.data["Total_Area"] = 0
        self.data["Guttae_area"]= 0
        self.data["cell_area"]= 0

        if 'Mac' in self.OS:
            Introduce_CD_u = Label(
                self.master,
                bg='#F0F0F0',
                fg='black',
                width=7,
                height=1,
                anchor='w',
                justify='left',
                text='cell/mm2',
                )
            Introduce_CD_u.pack()
            New_CD_U = Label(  # ,wraplength=700
                self.master,
                bg='#F0F0F0',
                font=self.font_default_small,
                fg='black',
                width=7,
                height=1,
                anchor='w',
                justify='right',
                text='cell/mm2',
                )
            New_CD_U.pack()
            NC_U = Label(  # ,wraplength=700
                self.master,
                bg='#F0F0F0',
                font=self.font_default_small,
                fg='black',
                width=7,
                height=1,
                anchor='w',
                justify='left',
                text='cells',
                )
            NC_U.pack()
            Min_size_U = Label(  # ,wraplength=700
                self.master,
                bg='#F0F0F0',
                font=self.font_default_small,
                fg='black',
                width=7,
                height=1,
                anchor='w',
                justify='left',
                text=micro,
                )
            Min_size_U.pack()
            Max_size_U = Label(  # ,wraplength=700
                self.master,
                bg='#F0F0F0',
                font=self.font_default_small,
                fg='black',
                width=7,
                height=1,
                anchor='w',
                justify='left',
                text=micro,
                )
            Max_size_U.pack()
            Average_U = Label(  # ,wraplength=700
                self.master,
                bg='#F0F0F0',
                font=self.font_default_small,
                fg='black',
                width=7,
                height=1,
                anchor='w',
                justify='left',
                text=micro,
                )
            Average_U.pack()
            GD_U = Label(  # ,wraplength=700
                self.master,
                bg='#F0F0F0',
                font=self.font_default_small,
                fg='black',
                width=9,
                height=1,
                anchor='w',
                justify='left',
                text='guttae/mm2',
                )
            GD_U.pack()
            NG_U = Label(  # ,wraplength=700
                self.master,
                bg='#F0F0F0',
                font=self.font_default_small,
                fg='black',
                width=7,
                height=1,
                anchor='w',
                justify='left',
                text='guttaes',
                )
            NG_U.pack()
            Min_size_G_U = Label(  # ,wraplength=700
                self.master,
                bg='#F0F0F0',
                font=self.font_default_small,
                fg='black',
                width=7,
                height=1,
                anchor='w',
                justify='left',
                text=micro,
                )
            Min_size_G_U.pack()
            Max_size_G_U = Label(  # ,wraplength=700
                self.master,
                bg='#F0F0F0',
                font=self.font_default_small,
                fg='black',
                width=7,
                height=1,
                anchor='w',
                justify='left',
                text=micro,
                )
            Max_size_G_U.pack()
            Average_G_U = Label(  # ,wraplength=700
                self.master,
                bg='#F0F0F0',
                font=self.font_default_small,
                fg='black',
                width=7,
                height=1,
                anchor='w',
                justify='left',
                text=micro,
                )
            Average_G_U.pack()
            
            Area_ratio_U = Label(  # ,wraplength=700
                self.master,
                bg='#F0F0F0',
                font=self.font_default_small,
                fg='black',
                width=7,
                height=1,
                anchor='w',
                justify='left',
                text='%',
                )
            Area_ratio_U.pack()
            
            Area_ratio_G_U = Label(  # ,wraplength=700
                self.master,
                bg='#F0F0F0',
                font=self.font_default_small,
                fg='black',
                width=7,
                height=1,
                anchor='w',
                justify='left',
                text='%',
                )
            Area_ratio_G_U.pack()
            
            Introduce_CD_u.place(x=300 + 30, y=80)
        else:

            Introduce_CD_u = Label(
                self.master,
                bg='#F0F0F0',
                fg='black',
                width=10,
                height=1,
                anchor='w',
                justify='left',
                text='cell/mm2',
                )
            Introduce_CD_u.pack()
            New_CD_U = Label(  # ,wraplength=500
                self.master,
                bg='#F0F0F0',
                fg='black',
                width=12,
                height=1,
                anchor='w',
                justify='right',
                text='cell/mm2',
                )
            New_CD_U.pack()
            NC_U = Label(  # ,wraplength=500
                self.master,
                bg='#F0F0F0',
                fg='black',
                width=12,
                height=1,
                anchor='w',
                justify='left',
                text='cells',
                )
            NC_U.pack()
            Min_size_U = Label(  # ,wraplength=500
                self.master,
                bg='#F0F0F0',
                fg='black',
                width=12,
                height=1,
                anchor='w',
                justify='left',
                text=micro,
                )
            Min_size_U.pack()
            Max_size_U = Label(  # ,wraplength=500
                self.master,
                bg='#F0F0F0',
                fg='black',
                width=12,
                height=1,
                anchor='w',
                justify='left',
                text=micro,
                )
            Max_size_U.pack()
            Average_U = Label(  # ,wraplength=500
                self.master,
                bg='#F0F0F0',
                fg='black',
                width=12,
                height=1,
                anchor='w',
                justify='left',
                text=micro,
                )
            Average_U.pack()
            GD_U = Label(  # ,wraplength=500
                self.master,
                bg='#F0F0F0',
                fg='black',
                width=12,
                height=1,
                anchor='w',
                justify='left',
                text='guttae/mm2',
                )
            GD_U.pack()
            NG_U = Label(  # ,wraplength=500
                self.master,
                bg='#F0F0F0',
                fg='black',
                width=12,
                height=1,
                anchor='w',
                justify='left',
                text='guttaes',
                )
            NG_U.pack()
            Min_size_G_U = Label(  # ,wraplength=500
                self.master,
                bg='#F0F0F0',
                fg='black',
                width=12,
                height=1,
                anchor='w',
                justify='left',
                text=micro,
                )
            Min_size_G_U.pack()
            Max_size_G_U = Label(  # ,wraplength=500
                self.master,
                bg='#F0F0F0',
                fg='black',
                width=12,
                height=1,
                anchor='w',
                justify='left',
                text=micro,
                )
            Max_size_G_U.pack()
            Average_G_U = Label(  # ,wraplength=500
                self.master,
                bg='#F0F0F0',
                fg='black',
                width=12,
                height=1,
                anchor='w',
                justify='left',
                text=micro,
                )
            Average_G_U.pack()
            Area_ratio_U = Label(  # ,wraplength=700
                self.master,
                bg='#F0F0F0',
                font=self.font_default_small,
                fg='black',
                width=7,
                height=1,
                anchor='w',
                justify='left',
                text='%',
                )
            Area_ratio_U.pack()
            
            Area_ratio_G_U = Label(  # ,wraplength=700
                self.master,
                bg='#F0F0F0',
                font=self.font_default_small,
                fg='black',
                width=7,
                height=1,
                anchor='w',
                justify='left',
                text='%',
                )
            Area_ratio_G_U.pack()
            Introduce_CD_u.place(x=300, y=80)

        New_CD_U.place(x=220, y=200)
        NC_U.place(x=220, y=240)
        Min_size_U.place(x=220, y=280)
        Max_size_U.place(x=220, y=320)
        Average_U.place(x=220, y=360)
        GD_U.place(x=540, y=200)
        NG_U.place(x=540, y=240)
        Min_size_G_U.place(x=540, y=280)
        Max_size_G_U.place(x=540, y=320)
        Average_G_U.place(x=540, y=360)
        Area_ratio_U.place(x=220, y=400)
        Area_ratio_G_U.place(x=540, y=400)
        

        self.Introduce_CD_entry = Entry(self.master, justify='center',
                state='disabled', width=15)
        self.Introduce_CD_entry.name = 'CD_entry'
        self.Introduce_CD_entry.bind('<Return>', lambda e: None)
        self.Introduce_CD_entry.pack()
        self.Introduce_CD_entry.place(x=180, y=80)
        self.after_id = self.master.after(0, self.update_GUI_messages)

    def show_help(self, button, event=None):
        messagebox.showinfo('Information',
                            self.mensajes_botones[button])

    def disable_buttons(self, to_disable=[], but=[]):
        if len(but) > 0 and len(to_disable) > 0:
            raise Exception('ERROR! Can not especify both "to_disable" and "but"'
                            )
        for name in self.buttons:
            if len(but) > 0 and name not in but:
                self.buttons[name].config(state='disable')
            if len(to_disable) > 0 and name in to_disable \
                or len(to_disable) == 0 and len(but) == 0:
                self.buttons[name].config(state='disable')

    def enable_buttons(self, to_enable=[], but=[]):
        if len(but) > 0 and len(to_enable) > 0:
            raise Exception('ERROR! Can not especify both "to_enable" and "but"'
                            )

        for name in self.buttons:
            if len(but) > 0 and name not in but:
                self.buttons[name].config(state='normal')

            if len(to_enable) > 0 and name in to_enable \
                or len(to_enable) == 0 and len(but) == 0:
                self.buttons[name].config(state='normal')

    def config_buttons(self, buttons, **kargs):

        for name in buttons:
            try:
                self.buttons[name].config(**kargs)
            except KeyError:
                if name == 'Previous' or name == 'Next':
                    pass
                else:
                    raise Exception('ERROR! The button "' + name
                                    + '" do not exist')
                    break

    def entry_unfocus(self):
        global enable_blink, texto
        x = self.master.winfo_pointerx() - self.master.winfo_rootx()
        y = self.master.winfo_pointery() - self.master.winfo_rooty()
        if x > 180 + 124 or x < 180 or y < 80 or y > 80 + 19:

            self.image.focus_set()
            if self.mensajes.cget('fg') != 'red':
                self.mensajes.config(fg='#F0F0F0')
            self.enable_blink = 0

    def update_GUI_messages(self, event=None):
        if self.normal_update:
            return
        try:
            if self.widget_actual.name == 'CD_entry':
                self.master.bind('<Button-1>', lambda e: \
                                 self.entry_unfocus)
        except AttributeError:
            self.master.bind('Button-1>', lambda e: None)

        if self.yapaso == 1:
            self.yapaso = 0
            self.timeout = 500
            self.color = 'black'

        if self.timeout == 3000:
            self.yapaso = 1
            self.mensajes.config(fg=self.color)
            self.mensajes.config(text=self.texto)
            self.texto = 'Press <INTRO> to finish'
            self.after_id = self.master.after(self.timeout,
                    self.update_GUI_messages)
        else:

            self.widget_actual = self.master.focus_get()
            try:
                if self.widget_actual.name == 'CD_entry':
                    self.enable_blink = 1
            except AttributeError:
                pass

            if self.enable_blink == 1:
                if self.mensajes.cget('fg') != '#F0F0F0':
                    self.mensajes.config(fg='#F0F0F0')
                    self.mensajes.config(text=self.texto)
                    self.after_id = self.master.after(300,
                            self.update_GUI_messages)
                else:
                    self.mensajes.config(fg=self.color)
                    self.after_id = self.master.after(self.timeout,
                            self.update_GUI_messages)
            else:
                self.mensajes.config(fg='#F0F0F0')
                self.mensajes.config(text=self.texto)
                self.after_id = self.master.after(self.timeout,
                        self.update_GUI_messages)

    def update_values_GUI(self, data):
        self.data = data.copy()
        imagen = ImageTk.PhotoImage(self.data['imagen_actual'])
        self.imagen_actual = self.data['imagen_actual']
        self.image['image'] = imagen
        self.image.imagen = imagen
        self.data['guttas'] = data['guttas']
        self.data['Ax'] = data['Ax']
        self.data['count'] = data['count']
        self.data['CG'] = data['CG']
        self.data['LG'] = data['LG']
        self.data['Total_Area'] = data['Total_Area']
        self.data['inverted_image'] = data['inverted_image']
        self.data['Imagen_Segmentacion'] = data['Imagen_Segmentacion']
        for name in self.value_labels:
            if 'ratio' in name:
                self.value_labels[name].configure(text='{:.2f}'.format(self.data[name]))
            else:
                self.value_labels[name].configure(text='{:.2f}'.format(self.data[name]).rstrip('0'
                    ).rstrip('.'))
        self.nombre_archivo.config(text=self.data['Nombre_Archivo'])

    def raise_above_all(self):
        if 'Windows' in self.OS:
            self.master.attributes('-topmost', 1)
            self.master.focus_force()
            self.master.attributes('-topmost', 0)

    def buscar(self, resetear=None):
        if not resetear:
            rep = filedialog.askopenfilenames(parent=self.master,
                    initialdir=self.dir_path, initialfile='tmp',
                    filetypes=[('TIF', '*.tif *.TIF')])
            self.rep = rep
        rep = self.rep

        try:
            if 'Windows' in self.OS:
                init = rep[0].rfind('/')
            elif 'Linux' in self.OS:
                init = rep[1].rfind('/')
            else:
                self.OS = 'Mac'
                init = rep[0].rfind('/')
        except IndexError:
            return 

        if 'Windows' in self.OS:
            self.file_path = rep[0]
        elif 'Linux' in self.OS:
            self.file_path = rep[1]
        else:
            self.file_path = rep[0]

        im = Image.open(self.file_path)
        self.im = im
        im.seek(1)
        try:
            im.seek(2)
            print ('FILE ERROR! The selected file have 3 channels. Please select a 2 channel .Tif file')
            self.file_path = None
            self.rep = None
            return
        except:
            pass

        imgCD = im.crop((490, 178, 640, 196))
        self.trabajando_sobre = self.file_path[init + 1:len(rep[0]) - 4]
        self.nombre_archivo.config(text=self.file_path[init
                                   + 1:len(rep[0]) - 4])
        self.Introduce_CD_entry.config(state='normal')
        imgCD = ImageTk.PhotoImage(imgCD)
        self.imageCD['image'] = imgCD
        self.imageCD.imgCD = imgCD
        return self.file_path
        self.guardo = False

    def saveBox(
        self,
        title='Guardar imagen como...',
        fileExt='.tif',
        fileTypes=None,
        asFile=False,
        just_save=False,
        ):

        if self.trabajando_sobre != None and just_save:
            return self.trabajando_sobre

        if fileTypes is None:
            fileTypes = [('TIF image', '.tif'), ('all files', '.*')]

        # define options for opening

        options = {}
        options['defaultextension'] = fileExt
        options['filetypes'] = fileTypes
        options['title'] = title

        if asFile:
            trabajando_sobre = filedialog.asksaveasfile(mode='w',
                    **options)
            if 'numpy' in str(type(self.imagen_actual)):
                self.imagen_actual = Image.fromarray(self.imagen_actual)
            self.imagen_actual.save(trabajando_sobre)
        else:

        # will return "" if cancelled

            trabajando_sobre = filedialog.asksaveasfilename(**options)
            if 'numpy' in str(type(self.imagen_actual)):
                self.imagen_actual = Image.fromarray(self.imagen_actual)
            try:
                self.imagen_actual.save(trabajando_sobre)
            except ValueError:
                pass

        # self.file_path=trabajando_sobre

        init = trabajando_sobre.rfind('/')
        self.trabajando_sobre = trabajando_sobre[init
            + 1:len(trabajando_sobre[0]) - 4]
        if self.trabajando_sobre[-1]=='.':
            self.trabajando_sobre=self.trabajando_sobre[0:-1]
        self.nombre_archivo.config(text=self.trabajando_sobre)
        return trabajando_sobre

    def ventana_zoom(self):
        win = Toplevel(self.master) 
        y=self.master.winfo_rooty()
        x=self.anchoCanvas+self.master.winfo_rootx()
        win.image = Label(win, bg='#F0F0F0')
        win.image.pack()
        win.image.place(x=0, y=0)
        win.geometry("500x500+"+str(int(x))+"+"+str(int(y)))
        win.wm_title("Zoom")
        self.zoom_image=win
        
    def update_zoom_image(self,imagen):
        imagen=imagen=ImageTk.PhotoImage(imagen)
        self.zoom_image.image['image'] = imagen
        self.zoom_image.image.imagen = imagen
        

def test():
    ventana = Tk()
    GUI = SecCorrectorGUI(ventana)
    GUI.disable_buttons()
    GUI.config_buttons(buttons=['Select_F'], state='normal',
                       command=GUI.buscar)
    GUI.raise_above_all()
    
    ventana.update()
    GUI.ventana_zoom()
    ventana.mainloop()


#test()



			