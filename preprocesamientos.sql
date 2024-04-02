
----procesamientos---

---crear tabla con usuarios con más de 50 peliculas vistas y menos de 1000

drop table if exists usuarios_sel;

create table usuarios_sel as 

select "userId" as user_id, count(*) as cnt_rat
from ratings
group by "userId"
having cnt_rat >50 and cnt_rat <= 100
order by cnt_rat desc ;



---crear tabla con peliculas que han sido vistas por más de 50 usuarios
drop table if exists movies_sel;



create table movies_sel as select movieId,
                         count(*) as cnt_rat
                         from ratings
                         group by movieId
                         having cnt_rat >50
                         order by cnt_rat desc ;


-------crear tablas filtradas de peliculas y calificaciones ----

drop table if exists ratings_final;

create table ratings_final as
select a."userId"as user_id,
a.movieId as movieId,
a."rating" as rating
from ratings a 
inner join movies_sel b
on a.movieId =b.movieId
inner join usuarios_sel c
on a."userId" =c.user_id;

drop table if exists movies_final;

create table movies_final as
select a.movieId as movieId,
a."title"  as title,
a."genres" as genres
from movies a
inner join movies_sel c
on a.movieId= c.movieId;


---crear tabla completa ----

drop table if exists full_ratings;

create table full_ratings as 
select 
    a.user_id,
    a.movieId,
    a.rating,
    b.title,
    b.genres
from 
    ratings_final a 
inner join 
    movies_final b 
on 
    a.movieId = b.movieId;

--Se crea una columna con el año de la película
ALTER TABLE full_ratings
ADD COLUMN year INTEGER;

UPDATE full_ratings
SET year = CAST(substr(title, instr(title, '(') + 1, 4) AS INTEGER);

