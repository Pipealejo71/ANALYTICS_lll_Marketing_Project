import numpy as np
import pandas as pd
import sqlite3 as sql
from sklearn.preprocessing import MinMaxScaler
from ipywidgets import interact ## para análisis interactivo
from sklearn import neighbors ### basado en contenido un solo producto consumido
import joblib



#### conectar_base_de_Datos
conn=sql.connect('db_movies')
cur=conn.cursor()
#### ver tablas disponibles en base de datos ###
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
cur.fetchall()



################## 1. sistemas basados en popularidad ###############
#####################################################################

#### mejores calificadas, excluyendo las que no tienen calificacion
pd.read_sql("""select title, 
            avg(rating) as avg_rat,
            count(*) as read_num
            from full_ratings
            where rating<>0
            group by title
            order by avg_rat desc
            limit 10
            """, conn)

#### con mayor cantidad de vistas y promedio de quienes calficaron
pd.read_sql("""select title, 
            avg(iif(rating = 0, Null, rating)) as avg_rat,
            count(*) as view_num
            from full_ratings
            group by title
            order by view_num desc
            """, conn)



######## 2.1 Sistema de recomendación basado en contenido un solo producto - Manual ########
############################################################################################

movies=pd.read_sql('select * from movies_final', conn )
movies.info()

##Extraer año de la pelicula
movies['year'] = movies['title'].str.extract('\(([^)]*)\)$', expand=False)
movies['year']=movies.year.astype('int')
movies['year'].value_counts()
movies.info()


##### escalar para que año esté en el mismo rango ###
sc=MinMaxScaler()
movies[["year_sc"]]=sc.fit_transform(movies[['year']])

#### eliminar filas que no se van a utilizar
movies_2=movies.drop(columns=['movieId','title','year'])
movies_2.info()

#### convertir a dummies
# Divide la columna de géneros en varias columnas
genres_split = movies_2['genres'].str.split('|', expand=True)

# Convierte estas columnas en columnas dummies
genres_dummies = pd.get_dummies(genres_split.stack()).groupby(level=0).sum()

# Une las columnas dummies al DataFrame original
movies_dum = pd.concat([movies_2, genres_dummies], axis=1)
movies_dum=movies_dum.drop(columns=['genres'])
movies_dum.shape

joblib.dump(movies_dum,"movies_dum.joblib") ### para utilizar en segundos modelos



#### peliculas recomendadas ejemplo para una pelicula
m='Reservoir Dogs (1992)'
ind_m=movies[movies['title']==m].index.values.astype(int)[0]
similar_m=movies_dum.corrwith(movies_dum.iloc[ind_m,:],axis=1)
similar_m=similar_m.sort_values(ascending=False)
top_similar_m=similar_m.to_frame(name="correlación").iloc[0:11,] ### el 11 es número de peliculas recomendadas
top_similar_m['title']=movies["title"] ### agregaro los nombres (como tiene mismo indice no se debe cruzar)
top_similar_m    

#### Peliculas recomendadas para una pelicula
def recomendacion(peli = list(movies['title'])):
     
    ind_peli=movies[movies['title']==peli].index.values.astype(int)[0]   #### obtener indice de pelicula seleccionada de lista
    similar_m = movies_dum.corrwith(movies_dum.iloc[ind_peli,:],axis=1) ## correlación entre pelicula seleccionada y todas las otras
    similar_m = similar_m.sort_values(ascending=False) #### ordenar correlaciones
    top_similar_m=similar_m.to_frame(name="correlación").iloc[0:11,] ### el 11 es número de peliculas recomendadas
    top_similar_m['title']=movies["title"] ### agregaro los nombres (como tiene mismo indice no se debe cruzar)
    
    return top_similar_m

print(interact(recomendacion))



######### 2.2 Sistema de recomendación basado en contenido KNN un solo producto visto ########
##############################################################################################

## el coseno de un angulo entre dos vectores es 1 cuando son perpendiculares y 0 cuando son paralelos(indicando que son muy similar324e-06	3.336112e-01	3.336665e-01	3.336665e-es)
model = neighbors.NearestNeighbors(n_neighbors=11, metric='cosine')
model.fit(movies_dum)
dist, idlist = model.kneighbors(movies_dum)

distancias=pd.DataFrame(dist) ## devuelve un ranking de la distancias más cercanas para cada fila(pelicula)
id_list=pd.DataFrame(idlist) ## para saber esas distancias a que item corresponde



####ejemplo para una pelicula
movies_list_name = []
movies_name='Reservoir Dogs (1992)'
movies_id = movies[movies['title'] == movies_name].index ### extraer el indice de la pelicula

for newid in idlist[movies_id]:
        movies_list_name.append(movies.loc[newid].title) ### agrega el nombre de cada una de los id recomendados

movies_list_name

#### Peliculas recomendadas para una pelicula
def MovieRecommender(movies_name = list(movies['title'].value_counts().index)):
    movies_list_name = []
    movies_id = movies[movies['title'] == movies_name].index
    movies_id = movies_id[0]
    for newid in idlist[movies_id]:
        movies_list_name.append(movies.loc[newid].title)
    return movies_list_name

print(interact(MovieRecommender))