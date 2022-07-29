"""
Uso de la libreia Tknder que nos permite la utilizacion de los comando y herramientas para la creacion de una interfaz
en base a código limpio y estable.
"""
from cgitb import text
from email import message
from email.mime import image
from itertools import tee
import logging
from operator import eq
from sqlite3 import Row
import tkinter as tk
import tkinter
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import font
from urllib.parse import ParseResultBytes
from uuid import getnode
from bson import ObjectId

import datetime
import requests
import os
import argparse
import re
import json
from dateutil.easter import easter
from dateutil.relativedelta import relativedelta as rd, FR
from holidays.constants import JAN, MAY, AUG, OCT, NOV, DEC
from holidays.holiday_base import HolidayBase

import pymongo

class FeriadoEcuador(HolidayBase):
    """
    Una clase que representar el feriado en Ecuador por provincia (FeriadoEcuador)
     Su objetivo es determinar si un fecha especifica es unas vacaciones lo mas 
     rapido y flexible posible.
     https://www.turismo.gob.ec/wp-content/uploads/2020/03/CALENDARIO-DE-FERIADOS.pdf
     ...
     Atributos (Se hereda en la clase HolidayBase)
     ----------
     prov: str
         codigo de provincia segun ISO3166-2
     Métodos
     -------
     __init__(self, placa, fecha, hora, en linea=False):
         Construye todos los atributos necesarios para el objeto HolidayEcuador.
     _poblar(self, año):
         Devuelve si una fecha es feriado o no
    """     
    # ISO 3166-2 códigos para la subdivisión principal, 
    # llamado provincias
    # https://es.wikipedia.org/wiki/ISO_3166-2:EC
    PROVINCIA = ["EC-P"]  # TODO agregar más provincias

    def __init__(self, **kwargs):
        """
       Contructor con todos los métodos necesario para los dias festivos de Ecuador.
        """         
        self.pais = "Ecuador"
        self.prov = kwargs.pop("provincia", "ON")
        HolidayBase.__init__(self, **kwargs)

    def _poblacion(self, año):
        """
        Revisa si una fecha es feriado o no
        
         Parámetros
         ----------
         año: str
             año de una fecha
         Devuelve
         -------
         Devuelve "verdadero" si una fecha es un día festivo, caso contrario da falso.
        """                    
        #Año Nuevo 
        self[datetime.date(año, JAN, 1)] = "Año Nuevo [Nuevo año]"
        
        #Navidades
        self[datetime.date(año, DEC, 25)] = "Navidad [Navidades]"
        
        #Semana Sata
        self[easter(año) + rd(weekday=FR(-1))] = "Semana Santa (Viernes Santo) [Good Friday)]"
        self[easter(año)] = "D a de Pascuas [Easter Day]"
        
        #Carnavales
        total_dias_libres = 46
        self[easter(año) - datetime.timedelta(days=total_dias_libres+2)] = "Lunes de carnaval [Carnival of Monday)]"
        self[easter(año) - datetime.timedelta(days=total_dias_libres+1)] = "Martes de carnaval [Tuesday of Carnival)]"
        
        # Dia nacional del trabajador
        nombre = "Día Nacional del Trabajo [Día del laborador]"
        # (Ley 858/Ley de Reforma a la LOSEP (vigente desde el 21 de diciembre de 2016 /R.O # 906)) Si el feriado cae un sábado o martes
        # el descanso obligatorio será trasladado al viernes o lunes
        # respectivamente:
        if año > 2015 and datetime.date(año, MAY, 1).weekday() in (5,1):
            self[datetime.date(año, MAY, 1) - datetime.timedelta(days=1)] = nombre
        # (Ley 858/Ley de Reforma a la LOSEP (vigente desde el 21 de diciembre de 2016 /R.O # 906)) si el feriado cae un domingo
        # el descanso obligatorio sera para el lunes
        elif año > 2015 and datetime.date(año, MAY, 1).weekday() == 6:
            self[datetime.date(año, MAY, 1) + datetime.timedelta(days=1)] = nombre
        # (Ley 858/Ley de Reforma a la LOSEP (vigente desde el 21 de diciembre de 2016 /R.O # 906)) Feriados que sean en mi rcoles o jueves
        # se moverán al viernes de esa semana
        elif año > 2015 and  datetime.date(año, MAY, 1).weekday() in (2,3):
            self[datetime.date(año, MAY, 1) + rd(weekday=FR)] = nombre
        else:
            self[datetime.date(año, MAY, 1)] = nombre
        
        # La Batalla de Pichincha, tiene las mismas raglas del dia del trabajador
        nombre = "La batalla del Pichincha [Batalla de Pichincha]"
        if año > 2015 and datetime.date(año, MAY, 24).weekday() in (5,1):
            self[datetime.date(año, MAY, 24).weekday() - datetime.timedelta(days=1)] = nombre
        elif año > 2015 and datetime.date(año, MAY, 24).weekday() == 6:
            self[datetime.date(año, MAY, 24) + datetime.timedelta(days=1)] = nombre
        elif año > 2015 and  datetime.date(año, MAY, 24).weekday() in (2,3):
            self[datetime.date(año, MAY, 24) + rd(weekday=FR)] = nombre
        else:
            self[datetime.date(año, MAY, 24)] = nombre
        
        #El Primer grito de Independencia, tiene las mismas raglas del dia del trabajador
        nombre = "El primer Grito de la Independencia [Primer grito de independencia]"
        if año > 2015 and datetime.date(año, AUG, 10).weekday() in (5,1):
            self[datetime.date(año, AUG, 10)- datetime.timedelta(days=1)] = nombre
        elif año > 2015 and datetime.date(año, AUG, 10).weekday() == 6:
            self[datetime.date(año, AUG, 10) + datetime.timedelta(days=1)] = nombre
        elif año > 2015 and  datetime.date(año, AUG, 10).weekday() in (2,3):
            self[datetime.date(año, AUG, 10) + rd(weekday=FR)] = nombre
        else:
            self[datetime.date(año, AUG, 10)] = nombre       
        
        #La Independencia de Guayaquil, tiene las mismas raglas del dia del trabajador
        nombre = "La independencia de Guayaquil [Independencia de Guayaquil]"
        if año > 2015 and datetime.date(año, OCT, 9).weekday() in (5,1):
            self[datetime.date(año, OCT, 9) - datetime.timedelta(days=1)] = nombre
        elif año > 2015 and datetime.date(año, OCT, 9).weekday() == 6:
            self[datetime.date(año, OCT, 9) + datetime.timedelta(days=1)] = nombre
        elif año > 2015 and  datetime.date(año, MAY, 1).weekday() in (2,3):
            self[datetime.date(año, OCT, 9) + rd(weekday=FR)] = nombre
        else:
            self[datetime.date(año, OCT, 9)] = nombre        
        
        #Dia de los Difuntos
        nombreagregar = "Día de los difuntos [Día de difuntos]" 
        # Independencia de Cuenca
        nombreic = "Independencia de Cuenca [Independence of Cuenca]"
        #(Ley 858/Ley de Reforma a la LOSEP (vigente desde el 21 de diciembre de 2016/R.O # 906))
        #Para festivos nacionales y/o locales que coincidan en días corridos,
        #serán aplicadas las siguientes reglas:
        if (datetime.date(año, NOV, 2).weekday() == 5 and  datetime.date(año, NOV, 3).weekday() == 6):
            self[datetime.date(año, NOV, 2) - datetime.timedelta(days=1)] = nombreagregar
            self[datetime.date(año, NOV, 3) + datetime.timedelta(days=1)] = nombreic     
        elif (datetime.date(año, NOV, 3).weekday() == 2):
            self[datetime.date(año, NOV, 2)] = nombreagregar
            self[datetime.date(año, NOV, 3) - datetime.timedelta(days=2)] = nombreic
        elif (datetime.date(año, NOV, 3).weekday() == 3):
            self[datetime.date(año, NOV, 3)] = nombreic
            self[datetime.date(año, NOV, 2) + datetime.timedelta(days=2)] = nombreagregar
        elif (datetime.date(año, NOV, 3).weekday() == 5):
            self[datetime.date(año, NOV, 2)] =  nombreagregar
            self[datetime.date(año, NOV, 3) - datetime.timedelta(days=2)] = nombreic
        elif (datetime.date(año, NOV, 3).weekday() == 0):
            self[datetime.date(año, NOV, 3)] = nombreic
            self[datetime.date(año, NOV, 2) + datetime.timedelta(days=2)] = nombreagregar
        else:
            self[datetime.date(año, NOV, 2)] = nombreagregar
            self[datetime.date(año, NOV, 3)] = nombreic  
            
        #Fundación de Quito (Aplica solo para la provincia de Pichincha)
        #Las reglas son las mismas que el día del trabajo
        nombre = "La fundación de Quito [Fundación de Quito]"        
        if self.prov in ("EC-P"):
            if año > 2015 and datetime.date(año, DEC, 6).weekday() in (5,1):
                self[datetime.date(año, DEC, 6) - datetime.timedelta(days=1)] = nombre
            elif año > 2015 and datetime.date(año, DEC, 6).weekday() == 6:
                self[(datetime.date(año, DEC, 6).weekday()) + datetime.timedelta(days=1)] =nombre
            elif año > 2015 and  datetime.date(año, DEC, 6).weekday() in (2,3):
                self[datetime.date(año, DEC, 6) + rd(weekday=FR)] = nombre
            else:
                self[datetime.date(año, DEC, 6)] = nombre

class Usuario:
    """
    Creación de la clase Usuarios en la cual tiene los siguietnes atributos y métodos:

    Atributos:
    ----------
    nombre: str
    apellido:str
    gmail: str
    usuario:str
    contrasena: str
    fechaNacimiento: str
    sexo: str

    Metodos:
    --------
    def __init__(self,nombre,apellido,gmail,usuario,contrasena,fechaNacimiento,sexo):
        Método de contrcutor que contiene los atributos de la clase.
    def iniciarSesion(self,user,login):
        Método de contrcutor que los atributos de inicio de sesión.
    """
    def __init__(self,nombre,apellido,gmail,usuario,contrasena,fechaNacimiento,sexo):
        """
        Método de constructor en el cual contiene los atributos de la clase.

        Atributos:
        -----------
        nombre: str
            nombre de a persona
        apellido: str
            apellido de la persona
        gmail: str
            correo de la persona
        usuario: str
            usuario de la persona
        contrasena: str
            contraseña d ela persona
        fechaNAcimiento: str
            fecha de nacimiento de la persona
        sexo: str
            sexualidad de la persona.

        """
        self.nombre=nombre
        self.apellido=apellido
        self.gmail=gmail
        self.usuario=usuario
        self.contrasena=contrasena
        self.fechaNacimiento=fechaNacimiento
        self.sexo=sexo
    def iniciar(self,user,login):
        """
        Método contructor que dara paso a el usuario y contraseña

        Atributos:
        ---------
        user:str
            usuario de la persona a verificar
        login: str
            contraseña del usuario a verificar
        
        """
        self.user=user
        self.login=login
        pass
class Application(ttk.Frame):
    """
    Creación de la clase Aplicacion en la cual tiene los siguietnes atributos y métodos:

    Atributos:
    ----------
    combo: opcion
        Creacion de lista de seleccion.
    
    Méetodos:
    ----------
    def __init__(self, main_window):
        Método de constructor que contendra los atributos y mostrar en pantalla la interfaz a mostrar.
    def selection_changed(self, event):
        Método de constructor que
    """
    def __init__(self, main_window):
        super().__init__(main_window)
        main_window.title("BIBLIOTECA VIRTUAL SANTO DOMINGO TSÁCHILAS")
        self.combo = ttk.Combobox(
            self,
            values=["Reportes", "Descuentos"]
        )
        self.combo.bind("<<ComboboxSelected>>", self.seleccionar)
        self.combo.place(x=50, y=50)

        self.mostrarTexto=tk.Label(main_window, text = "Buscar Libro")
        self.mostrarTexto.config(bg= "white", font=font.Font(family="Arial", size = "10"))
        self.mostrarTexto.place(x=75, y=75)
        self.buscarLibro=tk.Entry(main_window, font=font.Font(family="Times New Roman", size = "10"),textvar="", width=31, relief="flat")
        self.buscarLibro.place(x=100, y=100)

        self.buscar=Button(main_window, text="Buscar Libro", command=buscarLibros)
        self.buscar.place(x=150, y=130)
        main_window.config(width=500, height=200)
        self.place(width=300, height=200)
        
    def seleccionar(self, event):
        selection = self.combo.get()
        message=selection
        if message=="Reportes":
            Reports()
        elif message=="Descuentos":
            Descuentos()
        else:
            messagebox.showinfo(
            title="Elemento No encontrado",
        )
def buscarLibros():
    libro = coleccion2.find_one()
    messagebox.showinfo(
        title="Libro encontrado",
        message=libro
    )

def Reports():
    """
    Método en el cual su funcion es mostrar los reportes de Editorial, Año de un libro.
    """
    ventanaReportes=tk.Tk()
    ventanaReportes.title("Reportes de la Bibloteca")
    ventanaReportes.geometry("500x200+0+0")
    ventanaReportes.resizable(width="False", height="False")
    ventanaReportes.config(bg="light green")
    opcionEditorial=tkinter.Button(ventanaReportes, text="Reporte de Editorial", command=lambda: Editorial)
    opcionEditorial.pack()
    opcionEditorial=tkinter.Button(ventanaReportes, text="Reporte de Años", command=lambda: añoLibro)
    opcionEditorial.pack()
    opcionRegresar=tkinter.Button(ventanaReportes, text="Regresar", command=lambda: atras(ventanaReportes))
    opcionRegresar.pack()
    ventanaReportes.mainloop()
def Descuentos():
    """
    Método en el cual su función es mostrar los descuentos de los libros que hay.
    """
    ventanaDescuentos=tk.Tk()
    ventanaDescuentos.title("Descuentos de la Bibloteca")
    ventanaDescuentos.geometry("480x270+0+0")
    ventanaDescuentos.config(bg="light blue")
    opcionRegresar=tkinter.Button(ventanaDescuentos, text="Regresar", command=lambda: atras(ventanaDescuentos))
    opcionRegresar.pack()
    ventanaDescuentos.mainloop()


def Editorial():
    """
    Método qe muestra el reporte de los editoriales de los libros.
    """
    ventanaEditorial=tk.Tk()
    ventanaEditorial.title("Reportes del Editorial de los libros.")
    ventanaEditorial.geometry("480x270+0+0")
    ventanaEditorial.resizable(width="False", height="False")
    opcionRegresar=tkinter.Button(ventanaEditorial, text="Regresar", command=lambda: atras(ventanaEditorial))
    opcionRegresar.pack()
    ventanaEditorial.mainloop()  

def añoLibro():
    """
    Método qe muestra el reporte de los editoriales de los libros.
    """
    ventanaLibro=Tk()
    ventanaLibro.title("Reportes de Años de los libros")
    ventanaLibro.geometry("480x270+0+0")
    ventanaLibro.resizable(width="False", height="False")
    opcionRegresar=tkinter.Button(ventanaLibro, text="Regresar", command=lambda: atras(ventanaLibro))
    opcionRegresar.pack()
    ventanaLibro.mainloop() 
def baseDatos():
    pass

def atras(ventana_a_cerrar):
    """
    Método para regresar a la ventana anterior sin estar abriendo otra vez el codigo
    """
    ventana_a_cerrar.destroy()
    ventana.deiconify()
"""
Creacion de la interfaz por medio de tkinder.
En ella vamos a configurar como va hacer nuestra ventan al momento de iniciar en ella, en el cual tenemos lo siguiente:

ventana=Tk()<- Inicio de la creacion de la interfaz.
ventana.title("Bibloteca Virtual Santo Domingo")<- Titulo que tendra la interfaz
ventana.geometry("480x270+0+0")<-El tamaño que tomara la interfaz cuando se muestre.
fondo = PhotoImage(file = "fondo.gif") <- Asignacion de la foto para el fondo de la pantalla
lblFondo = Label(ventana, image=fondo ).place(x=0,y=0) <- Ingreso de la imagen en uestra interfaz
"""
ventana=Tk()
ventana.title("Bibloteca Virtual Santo Domingo")
ventana.geometry("444x200+0+0")
ventana.resizable(width="False", height="False")
fondo = PhotoImage(file = "imagenInicio.gif")
lblFondo = Label(ventana, image=fondo ).place(x=0,y=0)

def InicioSesion():
    """    
    Método que contendra la interfaz para el inicio de sesion de nuestro codigo 
    """
    ventanaSesion= tk.Tk()
    ventanaSesion.title("INICIAR SESION")
    """
    Ajustes de la interfaz de de inicio de sesion.
    """
    ventanaSesion.geometry("350x250")
    ventanaSesion.resizable(width="False", height="False")
    ventanaSesion.config(bg="aliceblue")

    #Ocultamiento de la ventana principal
    ventana.withdraw()
    """
    Entrada de texto para poder verificar si los datos son los correctos.
    """
    mostrarTexto=tk.Label(ventanaSesion, text = "Usuario")
    mostrarTexto.config(bg= "white", font=font.Font(family="Arial", size = "10"))
    mostrarTexto.pack()
    entradaUsuario=tk.Entry(ventanaSesion, font=font.Font(family="Arial", size = "10"),textvar="", width=32, relief="flat")
    entradaUsuario.pack()
    mostrarTexto=tk.Label(ventanaSesion, text = "Contraseña")
    mostrarTexto.config(bg= "white", font=font.Font(family="Arial", size = "10"))
    mostrarTexto.pack()
    entradaContrasena=tk.Entry(ventanaSesion, font=font.Font(family="Arial", size = "10"),textvar="", width=31, relief="flat")
    entradaContrasena.pack()
    validarInfoB= tk.Button(ventanaSesion, text= "Iniciar", cursor="hand1", bg= "#0a509f",fg= "black",  width=4, height=1, relief="flat", command = lambda: Validacion(entradaUsuario.get(),entradaContrasena.get())) 
    validarInfoB.pack()
    regreso2 = tkinter.Button(ventanaSesion, text="Regresar", command=lambda: atras(ventanaSesion))
    regreso2.pack()
    ventanaSesion.mainloop()

def RegistroMongo():
    """
    Método en el cual es la interfaz donde se ingresa los datos a la Base de datos de mongo
    """
    ventanaRegistro = tkinter.Tk()
    ventanaRegistro.title(" REGISTRARSE EN LA BIBLIOTECA")
    ventanaRegistro.geometry("400x400")
    ventanaRegistro.resizable(width="False", height="False")
    ventanaRegistro.config(bg="bisque")
    ventana.withdraw()
    """ Datos a pedir """
    mostrarTkMessage=tkinter.Label(ventanaRegistro, text="Nombre:")
    mostrarTkMessage.pack()
    """Entrada del nombre"""
    nombreTk = tkinter.Entry(ventanaRegistro)
    nombreTk.pack()
    """Datos a pedir"""
    mostrarTkMessage=tkinter.Label(ventanaRegistro, text="Apellido:")
    mostrarTkMessage.pack()
    """Entrada del apellido"""
    apellidoTK = tkinter.Entry(ventanaRegistro)
    apellidoTK.pack()
    """Datos a pedir"""
    mostrarTkMessage=tkinter.Label(ventanaRegistro, text="Gmail:")
    mostrarTkMessage.pack()
    """Entrada del gmail"""
    gmailTK = tkinter.Entry(ventanaRegistro)
    gmailTK.pack()
    """Datos a pedir"""
    mostrarTkMessage=tkinter.Label(ventanaRegistro, text="Fecha de Nacimiento:")
    mostrarTkMessage.pack()
    """Entrada de la fecha de nacimiento"""
    fechaNacimientoTK = tkinter.Entry(ventanaRegistro)
    fechaNacimientoTK.pack()
    """Datos a pedir"""
    mostrarTkMessage=tkinter.Label(ventanaRegistro, text="Sexo:")
    mostrarTkMessage.pack()
    """Entrada de la sexualidad"""
    sexoTk = tkinter.Entry(ventanaRegistro)
    sexoTk.pack()
    
    mostrarTkMessage=tkinter.Label(ventanaRegistro, text="Usuario:")
    mostrarTkMessage.pack()
    nombreUsuarioTk = tkinter.Entry(ventanaRegistro)
    nombreUsuarioTk.pack()

    mostrarTkMessage=tkinter.Label(ventanaRegistro, text="Contrasena:")
    mostrarTkMessage.pack()
    contrasenaTk = tkinter.Entry(ventanaRegistro)
    contrasenaTk.pack()

    #nombreUsuarioTK=nombreTk[0:3]+apellidoTK[0:3]
    #contrasenaTK=fechaNacimientoTK[0:3]+sexoTk[0:3]

    def agregar():
        mydict = {"nombre": nombreTk.get(), "apellidos": apellidoTK.get(), "gmail": gmailTK.get(), "sexo": sexoTk.get(), "fecha de nacimiento": fechaNacimientoTK.get(), "usuario": nombreUsuarioTk.get(), "contrasena": contrasenaTk.get()}
        agregarDatos = coleccion.insert_one(mydict)
        print(agregarDatos.inserted_id)
    
    """Creación de la guardar"""
    guardar= tkinter.Button(ventanaRegistro, text="Almacenar datos", command=agregar)
    guardar.pack()
    """Creación de un boto para regresar """
    regreso = tkinter.Button(ventanaRegistro, text="Regresar", command=lambda: atras(ventanaRegistro))
    regreso.pack()
    ventana.mainloop()

    


def usuarios():



    """
    Método que ayudará en la agregación de un dato en una lista creada de usuario y contraseña.


    Retorna:
    --------
    return coleccionUsuario & coleccionContrasena
        retorna la coleccion de usuario y contrasena.
    """ 
    coleccionTotal=coleccion.find()
    coleccionUsuario=[]

    """
    Condicional for que ingresa a la lista los datos de usuario y contrasena.
    """
    for i in coleccionTotal:
        coleccionUsuario.append(i['usuario'])
    return coleccionUsuario


def contrasenaBiblioteca():
    coleccionTotalContrasena=coleccion.find()
    coleccionContrasena=[]
    for i in coleccionTotalContrasena:
     coleccionContrasena.append(i['contrasena'])
    return coleccionContrasena

def Validacion(usuario,contrasena):
    """
    Método de contructor que nos hace conocer si la operacion logica es la correcta dentro de este
    mismo para que este.
    """
    user= usuarios()
    login= contrasenaBiblioteca()
    if usuario in user and contrasena in login:
        main_window = tk.Tk()
        app = Application(main_window)
        app.mainloop()
    else:
        messagebox.showwarning("Error, usuario y contraseña no coinciden")


if __name__=="__main__":

    myclient= pymongo.MongoClient("mongodb://localhost:27017/")
    MONGO_BASED= "registroBiblioteca"
    COLECCION= "users"
    baseDatos=myclient[MONGO_BASED]
    coleccion = baseDatos[COLECCION]
    
    MONGO_BASED2= "bibliotecaDigital"
    COLECCION2= "libros"
    baseDatos=myclient[MONGO_BASED2]
    coleccion2 = baseDatos[COLECCION2]

    """
    Muestra de la selección en la cual podemos seleccionar a que opción podemos ingresar.
    
    En el cual al momento de ingresar nos mostrarä las siguientes opciones:
    
    Resgitarse
    Inicio de Sesión
    Cerrar
    """
    mensajeTexto=Label(ventana, text="Bienvenido a la biblioteca virtual de Santo Domingo de los Tsáchilas",fg= "black")
    mensajeTexto.pack()
    registrar=tk.Button(ventana, font=("Times New Roman", 9), text= "Registrarse", cursor="hand1", highlightbackground="white",fg= "black",  width=9, height=2, command = RegistroMongo)
    registrar.place(x=190, y= 25)
    inicioSesion=tk.Button(ventana, font=("Times New Roman", 8), text= "Inicio de Sesión", cursor="hand1", highlightbackground="white",fg= "black",  width=9, height=2, command = InicioSesion)
    inicioSesion.place(x=190, y= 80)
    cerrar=Button(ventana, font=("Times New Roman", 13) ,text="Cerrar", highlightbackground="white",command=ventana.quit)
    cerrar.place(x=190, y=150)

"""
El cierre de la interfaz
"""
ventana.mainloop()
    

    
    

        