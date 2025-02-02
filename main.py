from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from correciones import DRIS
from pathlib import Path

app = FastAPI()

app.title= "DRIS: Sistema integral de diagnostico y recomendacion nutricional"
app.version = "1.0.0"

app.description = """La evaluacion del estado nutricional de una muestra requiere 
preparar un archivo csv o txt. Debe contener las siguientes columnas 
(Id, Pr, N,	P, K, Ca, Mg, S, Fe, Mn, Cu, Zn, B). Cada fila corresponde 
con los registros de cada variable asi: Id:numero de la muestra, 
Pr:Peso de racimo o rendimiento (kg), y las demas a los nutrientes reportados en 
los resultados de los analisis foliares para N,P,K,Ca,Mg y S en %, los demas en mg/kg.\n\n
*Nota: Si para un registro no conoce el valor de una o mas variables, ingreselo(s) como NA."""

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)

# Montar la carpeta estática para servir imágenes
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get('/', tags=['Realizado por: Dayana Villa y Dario Castañeda'])
def root():
    pass


@app.get('/home', tags=['Plátano'])
def principal(mtra:str, y:str="Pr", dec:str=".", sep:str=";", subregion:str="suroeste", p:float=0.9):
    # mtra: Ingrese muestra (archivo .csv o .txt)
    # dec: Caracter separador fraccion decimal valores muestra: ("." "," )
    # sep: Caracter separador de campos entre registros muestra: (","   ";"  "t" )
    # y: Variable de rendimiento o produccion
    # subregion: subregión (suroeste)
    # p: Percentil de seleccion poblacion referencia (p=0.8)
    s = DRIS(mtra, y, dec, sep, subregion, p)
    if (len(s) > 0):     
        return JSONResponse(content={"image_url":s},status_code=200)
    else:
        return HTMLResponse("Algo ha fallado", status_code=418)
    