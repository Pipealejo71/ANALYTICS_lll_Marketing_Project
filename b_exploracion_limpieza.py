
import numpy as np
import pandas as pd
import sqlite3 as sql
import plotly.graph_objs as go ### para gráficos
import plotly.express as px
import a_funciones as fn

#pip install --upgrade nbformat
###pip install  pysqlite3

###### para ejecutar sql y conectarse a bd ###


conn=sql.connect('db_movies') ### crear cuando no existe el nombre de cd  y para conectarse cuando sí existe.
cur=conn.cursor() ###para funciones que ejecutan sql en base de datos

##Verificar tablas que hay en la base de datos
cur.execute("SELECT name FROM sqlite_master where type='table' ")
cur.fetchall()

##### consultar trayendo para pandas ###
ratings=pd.read_sql("select * from ratings", conn)
movies=pd.read_sql("select * from movies", conn)
ratings_final=pd.read_sql("select * from ratings", conn)
movies_final=pd.read_sql("select * from movies", conn)
full_ratings=pd.read_sql('select * from full_ratings',conn)

#### para llevar de pandas a BD
#movies.to_sql("movies2", conn, if_exists='replace')
###conn.close()para cerrar conexión


#####Exploración inicial #####

### Identificar campos de cruce y verificar que estén en mismo formato ####
### verificar duplicados

movies.info()
movies.head()
movies.duplicated().sum() 
#movies[movies.duplicated(subset=['title'], keep=False)]

ratings.info()
ratings.head()
ratings.duplicated().sum()

##### Descripción base de ratings

###calcular la distribución de calificaciones
cr=pd.read_sql(""" select 
                          "rating", 
                          count(*) as conteo 
                          from ratings
                          group by "rating"
                          order by conteo desc""", conn)
###Nombres de columnas con numeros o guiones se deben poner en doble comilla para que se reconozcan


data  = go.Bar( x=cr.rating,y=cr.conteo, text=cr.conteo, textposition="outside")
Layout=go.Layout(title="Count of ratings",xaxis={'title':'Rating'},yaxis={'title':'Count'})
go.Figure(data,Layout)

### los que están en 0 fueron vistos pero no calificados
#### Se conoce como calificación implicita, consume producto pero no da una calificacion


### calcular cada usuario cuátos peliculas calificó
rating_users=pd.read_sql(''' select "userId",
                         count(*) as cnt_rat
                         from ratings
                         group by "userId"
                         order by cnt_rat asc
                         ''',conn )

fig  = px.histogram(rating_users, x= 'cnt_rat', title= 'Hist frecuencia de numero de calificaciones por usario')
fig.show() 


rating_users.describe()
### la mayoria de usarios tiene pocos libros calificados, pero los que más tienen muchos

#### excluir usuarios con menos de 50 libros calificados (para tener calificaion confiable) y los que tienen mas de mil porque pueden ser no razonables

rating_users2=pd.read_sql(''' select "User-Id" as user_id,
                         count(*) as cnt_rat
                         from book_ratings
                         group by "User-Id"
                         having cnt_rat >=50 and cnt_rat <=100
                         order by cnt_rat asc
                         ''',conn )

### ver distribucion despues de filtros,ahora se ve mas razonables
rating_users2.describe()


### graficar distribucion despues de filtrar datos
fig  = px.histogram(rating_users2, x= 'cnt_rat', title= 'Hist frecuencia de numero de calificaciones por usario')
fig.show() 


#### verificar cuantas calificaciones tiene cada pelicula
rating_movies=pd.read_sql(''' select movieId ,
                         count(*) as cnt_rat
                         from ratings
                         group by "movieId"
                         order by cnt_rat desc
                         ''',conn )

### analizar distribucion de calificaciones por libro
rating_movies.describe()

### graficar distribucion

fig  = px.histogram(rating_movies, x= 'cnt_rat', title= 'Hist frecuencia de numero de calificaciones para cada pelicula')
fig  
####Excluir peliculas que no tengan más de 10 calificaciones 
rating_movies2=pd.read_sql(''' select movieId ,
                         count(*) as cnt_rat
                         from ratings
                         group by "movieId"
                         having cnt_rat>=10
                         order by cnt_rat desc
                         ''',conn )

rating_movies2.describe()
fig  = px.histogram(rating_movies2, x= 'cnt_rat', title= 'Hist frecuencia de numero de calificaciones para cada pelicula')
fig

###########
fn.ejecutar_sql('preprocesamientos.sql', cur)

cur.execute("select name from sqlite_master where type='table' ")
cur.fetchall()


### verficar tamaño de tablas con filtros ####

####movies
pd.read_sql('select count(*) from movies', conn)
pd.read_sql('select count(*) from movies_final', conn)

##ratings
pd.read_sql('select count(*) from ratings', conn)
pd.read_sql('select count(*) from ratings_final', conn)

## 3 tablas cruzadas ###
pd.read_sql('select count(*) from full_ratings', conn)

ratings=pd.read_sql('select * from full_ratings',conn)
ratings.duplicated().sum() ## al cruzar tablas a veces se duplican registros
ratings.info()
ratings.head(10)

### tabla de full ratings se utilizara para modelos #####