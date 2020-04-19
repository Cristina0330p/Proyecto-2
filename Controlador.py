# -*- coding: utf-8 -*-
"""
Created on Sun Mar 22 22:50:52 2020

@author: Sara Cadavid - Cristina Pareja 

"""
#algo aca
# Se importa libreria necesaria para el funcionamiento del programa
from Modelo import Biosenal # De modelo importa la class Biosenal 
from interfaz import InterfazGrafico
import sys #Deja que el  programa ejecute 
from PyQt5.QtWidgets import QApplication #ejecucion de los programas para la interfaz 
class Principal(object): # con esta clase se conecta el modelo y la vista para poder trabajar con ambas clases 
    def __init__(self):        
        self.__app=QApplication(sys.argv)
        self.__mi_vista=InterfazGrafico() #se enlaza la funcion con una variable para su funcionamiento
        self.__mi_biosenal=Biosenal() #se enlaza la funcion con una variable para su funcionamiento
        self.__mi_controlador=Coordinador(self.__mi_vista,self.__mi_biosenal)
        self.__mi_vista.asignar_Controlador(self.__mi_controlador)
    def main(self):
        self.__mi_vista.show() # se muestra la ventana 
        sys.exit(self.__app.exec_()) 
    
class Coordinador(object): # Esta clase hace que comience la ejecución del programa 
    def __init__(self,vista,biosenal):
        self.__mi_vista=vista
        self.__mi_biosenal=biosenal
    def recibirDatosSenal(self,data): #función para recibir los datos se la señal que se cargue 
        self.__mi_biosenal.asignarDatos(data) #ejecuta la función asignarDatos 
    def devolverDatosSenal(self,x_min,x_max):
        return self.__mi_biosenal.devolver_segmento(x_min,x_max) #Devuelve el segmento seleccionado con un valor minimo y maximo
    def escalarSenal(self,x_min,x_max,escala):
        return self.__mi_biosenal.escalar_senal(x_min,x_max,escala)
p=Principal()
p.main()
