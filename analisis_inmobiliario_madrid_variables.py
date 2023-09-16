"""CASO 1 BA: ANALISIS MERCADO INMOBILIARIO PARA ALQUILER TURÍSTICO
Somos una empresa inmobiliaria que hace inversión en grandes ciudades para alquiler turístico
La dirección ha tomado la decisión de invertir en Madrid, y nos ha encargado analizar los datos que el líder del sector AirBnb hace públicos para intentar encontrar los tipos de inmuebles que tienen mayor potencial comercial para alquier turístico.

Como entregable principal esperan la tipología (o tipologías) de inmuebles que el equipo de valoraciones debe buscar entre las oportunidades existentes en la ciudad y los principales barrios o zonas geográficas en las que focalizarse.

Aunque este caso concreto esté centrado en el alquiler turístico el mismo tipo de aproximación se puede usar en casos que tengan un alto componente de "ubicación":

- apertura y cierre de tiendas
- reducción de capacidad instalada
- expansión de franquicias
etc.

Siguiendo la metodología de Discovery:

OBJETIVO

Localizar el perfil (o perfiles) de inmuebles que maximizan el potencial comercial en el mercado del alquiler turístico y las principales zonas donde buscarlos.

PALANCAS

Tras hablar con el equipo de valoraciones nos dicen que las palancas que tienen más impacto en la rentabilidad de este tipo de inversiones son:

- Precio alquiler: cuanto más se pueda cobrar por noche mayor es la rentabilidad
- Ocupación: en general cuantos más días al año se pueda alquilar un inmueble mayor es su rentabilidad
- Precio inmueble: cuanto más barato se pueda adquirir la propiedad mayor es la rentabilidad

KPIs

En este ejemplo los Kpis son bastante directos:

- Mediremos la ocupación como el número de días anuales que el inmueble se pueda alquilar
- Mediremos el precio del alquiler como el precio por noche en euros según Airbnb
- Mediremos el precio de un inmueble como la multiplicación entre el número de metros cuadrados y el precio medio del m2 en su zona, y aplicaremos un 25% de descuento sobre el precio oficial por la fuerza de negociciación de nuestro equipo de compras.

ENTIDADES Y DATOS

Las entidades relevantes para nuestro objetivo y de las que podemos disponer de datos son:

- Inmuebles
- Propietarios
- Distritos

Los datos que vamos a utilizar los puedes encontrar aquí: http://insideairbnb.com/

PREGUNTAS SEMILLA

Sobre el precio del alquiler:

- ¿Cual es el precio medio? ¿y el rango de precios?¿Y por distritos?¿Y por barrios?
- ¿Cual es el ranking de distritos y barrios por precio medio de alquiler?
- ¿Qué factores (a parte de la localización determinan el precio del alquiler?
- ¿Cual es la relación entre el tamaño del inmueble y el precio por el que se puede alquilar?
- ¿Cómo influye la competencia (num inmuebles disponibles por barrio) sobre el precio del alquiler?
- ¿Cómo varían los precios por tipo de alquiler (todo el piso, habitación privada, habitación compartida)?

Sobre la ocupación:

- ¿Cual es la ocupación media? ¿Y por distritos?¿Y por barrios?
- ¿Cómo de probable es cada nivel de ocupación en cada distrito?
- ¿Cual es el ranking de distritos y barrios por ocupación?
- ¿Qué factores (a parte de la localización determinan la ocupación?
- ¿Cual es la relación entre el tamaño del inmueble y su grado de ocupación?
- ¿Cómo influye la competencia (num inmuebles disponibles por barrio) sobre la ocupación?

Sobre el precio de compra:

- ¿Cual es el ranking de precio por m2 por distrito?
- ¿Cual es el ranking de precio del inmueble (m2 * tamaño medio) por distrito?
- ¿Cual es la relación entre el precio del inmueble y el precio del alquiler por distrito?
- ¿Cual es la relación entre el precio del inmueble y la ocupación por distrito?"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sqlalchemy as sa

# %matplotlib inline # para que los gráficos aparezcan en Jupyter Notebook
# %config IPCompleter.greedy=True # cuando pulsamos la tecla tabuladora que autocomplete

# CARGA DE DATOS

con = sa.create_engine('sqlite:///DatoscASO1/airbnb.db')

df = pd.read_sql('df', con = con)

print(df.head())

# PREPARACIÓN DE VARIABLES
# CREACIÓN DE KPIs DE PALANCAS

# Primero vamos a crear las variables de análisis, es decir las que habíamos identificado como los KPIs que usaremos en las palancas que influyen sobre el negocio.

# Habíamos dicho que eran 3:

# - precio por noche: esta ya la tenemos directamente en la variable price, pero vamos a revisarla para ver que la entendemos bien
# - ocupación: tenemos availability_365 pero hay que transformarla
# - precio del inmueble: esta tendremos que crearla con variables externas así que la dejamos para después

# Empezamos por el precio

# La documentación no aclara si el precio es por todo el inmueble, o si en el caso de que se alquile una habitación es por habitación.
# Es un dato clave para poder hacer la valoración de los potenciales ingresos de un inmueble. Vamos a intentar entenderlo analizando el precio medio por tipo de alquiler.

# Es importante filtrar por solo un distrito para no incluir el efecto "zona". Así que primero elegimos un distrito que tenga muchos datos.

print(df.distrito.value_counts())
print(df.loc[df.distrito == 'Centro',:].groupby('room_type').price.mean())

# CONCLUSIÓN:

# - alquilar el apartamento tiene un precio medio de 148€
# - alquilar una habitación tiene un precio medio de 60€ o 67€ según sea compartida o privada

# Por tanto para calcular los "ingresos" de un inmueble sí deberemos multiplicar el precio por el número de habitaciones cuando sea de los tipos Private room o Shared room

# Ahora bien, multiplicar el precio por el total de habitaciones puede sesgar artificialmente al alza la capacidad de generar ingresos de un inmueble.
# Ya que si se alquila por habitaciones no es probable que siempre esté al 100% Por tanto deberíamos ponderarlo por el porcentaje medio de habitaciones alquiladas.

# No tenemos ese dato, pero supongamos que hemos hablado con el responsable de negocio y nos ha dicho que es del 70%. Podemos crear la variable precio total aplicando apply sobre una función personalizada.

def crear_precio_total(registro):
    if (registro.beds > 1) & ((registro.room_type == 'Private room') | (registro.room_type == 'Shared room')):
        salida = registro.price * registro.beds * 0.7
    else:
        salida = registro.price
    return(salida)

df['precio_total'] = df.apply(crear_precio_total, axis = 1)

print(df[['room_type','price','beds','precio_total']].head(30))

# Ahora vamos con la ocupación

# La variable que tenemos que nos permite medir esto es availability_365.
# Esta variable nos dice el número de días a un año vista que el inmueble NO está ocupado.
# Por tanto nos interesaría transformarla a una medida más directa de ocupación, por ejemplo el % del año que SI está ocupada. Podemos hacerlo con una tranformación directa.

df['ocupacion'] = ((365 - df.availability_365) / 365 * 100).astype('int')
print(df.head())

# TRANSFORMACIÓN DE VARIABLES DE ANÁLISIS

# Algunas de las preguntas semilla están dirigidas a comprobar cómo se comporta el precio o la ocupación según otras variables como el número de habitaciones, la media de valoraciones, etc.
# Normalmente podremos hacer mejor estos análisis si discretizamos la variable de análisis.

# En nuestro caso las candidatas para este análisis son: accommodates, bedrooms, beds y number_of_reviews.
# En bedrooms tiene sentido una discretización más personalizada. En las otras podemos hacerla automática.

# Discretizar bedrooms. Comenzamos por evaluar la distribución de los datos.

df.bedrooms.value_counts().plot.bar();
plt.show()

# Vamos a discretizar para 1,2,3 y más de 3. Podemos usar np.select

condiciones = [df.bedrooms == 1,
               df.bedrooms == 2,
               df.bedrooms == 3,
               df.bedrooms > 3]

resultados = ['01_Una','02_Dos','03_Tres','04_Cuatro o mas']

df['bedrooms_disc'] = np.select(condiciones, resultados, default = -999)

print(df.bedrooms_disc.value_counts())

df.bedrooms_disc.value_counts().plot.bar();
plt.show()

# Discretizar accommodates, beds y number_of_reviews
# Vamos a usar qcut para discritizar con percentiles 0.5, 0.8, 1

df['accommodates_disc'] = pd.qcut(df.accommodates,[0, 0.5, 0.8, 1],
                                 labels = ['0-3','4','5-16'])

df['accommodates_disc'].value_counts().sort_index(ascending = False).plot.barh();
plt.show()

df['beds_disc'] = pd.qcut(df.beds,[0, 0.5, 0.8, 1],
                         labels = ['1','2','3-24'])

df['beds_disc'].value_counts().sort_index(ascending = False).plot.barh();
plt.show()

df['number_of_reviews_disc'] = pd.qcut(df.number_of_reviews,[0, 0.5, 0.8, 1],
                                      labels = ['1-4','5-48','48-744'])

df['number_of_reviews_disc'].value_counts().sort_index(ascending = False).plot.barh();
plt.show()

# CREACIÓN DE VARIABLES CON DATOS EXTERNOS

# En este caso en concreto se podrían hacer muchas cosas con datos externos.
# Lo primero, que ya hemos incorporado parcialmente, es la palanca del precio del inmueble.
# Decíamos que la podíamos estimar multiplicando los metros cuadrados del inmueble por el precio por m2.
# El precio_m2 ya lo hemos conseguido, pero el tamaño del inmueble no lo tenemos en los datos.
# Lo que podemos hacer es establecer unos criterios en base al número de habitaciones.
# No es perfecto, pero nos servirá de aproximación.

# Estimación de los metros cuadrados del inmueble. Vamos usar el siguiente algoritmo:

# - una habitación: m2 = 50
# - dos habitaciones: m2 = 70
# - tres habitaciones: m2 = 90
# - cuatro habitaciones: m2 = 120
# - cinco o más habitaciones: m2 = 150

condiciones = [df.bedrooms == 1,
               df.bedrooms == 2,
               df.bedrooms == 3,
               df.bedrooms == 4,
               df.bedrooms > 4]

resultados = [50,70,90,120,150]

df['m2'] = np.select(condiciones, resultados, default = -999)
print(df['m2'].value_counts())

# Ahora ya podemos estimar el precio de compra del inmueble.
# Recordamos que al precio que nos sale le quitábamos un 30% por capacidad de negociación.

df['precio_compra'] = df.m2 * df.precio_m2 * 0.7
print(df[['bedrooms','m2','distrito','precio_m2','precio_compra']].head(20))

# Ahora vamos a poner un ejemplo de qué otro tipo de variables podemos construir.
# En este caso podríamos hacer mucho con las coordenadas x,y. Ya que en turismo la localización es muy importante.

# Por ejemplo podríamos calcular las distancias a diferentes puntos de interés como monumentos, lugares de ocio, recintos deportivos, etc.
# Simplemente como ejemplo vamos a calcular la distancia de cada inmueble a la Puerta del Sol.

# Para ello buscamos en Google su longitud y latitud: https://www.123coordenadas.com/coordinates/81497-puerta-del-sol-madrid Latitud: 40.4167278 Longitud: -3.7033387

# Cálculo de la distancia de cada inmueble a la Puerta del Sol

# Dada la curvatura de la tierra la distancia entre dos puntos a partir de su latitud y longitud se calcula con una fórmula que se llama distancia de Haversine.
# Una búsqueda en Google nos da una función ya construída para calcularla que podemos adaptar: https://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points

from math import radians, cos, sin, asin, sqrt

def haversine(lat1, lon1, lat2, lon2):

      R = 6372.8 #En km, si usas millas tienes que cambiarlo por 3959.87433

      dLat = radians(lat2 - lat1)
      dLon = radians(lon2 - lon1)
      lat1 = radians(lat1)
      lat2 = radians(lat2)

      a = sin(dLat/2)**2 + cos(lat1)*cos(lat2)*sin(dLon/2)**2
      c = 2*asin(sqrt(a))

      return R * c

# Las coordenadas de la Puerta del Sol serán lat1 y lon1

lat1 = 40.4167278
lon1 = -3.7033387

df['pdi_sol'] = df.apply(lambda registro: haversine(lat1,lon1,registro.latitude,registro.longitude),axis = 1)

# Comprobamos revisando la distancia media por distritos.

print(df.groupby('distrito').pdi_sol.mean().sort_values())

# GUARDAMOS EN EL DATAMART

df.to_sql('df_preparado', con = con, if_exists = 'replace')
