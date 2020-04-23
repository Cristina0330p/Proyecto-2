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
import scipy.signal as signal;
import scipy.io as sio
import numpy as np
from Modelo import Biosenal
import pywt
from chronux.mtspectrumc import mtspectrumc
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
    def graficar_espectro(self,time, freqs, power):
        #primero se necesita limpiar la grafica anterior
        self.axes.clear()
        #ingresamos los datos a graficar
        self.axes.contourf(time,
                 freqs[(freqs >= 4) & (freqs <= 40)],
                 power[(freqs >= 4) & (freqs <= 40),:],
                 20, # Especificar 20 divisiones en las escalas de color 
                 extend='both')
        #y lo graficamos
        print("datos")
        #ordenamos que dibuje
        self.axes.figure.canvas.draw()
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
    welch=[]
    
    
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
        self.original.setEnabled(False)
        self.fs_2.setEnabled(False)
        self.multipaper.setEnabled(False)
     
        
        #enlazar funciones
        self.boton_cargar.clicked.connect(self.cargar_senal)
        self.cargarSenal.clicked.connect(self.load_senal)
        self.filtrar.clicked.connect(self.filtrar_senal)
        self.original.clicked.connect(self.load_original)
        self.boton_adelante.clicked.connect(self.adelante_senal)
        self.boton_atras.clicked.connect(self.atrasar_senal)
        self.boton_aumentar.clicked.connect(self.aumentar_senal)
        self.boton_disminuir.clicked.connect(self.disminuir_senal)    
        self.boton_disminuir.clicked.connect(self.disminuir_senal)     
        self.reload.clicked.connect(self.welch)     
        self.multipaper.clicked.connect(self.calcular_multipaper) 
                
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
            self.reload.setEnabled(True)
    
    def filtrar_senal(self):
        tiempo, freq, power = self.__coordinador.calcularWavelet(0)
        self.__sc.graficar_espectro(tiempo, freq, power)    
        self.original.setEnabled(True)
        self.filtrar.setEnabled(False)
        
    def load_original(self):
        self.original.setEnabled(False)
        self.__coordinador.recibirDatosSenal(self.senalSelected)
        self.__x_min=0
        self.__x_max=16000
        self.__y_min=-58000
        self.__y_max=-55000
        self.__sc.graficar_gatos(self.__coordinador.devolverDatosSenal(self.__x_min,self.__x_max))
        self.filtrar.setEnabled(True)
    def load_senal(self):
        
        cont=1
        if(int(self.senalSeleccionada.text())<=len(self.senales.keys()) and int(self.senalSeleccionada.text())>0):
            for i in self.senales.keys():
                if(int(self.senalSeleccionada.text())==cont): 
                    self.senalSelected=self.senales.get(i)
                cont=cont+1
                    
            print(self.senalSelected.shape)
            print(self.senalSelected)
             
            #self.senalSelected=np.reshape(senalSelected,(sensores,puntos*p),order="F")
            self.__coordinador.recibirDatosSenal(self.senalSelected)
            self.__x_min=0
            self.__x_max=16000
            self.__y_min=-58000
            self.__y_max=-55000
            #graficar utilizando el controlador
            self.__sc.graficar_gatos(self.__coordinador.devolverDatosSenal(self.__x_min,self.__x_max))
            self.boton_adelante.setEnabled(True)
            self.boton_atras.setEnabled(True)
            self.boton_aumentar.setEnabled(True)
            self.boton_disminuir.setEnabled(True)
            self.filtrar.setEnabled(True)
            self.ventana.setEnabled(True)
            self.fs.setEnabled(True)
            self.nperseg.setEnabled(True)
            self.nooverlap.setEnabled(True)
            self.scaling.setEnabled(True)
            self.fs_2.setEnabled(True)
            self.multipaper.setEnabled(True)
        else:
            print("fuera de rango")
            
    def welch(self):
        diccionario1 = dict()
        diccionario1 = {"1":"hamming","2":"hanning","3":"blackman","4":"flattop","5":"boxcar"}
        diccionario2 = dict()
        diccionario2 = {"1":"density","2":"spectrum"}
        
        if(int(self.ventana.text())>0 and int(self.ventana.text())<6  and int(self.scaling.text())>0 and int(self.scaling.text())<3  ):
            print(self.fs.text())
            print(diccionario1.get(self.ventana.text()))
            print(self.nperseg.text())
            print(self.nooverlap.text())
            print(diccionario2.get(self.scaling.text()))
            
            w ,  Wxx_den  =  signal.welch(self.senalSelected , float(self.fs.text()) ,diccionario1.get(self.ventana.text()), nperseg = float(self.nperseg.text()), noverlap = float(self.nooverlap.text()), scaling=diccionario2.get(self.scaling.text()))
            print(Wxx_den)
            self.__coordinador.recibirDatosSenal(Wxx_den)
            self.__x_min=0
            self.__x_max=2000            
           #graficar utilizando el controlador
            self.__sc2.graficar_gatos(self.__coordinador.devolverDatosSenal(self.__x_min,self.__x_max))
        else:
            print("fuera de rango")    
    def calcular_multipaper(self):
        params = dict(fs = float(self.fs_2.text()), fpass = [0, 50], tapers = [2, 2, 1], trialave = 1)
        data = np.reshape(self.senalSelected,(250,10*5),order='F')
        Pxx, f = mtspectrumc(data, params)
        dataf=np.reshape(Pxx,(1,len(Pxx)))
        self.__coordinador.recibirDatosSenal(dataf)
        self.__sc2.graficar_gatos(self.__coordinador.devolverDatosSenal(self.__x_min,self.__x_max))
       