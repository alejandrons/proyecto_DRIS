# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 20:21:45 2024

@author: DAYANA
"""
import pandas as pd  #Bases de datos, carga bases de datos, saca los estadisticos
import numpy as np   #Calculo vectorial y matricial
from itertools import product

bd = pd.read_csv("foliar.csv", sep=";")
mtra = pd.read_csv("muestra_so.csv", sep=";")
p= 0.9 #Percentil
y="Pr"    

#TODO_VALIDAR SI HAY NULOS EN LA COLUMNA ID
#TODO_VALIDAR LA SUBREGION ES SUROESTE  
#TODO_VALIDAR LA OPCION TODOS O LA MITAD DE LAS RELACIONES

# Combinar las bases de datos
bd_t = pd.concat([bd, mtra], ignore_index=True) #Ignore (Sirve para ignorar los indices de los dataframes) une un dataframe con el otro

# Selección de nutrientes móviles
m = bd_t[["N", "P", "K", "Mg", "S"]] #to_numpy hace la matrixxxxx **se elimino numpy

# Generar todas las relaciones posibles entre los nutrientes móviles
r_m = np.kron(m, 1/m) 
#Darle nombre a las columnas ya que no se estaban generando
col_names = [f"{col1}:{col2}" for col1, col2 in product(m.columns.values.tolist(), repeat=2)] 
r_m = pd.DataFrame(r_m, columns=col_names)

# Seleccionar relaciones de interés entre nutrientes móviles
r_mov = r_m[0:m.shape[0]:m.shape[0]][:,1:m.shape[1]:m.shape[1]] # 1.:from 2.:to 3.len length. El : solo fuerza a que vaya por todo el vector
r_m.drop(list(np.linspace(start=0,stop=r_m.shape[0]-1,num=m.shape[0]).astype(int)),axis=0, inplace=True)
r_m.drop(list(np.linspace(start=0,stop=r_m.shape[1]-1,num=m.shape[1]).astype(int)),axis=1, inplace=True)
# Selección de nutrientes no móviles
n = bd_t[["Ca", "Fe", "Mn", "Cu", "Zn", "B"]].to_numpy()

# Relación entre nutrientes no móviles
r_n = np.kron(n, 1/n.T) 

# Selección de relaciones no móviles de interés
r_nom = r_n[::len(n), :][:, ::len(n)]

# Relación entre móviles y no móviles
r_mn = np.kron(m, n) #ESTE PARCERO ENTIENDE QUE MULTIPLICA

# Combinar las relaciones en la base de datos
bd_t_r = pd.concat([bd_t, r_mov, pd.DataFrame(r_nom)], axis=1) #axis: es el eje por el que se va a concatenar (filas (0) o columnas (1))

# Seleccionar las muestras que cumplen 
a = bd[bd[y] >= bd[y].quantile(p)].index  #index obtener indices de filas

# Selecciona de población de alto rendimiento
p_a = bd_t_r.iloc[a]  #iloc es para seleccionar una fila o un subconjunto de filas

# Muestra, es decir, datos adicionales no incluidos en 'bd'
p_mtra = bd_t_r.iloc[len(bd):]

# Unimos la población de alto rendimiento y la muestra
p_a_mtra = pd.concat([p_a, p_mtra], ignore_index=True) #el ignore_index es para que todo quede pegado en un mismo dataframe

# Selección de relaciones en población de alto y bajo rendimiento y muestra
r_a = p_a

# Selección de matriz de relaciones 
r_b = bd_t_r[bd_t_r[y].to_numpy() < np.quantile(bd_t_r[y].to_numpy(), p)].iloc[:, len(bd.columns):]
print(r_b)                            

# Matriz de relaciones en muestra
r_mtra = bd_t_r.iloc[len(bd):]

# Unimos ambas matrices de relaciones (alto rendimiento y muestra)
r_a_mtra = pd.concat([r_a, r_mtra], ignore_index=True)
