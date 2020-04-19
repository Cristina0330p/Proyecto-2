# Este Modelo lo que hace es intercatuar con las variables usadas 
#para la ejecucion del programa y la interfaz
# comentario
import numpy as np # se usa la libreria de numpy 
class Biosenal(object): # Se crea class Biosenal 
    def __init__(self,data=None):
        if not data==None:
            self.asignarDatos(data)
        else:
            self.__data=np.asarray([]) #se crea un vector para data
            self.__canales=0
            self.__puntos=0
    def asignarDatos(self,data):
        self.__data=data
        self.__canales=data.shape[0]
        self.__puntos=data.shape[1]
    #necesitamos hacer operacioes basicas sobre las senal, ampliarla, disminuirla, trasladarla temporalmente etc
    def devolver_segmento(self,x_min,x_max):
        #prevengo errores logicos
        if x_min>=x_max:
            return None
        #cojo los valores que necesito en la biosenal
        return self.__data[:,x_min:x_max]

    def escalar_senal(self,x_min,x_max,escala):
        copia_datos=self.__data[:,x_min:x_max].copy()
        return copia_datos*escala
