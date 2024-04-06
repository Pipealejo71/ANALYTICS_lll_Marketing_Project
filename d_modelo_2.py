
#pip install scikit-surprise
#pip install scikit-surprise==1.1.2
#import surprise

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

#from surprise import Reader, Dataset
#from surprise.model_selection import cross_validate, GridSearchCV
#from surprise import KNNBasic, KNNWithMeans, KNNWithZScore, KNNBaseline
#from surprise.model_selection import train_test_split


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
ratings=pd.read_sql('select * from ratings', conn )

movies=pd.read_sql('select * from movies_final', conn )
movies['year'] = movies['title'].str.extract('\(([^)]*)\)$', expand=False)
movies['year']=movies.year.astype('int')
movies['year'].value_counts()
movies.info()
##### cargar data frame escalado y con dummies ###

movies_dum2= joblib.load('movies_dum.joblib')


#### seleccionar usuario para recomendaciones ####

usuarios_sel=pd.read_sql('select distinct (user_id) as userId from usuarios_sel',conn)

user_id=604 ### para ejemplo manual


def recomendar(user_id=list(usuarios_sel['userId'].value_counts().index)):
    
    ###seleccionar solo los ratings del usuario seleccionado
    ratings=pd.read_sql('select *from ratings where userId=:user',conn, params={'user':user_id,})
    
    ###convertir ratings del usuario a array
    l_movies_r=ratings['movieId'].to_numpy()
    
    ###agregar la columna de isbn y titulo del libro a dummie para filtrar y mostrar nombre
    movies_dum2[['movieId','title']]=movies[['movieId','title']]
    
    ### filtrar libros calificados por el usuario
    movies_r=movies_dum2[movies_dum2['movieId'].isin(l_movies_r)]
    
    ## eliminar columna nombre e isbn
    movies_r=movies_r.drop(columns=['movieId','title'])
    movies_r["indice"]=1 ### para usar group by y que quede en formato pandas tabla de centroide
    ##centroide o perfil del usuario
    centroide=movies_r.groupby("indice").mean()
    
    
    ### filtrar libros no leídos
    movies_nr=movies_dum2[~movies_dum2['movieId'].isin(l_movies_r)]
    ## eliminbar nombre e movieId
    movies_nr=movies_nr.drop(columns=['movieId','title'])
    
    ### entrenar modelo 
    model=neighbors.NearestNeighbors(n_neighbors=11, metric='cosine')
    model.fit(movies_nr)
    dist, idlist = model.kneighbors(centroide)
    
    ids=idlist[0] ### queda en un array anidado, para sacarlo
    recomend_b=movies.loc[ids][['movieId','title']]
    vistos=movies[movies['movieId'].isin(l_movies_r)][['movieId','title']]
    
    return recomend_b


recomendar(52853)


print(interact(recomendar))


