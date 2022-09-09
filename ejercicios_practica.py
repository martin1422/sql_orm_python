#!/usr/bin/env python
'''
SQL Introducción [Python]
Ejercicios de práctica
---------------------------
Autor: Inove Coding School
Version: 1.1

Descripcion:
Programa creado para poner a prueba los conocimientos
adquiridos durante la clase
'''

__author__ = "Inove Coding School"
__email__ = "alumnos@inove.com.ar"
__version__ = "1.1"

import sqlite3
import os
import csv

import sqlalchemy
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Crear el motor (engine) de la base de datos
engine = sqlalchemy.create_engine("sqlite:///secundaria.db")
base = declarative_base()

from config import config

# Obtener la path de ejecución actual del script
script_path = os.path.dirname(os.path.realpath(__file__))

# Obtener los parámetros del archivo de configuración
config_path_name = os.path.join(script_path, 'config.ini')
data_secundaria = config('data_secundaria', config_path_name)

class Tutor(base):
    __tablename__ = "tutor"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    
    def __repr__(self):
        return f"Tutor: {self.name}"


class Estudiante(base):
    __tablename__ = "estudiante"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)
    grade = Column(Integer)
    tutor_id = Column(Integer, ForeignKey("tutor.id"))

    tutor = relationship("Tutor")

    def __repr__(self):
        return f"Estudiante: {self.name}, edad {self.age}, grado {self.grade}, tutor {self.tutor.name}"


def create_schema():
    
    # Borrar todos las tablas existentes en la base de datos
    # Esta linea puede comentarse sino se eliminar los datos
    base.metadata.drop_all(engine)

    # Crear las tablas
    base.metadata.create_all(engine)

def insert_tutor(name):
    # Crear la session
    Session = sessionmaker(bind=engine)
    session = Session()

    tutor = Tutor(name=name)

    session.add(tutor)
    session.commit()
    print(tutor)


def insert_estudiante(name, age, grade, tutor):
    # Crear la session
    Session = sessionmaker(bind=engine)
    session = Session()

 
    tutor = session.query(Tutor).filter(Tutor.name == tutor).first()
    
    if tutor is None:
        # Podrá ver en este ejemplo que sucederá este error con la persona
        # de nacionalidad Inglaterra ya que no está definida en el archivo
        # de nacinoalidades
        print(f"Error la crear la persona {name}, no existe la nacionalidad {tutor}")
        return

    # Crear la persona
    estudiante = Estudiante(name=name, age=age, grade=grade, tutor=tutor)
    estudiante.tutor = tutor

    # Agregar la persona a la DB
    session.add(estudiante)
    session.commit()
    print(estudiante)

def fill():
    print('Completemos esta tablita!')
    # Llenar la tabla de la secundaria con al munos 2 tutores
    # Cada tutor tiene los campos:
    # id --> este campo es auto incremental por lo que no deberá completarlo
    # name --> El nombre del tutor (puede ser solo nombre sin apellido)

    # Llenar la tabla de la secundaria con al menos 5 estudiantes
    # Cada estudiante tiene los posibles campos:
    # id --> este campo es auto incremental por lo que no deberá completarlo
    # name --> El nombre del estudiante (puede ser solo nombre sin apellido)
    # age --> cuantos años tiene el estudiante
    # grade --> en que año de la secundaria se encuentra (1-6)
    # tutor --> el tutor de ese estudiante (el objeto creado antes)

    # No olvidarse que antes de poder crear un estudiante debe haberse
    # primero creado el tutor.
    with open(data_secundaria['tutor']) as fi:
        data = list(csv.DictReader(fi))

        for row in data:
            insert_tutor(row['tutor'])

    # Insertar el archivo CSV de personas
    # Insertar todas las filas juntas
    with open(data_secundaria['estudiante']) as fi:
        data = list(csv.DictReader(fi))

        for row in data:
            insert_estudiante(row['name'], int(row['age']), int(row['grade']), row['tutor'])

def fetch(limit=0):
    print('Comprovemos su contenido, ¿qué hay en la tabla?')
    # Crear una query para imprimir en pantalla
    # todos los objetos creaods de la tabla estudiante.
    # Imprimir en pantalla cada objeto que traiga la query
    # Realizar un bucle para imprimir de una fila a la vez
    # Crear la session
    Session = sessionmaker(bind=engine)
    session = Session()

    # Buscar todas las personas
    query = session.query(Estudiante).order_by(Estudiante.age.desc())

    # Si está definido el limite aplicarlo
    if limit > 0:
        query = query.limit(limit)

    # Leer una persona a la vez e imprimir en pantalla
    for estudiante in query:
        print(estudiante)


def search_by_tutor(tutor):
    print('Operación búsqueda!')
    # Esta función recibe como parámetro el nombre de un posible tutor.
    # Crear una query para imprimir en pantalla
    # aquellos estudiantes que tengan asignado dicho tutor.

    # Para poder realizar esta query debe usar join, ya que
    # deberá crear la query para la tabla estudiante pero
    # buscar por la propiedad de tutor.name
    Session = sessionmaker(bind=engine)
    session = Session()

    result = session.query(Estudiante).join(Estudiante.tutor).filter(Tutor.name == tutor).count()
    print('Estudiantes a cargo del tutor: ',tutor, ' encontrados son: ', result)



def modify(id, name):
    print('Modificando la tabla')
    # Deberá actualizar el tutor de un estudiante, cambiarlo para eso debe
    # 1) buscar con una query el tutor por "tutor.name" usando name
    # pasado como parámetro y obtener el objeto del tutor
    # 2) buscar con una query el estudiante por "estudiante.id" usando
    # el id pasado como parámetro
    # 3) actualizar el objeto de tutor del estudiante con el obtenido
    # en el punto 1 y actualizar la base de datos

    # TIP: En clase se hizo lo mismo para las nacionalidades con
    # en la función update_persona_nationality
   # Crear la session
    Session = sessionmaker(bind=engine)
    session = Session()

  
    # Buscar la persona que se desea actualizar
    query = session.query(Tutor).filter(Tutor.id == id).update({Tutor.name: name})
    query = session.query(Tutor).filter(Tutor.id == id).first()
    tutor = query

    # Actualizar la persona con nombre "name"
    tutor.name = name

    # Aunque la persona ya existe, como el id coincide
    # se actualiza sin generar una nueva entrada en la DB
    session.add(tutor)
    session.commit()

    print('tutor actualizada', name)


def count_grade(grade):
    print('Estudiante por grado')
    # Utilizar la sentencia COUNT para contar cuantos estudiante
    # se encuentran cursando el grado "grade" pasado como parámetro
    # Imprimir en pantalla el resultado

    # TIP: En clase se hizo lo mismo para las nacionalidades con
    # en la función count_persona
    Session = sessionmaker(bind=engine)
    session = Session()

    result = session.query(Estudiante).filter(Estudiante.grade == grade).count()
    print('Estudiantes del grado: ', grade, 'encontrados:', result)


if __name__ == '__main__':
    print("Bienvenidos a otra clase de Inove con Python")
    create_schema()   # create and reset database (DB)
    fill()
    fetch()

    tutor = 'Martin'
    search_by_tutor(tutor)

    tutor = 'Tony'
    search_by_tutor(tutor)

    nuevo_tutor = 'Luciano'
    id = 4
    modify(id, nuevo_tutor)

    grade = 1
    count_grade(grade)
