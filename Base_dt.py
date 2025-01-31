# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 20:19:46 2024

@author: DAYANA
"""

import pandas as pd

foliar = pd.read_csv("foliar.csv", sep=";")
print(foliar.head())


mtra = pd.read_csv("muestra_so.csv", sep=";")
print(mtra.head())  

# Guardar el DataFrame foliar como un archivo pickle para emular el RData
foliar.to_pickle("bdsuro.pkl")

