# -*- coding: utf-8 -*-
"""
Created on Fri Nov  1 16:29:08 2024

@author: DAYANA
"""

import pandas as pd  #Bases de datos, carga bases de datos, saca los estadisticos
import numpy as np   #Calculo vectorial y matricial
import matplotlib.pyplot as plt
from itertools import product
from pathlib import Path    ## Para guardar las imágenes

def DRIS(muestra:str, perfVar:str="Pr", dec:str=".", separador:str=";", subregion:str="suroeste", perc:float=0.9):

    # Carpeta para guardar imágenes
    BASE_DIR = Path(__file__).resolve().parent
    IMAGE_DIR = BASE_DIR / "static/images"
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)

    # Lectura de las base de datos
    bd = pd.read_csv("foliar.csv", sep=separador)
    mtra =  pd.read_csv(muestra, sep=separador)

    p = perc #Percentil
    y = perfVar    

    #TODO_VALIDAR SI HAY NULOS EN LA COLUMNA ID
    #TODO_VALIDAR LA SUBREGION ES SUROESTE  
    #TODO_VALIDAR LA OPCION TODOS O LA MITAD DE LAS RELACIONES

    # Combinar las bases de datos
    bd_t = pd.concat([bd, mtra], ignore_index=True) #Ignore (Sirve para ignorar los indices de los dataframes) une un dataframe con el otro
    m_bd_t = pd.DataFrame(bd_t)

    # Selección de nutrientes móviles
    m = m_bd_t[["N", "P", "K", "Mg", "S"]] #to_numpy hace la matrixxxxx **se elimino numpy

    # Generar todas las relaciones posibles entre los nutrientes móviles
    r_m = pd.DataFrame (np.kron(m, 1/m))

    r_m=r_m.iloc[np.linspace(start=0,stop=r_m.shape[0]-1,num=m.shape[0]).astype(int),0:r_m.shape[1]]
    r_m.drop((np.linspace(start=0,stop=r_m.shape[1]-1,num=m.shape[1]).astype(int)),axis=1, inplace=True)

    #Darle nombre a las columnas ya que no se estaban generando
    col_names = [f"{col1}:{col2}" for col1, col2 in product(m.columns.values.tolist(), repeat=2)]   #Crear los nombres para las relaciones
    col_names = [s for s in col_names if s.split(":")[0] != s.split(":")[1]]     #Borrar las relaciones repetidas
    r_m.columns = col_names         #Cambiar los nombres de las columnas por las relaciones
    r_m.reset_index(drop=True, inplace=True)

    # Selección de nutrientes no móviles
    n = bd_t[["Ca", "Fe", "Mn", "Cu", "Zn", "B"]]

    # Relación entre nutrientes no móviles
    r_n = pd.DataFrame(np.kron(n, 1/n))
    
    r_n=r_n.iloc[np.linspace(start=0,stop=r_n.shape[0]-1,num=n.shape[0]).astype(int),0:r_n.shape[1]]
    r_n.drop((np.linspace(start=0,stop=r_n.shape[1]-1,num=n.shape[1]).astype(int)),axis=1, inplace=True)

    col_names = [f"{col1}:{col2}" for col1, col2 in product(n.columns.values.tolist(), repeat=2)] 
    col_names = [s for s in col_names if s.split(":")[0] != s.split(":")[1]]     #Borrar las relaciones repetidas
    r_n.columns = col_names         #Cambiar los nombres de las columnas por las relaciones
    r_n.reset_index(drop=True, inplace=True)

    # Relación entre móviles y no móviles
    r_mn = pd.DataFrame(np.kron(m, n)) #ESTE PARCERO ENTIENDE QUE MULTIPLICA
    r_mn = r_mn.iloc[np.linspace(start=0,stop=r_mn.shape[0]-1,num=m.shape[0]).astype(int),0:r_mn.shape[1]]

    col_names = [f"{col1}:{col2}" for col1, col2 in product(m.columns.values.tolist(), n.columns.values.tolist())] 
    col_names = [s for s in col_names if s.split(":")[0] != s.split(":")[1]]     #Borrar las relaciones repetidas
    r_mn.columns = col_names

    # Combinar las relaciones en la base de datos
    bd_t_r = pd.concat([bd_t, r_m,r_n], axis=1) #axis: es el eje por el que se va a concatenar (filas (0) o columnas (1))

    # Seleccionar las muestras que cumplen 
    a = bd[bd[y] >= bd[y].quantile(p)].index  #index obtener indices de filas

    # Selecciona de población de alto rendimiento
    p_a = bd_t_r.iloc[a]  #iloc es para seleccionar una fila o un subconjunto de filas

    # Muestra, es decir, datos adicionales no incluidos en 'bd'
    p_mtra = bd_t_r.drop(range(len(bd)),axis=0)

    # Unimos la población de alto rendimiento y la muestra
    p_a_mtra = pd.concat([p_a, p_mtra], ignore_index=True) #el ignore_index es para que todo quede pegado en un mismo dataframe

    # Selección de relaciones en población de alto y bajo rendimiento y muestra
    r_a = p_a

    # Selección de matriz de relaciones 
    r_b = bd_t_r[bd_t_r[y].to_numpy() < np.quantile(bd_t_r[y].to_numpy(), p)].iloc[:, len(bd.columns):]
                                
    # Matriz de relaciones en muestra
    r_mtra = p_mtra

    # Union de las matrices de relaciones (alto rendimiento y muestra)
    r_a_mtra = pd.concat([r_a, r_mtra], ignore_index=True)

    #AQUI VA EL PRIMER IF SOBRE LAS RELACIONES A ESCOGER
    # Estadisticos para DRIS con todas relaciones
    # Caracteristicas promedio y sd en poblacion de refencia
    prom_nut_a = p_a.iloc[:, :len(bd.columns)].mean()  # Promedio
    sd_nut_a = p_a.iloc[:, 1:len(bd.columns)].std()    # Desviación estándar
    prom_a = r_a.mean()
    cv_a = r_a.std() / abs(prom_a)

    # Matriz de promedios de relaciones de referencia
    m_prom_a = pd.DataFrame(np.tile(prom_a.values, (len(r_a_mtra), 1)), columns=r_a_mtra.columns)
    m_cv_a = pd.DataFrame(np.tile(cv_a.values, (len(r_a_mtra), 1)), columns=r_a_mtra.columns)
    #
    #
    #TODO_VALIDAR LOS ESTADISTICOS DE LA POBLACIÓN ESTANDAR

    #SEGUIR CON TODAS LAS RELACIONES
    #Funciones en la poblacion de referencia y muestra
    #f1(r.mtra/prom.a-1)*1/cv.a), cuando (A/B>=a/b)
    f_a_mtra1 = (1 * (r_a_mtra >= m_prom_a)) * ((r_a_mtra / m_prom_a) - 1) * (1 / m_cv_a)
    f_a_mtra1.fillna(0, inplace=True) # Reemplazamos valores NULOS por 0
    #f2(1-r.mtra/prom.a)*1/cv.a), cuando (A/B<a/b)
    f_a_mtra2 = (1 * (r_a_mtra < m_prom_a)) * ((1 - m_prom_a / r_a_mtra) * (1 / m_cv_a))
    f_a_mtra2.fillna(0, inplace=True)
    # Suma de las funciones
    f_a_mtra = f_a_mtra1 + f_a_mtra2 #donde ya no hay valores nulos

    ###Inicializacion de matriz almacenamiento indices DRIS en referencia y muestra###
    macro = ["N", "P", "K", "Ca", "Mg", "S"]
    micro = ["Fe", "Mn", "Cu", "Zn", "B"]
    ma_mi = macro + micro
    ID_a_mtra = p_a_mtra[ma_mi] * 0  #p_a_mtra las columnas de interés
    # Crear la lista concatenando los nombres de las columnas con :
    ta1 = [f"{col}" for col in ID_a_mtra.columns]

    #Generacion de los indices en poblacion referencia y muestra 

    for i in range(ID_a_mtra.shape[0]): #recorre la matriz (fila por fila)  mejor for si es finito
        for j in range(ID_a_mtra.shape[1]): #(columna por columna)
            #TODO Corregir: Setting an item of incompatible dtype is deprecated and will raise an error in a future version of pandas.
            
            matching_cols = [col for col in f_a_mtra.columns if ta1[j] in col.split(":")[0]] #igual que el grep
            matching_cols.pop(0) #pop borra el primer elemento que no sirve
            col_sum = f_a_mtra.iloc[i][matching_cols].sum()
            col_count = len(matching_cols)
            ID_a_mtra.iloc[i, j] = float(col_sum) / col_count if col_count > 0 else 0.0

    ID = pd.concat([prom_nut_a[ma_mi].to_frame().T,sd_nut_a[ma_mi].to_frame().T,ID_a_mtra[:p_a.shape[0]].mean().to_frame().T,ID_a_mtra[:p_a.shape[0]].std().to_frame().T,ID_a_mtra[p_a.shape[0]:]])
    ID[2:]=0
    ID = ID.round(2)
    ID[ID==0] = np.nan
    index_list = ["Prom.nutrientes","Sd.nutrientes","ID.norma","Sd.ID.norma"]
    for i in mtra["Id"]:
        index_list += ["id_muestra_"+str(i)]
    ID.index = index_list

    img_dir = []
    #GRAFICOS
    import matplotlib.pyplot as plt
    for i in range(4, ID.shape[0]):  # Empieza desde el quinto elemento
        sample_name = ID.index[i]
        file_name = f"{sample_name}.png"

        # Crear figura
        fig, axes = plt.subplots(3, 1, figsize=(7, 14))
        plt.subplots_adjust(hspace=0.4)  # Espaciado entre subgráficos

        # **Gráfico 1: RANGOS - Macronutrientes**
        ax = axes[0]
        y_macro_prom = ID.loc["Prom.nutrientes", macro]
        y_macro_sd = ID.loc["Sd.nutrientes", macro]
        y_macro_sample = mtra.loc[i-4, macro]
        x_macro = np.arange(1, len(macro) + 1)

        ax.errorbar(x_macro, y_macro_prom, yerr=y_macro_sd, fmt='o', color='green', label="Norma", capsize=5)
        ax.scatter(x_macro + 0.1, y_macro_sample, color='red', label="Muestra")
        ax.set_xticks(x_macro)
        ax.set_xticklabels(macro)
        ax.set_ylim(0, max(y_macro_prom + y_macro_sd) * 1.2)
        ax.set_xlabel("Nutrientes")
        ax.set_ylabel("Contenido (%)")
        ax.set_title(sample_name)
        ax.legend()

        # **Gráfico 2: RANGOS - Micronutrientes**
        ax = axes[1]
        y_micro_prom = ID.loc["Prom.nutrientes", micro]
        y_micro_sd = ID.loc["Sd.nutrientes", micro]
        y_micro_sample = mtra.loc[i-4, micro]
        x_micro = np.arange(1, len(micro) + 1)

        ax.errorbar(x_micro, y_micro_prom, yerr=y_micro_sd, fmt='o', color='green', label="Norma", capsize=5)
        ax.scatter(x_micro + 0.1, y_micro_sample, color='red', label="Muestra")
        ax.set_xticks(x_micro)
        ax.set_xticklabels(micro)
        ax.set_ylim(0, max(y_micro_prom + y_micro_sd) * 1.2)
        ax.set_xlabel("Nutrientes")
        ax.set_ylabel("Contenido (mg/kg)")
        ax.legend()

        # **Gráfico 3: Índices DRIS**
        ax = axes[2]
        x = np.arange(1, ID.shape[1] + 1)
        y_norma = ID.loc["ID.norma"]
        y_sd_norma = ID.loc["Sd.ID.norma"]
        y_sample = ID_a_mtra.loc[i]

        ax.errorbar(x, np.zeros((ID.shape[1],)), yerr=np.zeros((ID.shape[1],)), fmt='o', color='green', label="ID.norma", capsize=5)
        ax.scatter(x, y_sample, color='red', label="ID.muestra")
        ax.axhline(0, linestyle="--", color="black", linewidth=1)
        ax.set_xticks(x)
        ax.set_xticklabels(ID.columns, rotation=90)
        ax.set_xlabel("Nutrientes")
        ax.set_ylabel("Índice DRIS")
        ax.legend()

        # Guardar figura como imagen
        img_dir += [f"127.0.0.1:8000/static/images/{file_name}"]
        image_path = IMAGE_DIR / file_name
        plt.savefig(image_path)
        plt.close(fig)

    return img_dir
