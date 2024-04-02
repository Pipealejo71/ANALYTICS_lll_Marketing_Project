
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



##### EXPLORACIÓN INICIAL
movies.info()
movies.head()
movies.duplicated().sum() 
#movies[movies.duplicated(subset=['title'], keep=False)]
ratings.info()
ratings.head()
ratings.duplicated().sum()



##### DESCRIPCIÓN DE BASE RATINGS

### calcular distribución de calificaciones
cr=pd.read_sql(""" select 
                          "rating", 
                          count(*) as conteo 
                          from ratings
                          group by "rating"
                          order by conteo desc""", conn)

data  = go.Bar( x=cr.rating,y=cr.conteo, text=cr.conteo, textposition="outside")
Layout=go.Layout(title="Count of ratings",xaxis={'title':'Rating'},yaxis={'title':'Count'})
go.Figure(data,Layout)



### USUARIOS. calcular antidad de peliculas calificadas por usuario
rating_users=pd.read_sql(''' select "userId",
                         count(*) as cnt_rat
                         from ratings
                         group by "userId"
                         order by cnt_rat asc
                         ''',conn )

fig  = px.histogram(rating_users, x= 'cnt_rat', title= 'Hist frecuencia de numero de calificaciones por usario')
fig.show() 

rating_users.describe()
### la mayoria de usarios tiene pocas Peliculas calificadas, pero los que más tienen muchos



#### excluir usuarios con menos de 50 Peliculas calificadas (para tener calificaion confiable) y los que tienen mas de mil porque pueden ser no razonables
rating_users2=pd.read_sql(''' select "userId" as user_id,
                         count(*) as cnt_rat
                         from ratings
                         group by "userId"
                         having cnt_rat >=50 and cnt_rat <=100
                         order by cnt_rat asc
                         ''',conn )

rating_users2.describe()

fig  = px.histogram(rating_users2, x= 'cnt_rat', title= 'Hist frecuencia de numero de calificaciones por usario')
fig.show() 



#### PELICULA. verificar cuantas calificaciones tiene cada pelicula
rating_movies=pd.read_sql(''' select movieId ,
                         count(*) as cnt_rat
                         from ratings
                         group by "movieId"
                         order by cnt_rat desc
                         ''',conn )

rating_movies.describe()

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



#### SQL
fn.ejecutar_sql('preprocesamientos.sql', cur)
## Verificar tablas que hay en la base de datos
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



### tabla de ´full ratings´ se utilizara para modelos.