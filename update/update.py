#!/usr/bin/env python

import requests
import pandas as pd
import datetime as dt
import os

def make_timestamp():
    
    return dt.datetime.now(tz=dt.timezone.utc).strftime('%Y-%m-%d')


def dl_departamento(dep):
    
    url = 'https://refrigerio.consumelonuestro.gob.bo/puntosPorDpto/0{}/1/2000'.format(dep)
    response = requests.get(url, timeout=20).json()
    if response.__contains__('lugares') and len(response['lugares']) > 0:
        df = pd.DataFrame(response['lugares'])
        df.insert(0, 'departamento', response['mensaje'].split(':')[-1].strip().lower())
        return df
    else:
        return pd.DataFrame()


def dl_entidad(id_entidad):
    
    url = 'https://refrigerio.consumelonuestro.gob.bo/entidades/{}/productos?buscar=&pag=1&limit=2000'.format(id_entidad)
    response = requests.get(url, timeout=20).json()
    if response.__contains__('productos') and len(response['productos']) > 0:
        df = pd.DataFrame(response['productos'])
        df.insert(0, 'id_entidad', id_entidad)
        return df
    else:
        return pd.DataFrame()

    
def save(df, path, unique_columns, sort_columns):
    if os.path.exists(path):
        df = pd.concat([pd.read_csv(path), df])
        df.drop_duplicates(subset=unique_columns, keep='last', inplace=True)
    df.sort_values(sort_columns).to_csv(path, index=False)


timestamp = make_timestamp()

entidades = pd.concat([dl_departamento(dep) for dep in range(1,10)])
productos = pd.concat([dl_entidad(id_entidad) for id_entidad in entidades.id_entidad.unique()])

entidades = entidades[['departamento', 'id_entidad', 'nombre_entidad', 'id_sucursal', 'nombre_sucursal', 'latitud', 'longitud']]
productos = productos[['id_entidad', 'id', 'nombre']]
for df in [entidades, productos]:
    df.insert(0, 'date', timestamp)

save(entidades, 'data/entidades.csv', ['id_entidad', 'id_sucursal'], ['departamento', 'id_entidad'])
save(productos, 'data/productos.csv', ['id_entidad', 'id'], ['id_entidad', 'id'])

