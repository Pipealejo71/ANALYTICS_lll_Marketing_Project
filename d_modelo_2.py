
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
    
    ###agregar la columna de movieId y titulo de la pelicula a dummie para filtrar y mostrar nombre
    movies_dum2[['movieId','title']]=movies[['movieId','title']]
    
    ### filtrar peliculas calificados por el usuario
    movies_r=movies_dum2[movies_dum2['movieId'].isin(l_movies_r)]
    
    ## eliminar columna nombre e movieId
    movies_r=movies_r.drop(columns=['movieId','title'])
    movies_r["indice"]=1 ### para usar group by y que quede en formato pandas tabla de centroide
    ##centroide o perfil del usuario
    centroide=movies_r.groupby("indice").mean()
    
    
    ### filtrar peliculas no vistas
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


recomendar(604)


print(interact(recomendar))


############################################################################
#####4 Sistema de recomendación filtro colaborativo #####
############################################################################

### datos originales en pandas
## knn solo sirve para calificaciones explicitas
ratings=pd.read_sql('select * from ratings_final where rating>0', conn)


####los datos deben ser leidos en un formato espacial para surprise
reader = Reader(rating_scale=(0, 10)) ### la escala de la calificación
###las columnas deben estar en orden estándar: user item rating
data   = Dataset.load_from_df(ratings[['user_id','movieId','rating']], reader)


#####Existen varios modelos 
models=[KNNBasic(),KNNWithMeans(),KNNWithZScore(),KNNBaseline()] 
results = {}

###knnBasiscs: calcula el rating ponderando por distancia con usuario/Items
###KnnWith means: en la ponderación se resta la media del rating, y al final se suma la media general
####KnnwithZscores: estandariza el rating restando media y dividiendo por desviación 
####Knnbaseline: calculan el desvío de cada calificación con respecto al promedio y con base en esos calculan la ponderación


#### for para probar varios modelos ##########
model=models[1]
for model in models:
 
    CV_scores = cross_validate(model, data, measures=["MAE","RMSE"], cv=5, n_jobs=-1)  
    
    result = pd.DataFrame.from_dict(CV_scores).mean(axis=0).\
             rename({'test_mae':'MAE', 'test_rmse': 'RMSE'})
    results[str(model).split("algorithms.")[1].split("object ")[0]] = result


performance_df = pd.DataFrame.from_dict(results).T
performance_df.sort_values(by='RMSE')

###################se escoge el mejor knn withmeans#########################
param_grid = { 'sim_options' : {'name': ['msd','cosine'], \
                                'min_support': [5,2], \
                                'user_based': [False, True]}
             }

## min support es la cantidad de items o usuarios que necesita para calcular recomendación
## name medidas de distancia

### se afina si es basado en usuario o basado en ítem

gridsearchKNNWithMeans = GridSearchCV(KNNWithMeans, param_grid, measures=['rmse'], \
                                      cv=2, n_jobs=-1)
                                    
gridsearchKNNWithMeans.fit(data)


gridsearchKNNWithMeans.best_params["rmse"]
gridsearchKNNWithMeans.best_score["rmse"]
gs_model=gridsearchKNNWithMeans.best_estimator['rmse'] ### mejor estimador de gridsearch


################# Entrenar con todos los datos y Realizar predicciones con el modelo afinado

trainset = data.build_full_trainset() ### esta función convierte todos los datos en entrnamiento, las funciones anteriores dividen  en entrenamiento y evaluación
model=gs_model.fit(trainset) ## se reentrena sobre todos los datos posibles (sin dividir)



predset = trainset.build_anti_testset() ### crea una tabla con todos los usuarios y los libros que no han leido
#### en la columna de rating pone el promedio de todos los rating, en caso de que no pueda calcularlo para un item-usuario
len(predset)

predictions = gs_model.test(predset) ### función muy pesada, hace las predicciones de rating para todos los libros que no hay leido un usuario
### la funcion test recibe un test set constriuido con build_test method, o el que genera crosvalidate

####### la predicción se puede hacer para un libro puntual
model.predict(uid=269397, iid='0446353205',r_ui='') ### uid debía estar en número e isb en comillas

predictions_df = pd.DataFrame(predictions) ### esta tabla se puede llevar a una base donde estarán todas las predicciones
predictions_df.shape
predictions_df.head()
predictions_df['r_ui'].unique() ### promedio de ratings
predictions_df.sort_values(by='est',ascending=False)


##### funcion para recomendar los 10 libros con mejores predicciones y llevar base de datos para consultar resto de información
def recomendaciones(user_id,n_recomend=10):
    
    predictions_userID = predictions_df[predictions_df['uid'] == user_id].\
                    sort_values(by="est", ascending = False).head(n_recomend)

    recomendados = predictions_userID[['iid','est']]
    recomendados.to_sql('reco',conn,if_exists="replace")
    
    recomendados=pd.read_sql('''select a.*, b.title 
                             from reco a left join movies_final b
                             on a.iid=b.isbn ''', conn)

    return(recomendados)


 
recomendaciones(user_id=604,n_recomend=10)