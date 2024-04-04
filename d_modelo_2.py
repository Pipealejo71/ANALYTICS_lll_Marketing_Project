
#pip install scikit-surprise
#pip install scikit-surprise==1.1.2
import surprise

import numpy as np
import pandas as pd
import sqlite3 as sql
from sklearn.preprocessing import MinMaxScaler
from ipywidgets import interact ## para análisis interactivo
from sklearn import neighbors ### basado en contenido un solo producto consumido
import joblib
####Paquete para sistemas de recomendación surprise
###Puede generar problemas en instalación local de pyhton. Genera error instalando con pip
#### probar que les funcione para la próxima clase 

from surprise import Reader, Dataset
from surprise.model_selection import cross_validate, GridSearchCV
from surprise import KNNBasic, KNNWithMeans, KNNWithZScore, KNNBaseline
from surprise.model_selection import train_test_split


#### conectar_base_de_Datos
conn=sql.connect('db_movies')
cur=conn.cursor()
#### ver tablas disponibles en base de datos ###
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
cur.fetchall()



#######################################################################
#### 3 Sistema de recomendación basado en contenido KNN #################
#### Con base en todo lo visto por el usuario #######################
#######################################################################

movies=pd.read_sql('select * from db_movies', conn )
movies['year']=movies.year.astype('int')

##### cargar data frame escalado y con dummies ###

movies_dum2= joblib.load('salidas\\movies_dum2.joblib')


#### seleccionar usuario para recomendaciones ####

usuarios=pd.read_sql('select distinct (user_id) as user_id from ratings',conn)

user_id=31226 ### para ejemplo manual


def recomendar(user_id=list(usuarios['user_id'].value_counts().index)):
    
    ###seleccionar solo los ratings del usuario seleccionado
    ratings=pd.read_sql('select *from ratings where user_id=:user',conn, params={'user':user_id,})
    
    ###convertir ratings del usuario a array
    l_books_r=ratings['isbn'].to_numpy()
    
    ###agregar la columna de isbn y titulo del libro a dummie para filtrar y mostrar nombre
    books_dum2[['isbn','book_title']]=books[['isbn','book_title']]
    
    ### filtrar libros calificados por el usuario
    books_r=books_dum2[books_dum2['isbn'].isin(l_books_r)]
    
    ## eliminar columna nombre e isbn
    books_r=books_r.drop(columns=['isbn','book_title'])
    books_r["indice"]=1 ### para usar group by y que quede en formato pandas tabla de centroide
    ##centroide o perfil del usuario
    centroide=books_r.groupby("indice").mean()
    
    
    ### filtrar libros no leídos
    books_nr=books_dum2[~books_dum2['isbn'].isin(l_books_r)]
    ## eliminbar nombre e isbn
    books_nr=books_nr.drop(columns=['isbn','book_title'])
    
    ### entrenar modelo 
    model=neighbors.NearestNeighbors(n_neighbors=11, metric='cosine')
    model.fit(books_nr)
    dist, idlist = model.kneighbors(centroide)
    
    ids=idlist[0] ### queda en un array anidado, para sacarlo
    recomend_b=books.loc[ids][['book_title','isbn']]
    leidos=books[books['isbn'].isin(l_books_r)][['book_title','isbn']]
    
    return recomend_b


recomendar(52853)


print(interact(recomendar))


