import sys
#Qfiledialog es una ventana para abrir yu gfuardar archivos
#Qvbox es un organizador de widget en la ventana, este en particular los apila en vertcal
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QFileDialog
from PyQt5 import QtCore, QtWidgets

from matplotlib.figure import Figure

from PyQt5.uic import loadUi

from numpy import arange, sin, pi
#contenido para graficos de matplotlib
from matplotlib.backends. backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

import scipy.io as sio
import numpy as np
from Modelo import Biosenal
# clase con el lienzo (canvas=lienzo) para mostrar en la interfaz los graficos matplotlib, el canvas mete la grafica dentro de la interfaz
class MyGraphCanvas(FigureCanvas):
    #constructor
    def __init__(self, parent= None,width=5, height=4, dpi=100):
        
        #se crea un objeto figura
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        #el axes en donde va a estar mi grafico debe estar en mi figura
        self.axes = self.fig.add_subplot(111)
        
        #llamo al metodo para crear el primer grafico
        self.compute_initial_figure()
        
        #se inicializa la clase FigureCanvas con el objeto fig
        FigureCanvas.__init__(self,self.fig)
        
    #este metodo me grafica al senal senoidal 
    def compute_initial_figure(self):
        t = arange(0.0, 3.0, 0.01)
        s = sin(2*pi*t)
        self.axes.plot(t,s)
    #hay que crear un metodo para graficar lo que quiera
    def graficar_gatos(self,datos):
        #primero se necesita limpiar la grafica anterior
        self.axes.clear()
        #ingresamos los datos a graficar
        self.axes.plot(datos)
        #y lo graficamos
        
        #voy a graficar en un mismo plano varias senales que no quecden superpuestas cuando uso plot me pone las graficas en un mismo grafico
        for c in range(datos.shape[0]):
            self.axes.plot(datos[c,:]+c*10)
        self.axes.set_xlabel("muestras")
        self.axes.set_ylabel("voltaje (uV)")
        #self.axes.set
        #ordenamos que dibuje
        self.axes.figure.canvas.draw()

        #es una clase que yop defino para crear los intefaces graficos
class InterfazGrafico(QMainWindow):
    senales = dict()    
    senalSelected=[]
    
    
    def __init__(self):
        #siempre va
        super(InterfazGrafico,self).__init__()
        #se carga el diseno
        loadUi ('grafico.ui',self)
        #se llama la rutina donde configuramos la interfaz
        self.setup()
        #se muestra la interfaz
        self.show()
    def setup(self):
        #los layout permiten organizar widgets en un contenedor
        #esta clase permite aÃ±adir widget uno encima del otro (vertical)
        layout = QVBoxLayout()
        layout2 = QVBoxLayout()
        #se aÃ±ade el organizador al campo grafico
        self.campo_grafico.setLayout(layout)
        self.campo_grafico2.setLayout(layout2)
        #se crea un objeto para manejo de graficos
        self.__sc = MyGraphCanvas(self.campo_grafico, width=5, height=4, dpi=100)
        self.__sc2 = MyGraphCanvas(self.campo_grafico2, width=5, height=4, dpi=100)
        #se aÃ±ade el campo de graficos
        layout.addWidget(self.__sc)
        layout2.addWidget(self.__sc2)
        
        #inputs y botones desactivados al inicio del flujo de la interfaz
        self.boton_adelante.setEnabled(False)
        self.boton_atras.setEnabled(False)
        self.boton_aumentar.setEnabled(False)
        self.boton_disminuir.setEnabled(False)
        self.boton_adelante_2.setEnabled(False)
        self.boton_atras_2.setEnabled(False)
        self.boton_aumentar_2.setEnabled(False)
        self.boton_disminuir_2.setEnabled(False)
        self.filtrar.setEnabled(False)
        self.ventana.setEnabled(False)
        self.fs.setEnabled(False)
        self.nooverlap.setEnabled(False)
        self.scaling.setEnabled(False)
        self.nperseg.setEnabled(False)
        self.reload.setEnabled(False)
        self.senalesDetectadas.setEnabled(False)
        self.senalSeleccionada.setEnabled(False)
        self.cargarSenal.setEnabled(False)
        
        #enlazar funciones
        self.boton_cargar.clicked.connect(self.cargar_senal)
        self.cargarSenal.clicked.connect(self.load_senal)
        
        
        #cuando cargue la senal debo volver a habilitarlos
    def asignar_Controlador(self,controlador):
        self.__coordinador=controlador
    def adelante_senal(self):
        self.__x_min=self.__x_min+2000
        self.__x_max=self.__x_max+2000
        self.__sc.graficar_gatos(self.__coordinador.devolverDatosSenal(self.__x_min,self.__x_max))
    def atrasar_senal(self):
        #que se salga de la rutina si no puede atrazar
        if self.__x_min<2000:
            return
        self.__x_min=self.__x_min-2000
        self.__x_max=self.__x_max-2000
        self.__sc.graficar_gatos(self.__coordinador.devolverDatosSenal(self.__x_min,self.__x_max))
    def aumentar_senal(self):
        #en realidad solo necesito limites cuando tengo que extraerlos, pero si los 
        #extraigo por fuera mi funcion de grafico puede leer los valores
        self.__sc.graficar_gatos(self.__coordinador.escalarSenal(self.__x_min,self.__x_max,2))
    def disminuir_senal(self):
        self.__sc.graficar_gatos(self.__coordinador.escalarSenal(self.__x_min,self.__x_max,0.5))
    
        
    def energy(signal):
        energy = np.sum(np.power(signal,2),0)
        return energy;    
    
    def cargar_senal(self):
        archivo_cargado, name= QFileDialog.getOpenFileName(self, "Abrir seÃ±al","","Todos los archivos (*);;Archivos mat (*.mat)*")
        if archivo_cargado != "":
            data=sio.loadmat(archivo_cargado)
            self.senales = dict()
            print(data.keys())
            for (key, value) in data.items():
                # Check if key is even then add pair to new dictionary
                if key != '__globals__' and  key != '__version__' and key != '__header__' and key != 'Fs' :
                    self.senales[key] = value
            print(self.senales.keys())
            text="<ol><p>Seleccione una de las siguientes senales</p>"            
            for i in self.senales.keys():
                text=text+"<li>"+i+"</li>"
            text=text+"</ol>"
            self.senalesDetectadas.setText(text) 
            self.senalSeleccionada.setEnabled(True)
            self.cargarSenal.setEnabled(True)
            
    def load_senal(self):
        
        cont=1
        if(int(self.senalSeleccionada.text())<=len(self.senales.keys()) and int(self.senalSeleccionada.text())>0):
            for i in self.senales.keys():
                if(int(self.senalSeleccionada.text())==cont): 
                    self.senalSelected=self.senales.get(i)
                cont=cont+1
                    
            print(self.senalSelected.shape)
             
            #self.senalSelected=np.reshape(senalSelected,(sensores,puntos*p),order="F")
            self.__coordinador.recibirDatosSenal(self.senalSelected)
            self.__x_min=0
            self.__x_max=16000
            self.__y_min=-58000
            self.__y_max=-55000
            #graficar utilizando el controlador
            self.__sc.graficar_gatos(self.__coordinador.devolverDatosSenal(self.__x_min,self.__x_max))
        else:
            print("fuera de rango")
                
    
       