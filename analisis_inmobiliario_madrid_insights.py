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

- ¿Cual es la ocupación media? ¿Y por distritos? ¿Y por barrios?
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

# ANALISIS E INSIGHTS

# Esta es la parte más importante, donde vamos a obtener conclusiones relevantes para el objetivo utilizando todo el trabajo de preparación que se ha hecho, las técnicas de Business Analytics y vamos a crear una visualización en mapa.
# Para ello empezaremos dando respuesta a las preguntas semilla y es probable que en el proceso nos vayan surgiendo hallazgos interesantes que nos lleven a nuevas preguntas o a la aplicación de ciertas técnicas.

con = sa.create_engine('sqlite:///DatosCaso1/airbnb.db')
df = pd.read_sql('df_preparado', con = con)

print(df.head())

# Analisis sobre el precio

# ¿Cual es el precio medio? ¿y el rango de precios?¿Y por distritos? ¿Y por barrios?
# ¿Cual es el ranking de distritos y barrios por precio medio de alquiler?

print(df.precio_total.describe())

# Vemos que hay al menos un atípico por la parte de arriba que sesga la media, por tanto vamos a usar la mediana como medida de centralización más fiable

print(df.precio_total.median())

print(df.groupby('distrito').precio_total.median().sort_values(ascending = False))

# Nos llama la atención el dato de San Blas, vamos a verlo con más detalle a ver qué está pasando.

print(df.loc[df.distrito == 'San Blas - Canillejas'].sort_values('precio_total',ascending = False).head(10))

# Vemos que son precios en el entorno de los 3.000 - 5.000 euros!
# Al leer la descripción nos damos cuenta de todos estos precios están definidos por la final de la Champions League.

# Lo cual es un insight interesante:

# INSIGHT 1: pueden existir inmuebles con un valor regular residual pero con alto valor en momentos puntuales por acontenicimientos deportivos o espectáculos
# ¿Tendría sentido generar un producto de alquiler que consista en alquilar de forma "normal" a un precio inferior al mercado con la condición de que el inquilino deje el piso libre para alquilarlo "turísticamente" en fechas señaladas?

# En el resto no hay sorpresas, con distritos como Salamanca, Centro o Chanmartín a la cabeza.
# Pero por ejemplo vemos que la diferencia de precio media entre Retiro y Tetuán es muy baja.
# Esto nos lleva a comparar el precio medio por distrito con el precio medio de compra también por distrito.

temp = df.groupby('distrito')[['precio_total','precio_compra']].median()
print(temp)

plt.figure(figsize = (16,8))

sns.scatterplot(data = temp, x = 'precio_compra', y = 'precio_total')

# Ponemos las etiquetas

for cada in range(0,temp.shape[0]):
    plt.text(temp.precio_compra[cada], temp.precio_total[cada], temp.index[cada])

# Existe una clara correlación entre el precio de compra en cada distrito y el precio que podremos cobrar.
# Claramente se perciben tres clusters de bajo-bajo, medio-medio y alto-alto.

# Y la excepción de San Blas que ya sabemos por qué es.

# Por tanto como era esperable no hay a priori ningún "chollo" claro a este nivel.
# Vamos a repetir el análisis a nivel de barrio a ver si identificamos algo.

temp = df.groupby('neighbourhood')[['precio_total','precio_compra']].median()
print(temp)

"""plt.figure(figsize = (16,20))
sns.scatterplot(data = temp, x = 'precio_compra', y = 'precio_total')
"""
# Ponemos las etiquetas

for cada in range(0,temp.shape[0]):
    plt.text(temp.precio_compra[cada], temp.precio_total[cada], temp.index[cada])

# A este nivel ya vemos más cosas:

# - 3 barrios que sobresalen, posiblemente los 3 sean de San Blas
# - Dentro de cada grupo de bajo-medio-alto sí podemos empezar a separarar
    # - Bajo: Simancas, Ambroz, Marroquina, San Juan Bautista
    # - Medio: El Plantio, Valdemarín, Valdefuentes
    # - Medio-alto: Jerónimos, Fuente la reina
    # - Alto: Recoletos

#INSIGHT 2: Existen ciertos barrios que apriori pueden maximizar la relación coste-ingresos y además podemos segmentarlo por el tipo calidad del inmueble en el que nos interes invertir

print(df.loc[df.neighbourhood.isin(['Rosas','Canillejas','Hellin']),'distrito'].unique())

# ¿Qué factores (a parte de la localización determinan el precio del alquiler?
# Para responder a esta pregunta podemos construir un minicubo, ya que hemos discretizado nuestras variables de análisis.

# PASO 1: Seleccionar qué variables serán la métricas y cuales las dimensiones

metricas = ['precio_total','precio_compra']
dimensiones = ['bedrooms_disc','accommodates_disc','beds_disc','number_of_reviews_disc']

minicubo_precio = df[dimensiones + metricas]
print(minicubo_precio)

# PASO 2: Pasar a transaccional las dimensiones

minicubo_precio = minicubo_precio.melt(id_vars=['precio_total','precio_compra'])
print(minicubo_precio)

# PASO 3: Agregar las métricas por "variable" y "valor" con las funciones deseadas

minicubo_precio = minicubo_precio.groupby(['variable','value'])[['precio_total','precio_compra']].agg('median')
print(minicubo_precio)

# Sobre el minicubo vamos analizando cada variable.

print(minicubo_precio.loc['bedrooms_disc'])

"""f, ax = plt.subplots()
ax.plot(minicubo_precio.loc['bedrooms_disc'].precio_total)
ax2 = ax.twinx()
ax2.plot(minicubo_precio.loc['bedrooms_disc'].precio_compra,color = 'green');
"""

# En cuanto al número de habitaciones no hay nada que destacar.
# Existe una relación casi perfecta entre el precio de compra y el precio total que se puede cobrar.
# Parte de este efecto puede ser artificial, ya que usamos el número de habitaciones para calcular el precio total como el precio de compra.

print(minicubo_precio.loc['beds_disc'])

"""f, ax = plt.subplots()
ax.plot(minicubo_precio.loc['beds_disc'].precio_total)
ax2 = ax.twinx()
ax2.plot(minicubo_precio.loc['beds_disc'].precio_compra,color = 'green');
"""

# En cuanto al número de camas sí hay una conclusión:

# INSIGHT 3: El número de camas a evitar es 2. O bien ponemos una cama o intentamos meter todas las posibles.
# Dado que no había este efecto en el número de habitaciones ¿podría ser que los propietarios estén intentando meter muchas más camas que habitaciones para maximizar el ingreso?

# Veámoslo por ejemplo con los pisos de una habitación:

df[df.bedrooms == 1].groupby('beds').precio_total.median().plot();

# Efectivamente aquí hay algo, ya que figura que para pisos de una habitación hay gente que está metiendo hasta decenas de camas!
# Sería un tema a explorar con más detalle y comentar con alguien que conozca el negocio.

# Vamos a ver unos ejemplos:

print(df.loc[(df.bedrooms == 1) & (df.beds > 8)])

# Vamos a analizar ahora por el número de huéspedes que aceptan

print(minicubo_precio.loc['accommodates_disc'])

"""f, ax = plt.subplots()
ax.plot(minicubo_precio.loc['accommodates_disc'].precio_total)
ax2 = ax.twinx()
ax2.plot(minicubo_precio.loc['accommodates_disc'].precio_compra,color = 'green');
"""

# INSIGHT 4: El número óptimo de huéspedes está en 3, ya que el precio de los inmuebles para acomodar 3 es el mismo que para acomodar 1 o 2. A partir de 4 el piso necesita ser mayor y el precio de compra se incrementa bastante

# Por último vamos a analizar la variable que hemos construído de cercanía a un punto de interés para ver si tiene efecto sobre el precio de las habitaciones.
# En una situación real hubiéramos construído muchas de este tipo, y repetido el análisis con todas.

# En este caso como hemos construído la distancia a la Puerta del Sol vamos a evaluar solo los distritos para lo que esto puede ser relevante, es decir los más céntricos.
# Para ello primero vamos a calcular la distancia media por distrito y elegir un punto de corte.

print(df.groupby('distrito').pdi_sol.median().sort_values())

# Vamos a cortar en Latina incluído. Y sobre esa selección vamos a visualizar con un scatter.

print(df.groupby('distrito').pdi_sol.median().sort_values()[0:7].index.to_list())

seleccion = df.groupby('distrito').pdi_sol.median().sort_values()[0:7].index.to_list()

"""plt.figure(figsize = (16,12))
sns.scatterplot(data = df.loc[df.distrito.isin(seleccion)], x = 'pdi_sol', y = 'precio_total');
"""

# INSIGHT 5: Estando dentro del distrito parece que la cercanía a puntos de interés no tiene tanto impacto como sería esperable.
# Eso abre la puerta a buscar inmuebles que estando en un distrito céntrico no estén justo al lado del PdI y por tanto esperablmente tengan un precio de compra menor

# ANÁLISIS SOBRE LA OCUPACIÓN

# Para este punto podríamos repetir exactamente los mismos análisis que con el precio pero cambiando la variable precio por la de ocupación que habíamos construido.
# Dado que sería igual no vamos a desarrollarlo y te lo dejo como tarea para que practiques e intentes obtener tus primeros insights.

# 1. Cargar los datos: Leer el conjunto de datos desde la base de datos SQLite en un DataFrame de Pandas.

# 2. Análisis sobre el precio del alquiler:
      # - Calcular el precio medio, rango de precios, y precios por distritos y barrios.
      # - Crear un ranking de distritos y barrios por precio medio de alquiler.

# 3. Análisis sobre la ocupación:
      # - Calcular la ocupación media y por distritos y barrios.
      # - Determinar la probabilidad de cada nivel de ocupación en cada distrito.

# 4. Análisis sobre el precio de compra:
      # - Crear un ranking de precio por m2 por distrito.
      # - Calcular la relación entre el precio del inmueble y el precio del alquiler por distrito.

# 5. Insights y conclusiones: Resumir los insights y recomendaciones basadas en los análisis anteriores.

# Occupancy Analysis
# What is the average occupancy? And by district? And by neighborhood?

avg_occupancy = df['ocupacion'].mean()
occupancy_by_district = df.groupby('distrito')['ocupacion'].mean().sort_values(ascending=False)
occupancy_by_neighbourhood = df.groupby('neighbourhood')['ocupacion'].mean().sort_values(ascending=False)

print(f"Average Occupancy: {avg_occupancy}")
print(f"Occupancy by District: \\n{occupancy_by_district}")
print(f"Occupancy by Neighbourhood: \\n{occupancy_by_neighbourhood}")

# How likely is each occupancy level in each district?
occupancy_probability_by_district = df.groupby(['distrito', 'ocupacion']).size().groupby(level=0).apply(
    lambda x: 100 * x / x.sum()
).reset_index(drop=True, name='probability')

# Occupancy Ranking by District and Neighborhood
ranking_district_occupancy = df.groupby('distrito')['ocupacion'].mean().sort_values(ascending=False)
ranking_neighbourhood_occupancy = df.groupby('neighbourhood')['ocupacion'].mean().sort_values(ascending=False)

print(f"Ranking of Districts by Occupancy: \\n{ranking_district_occupancy}")
print(f"Ranking of Neighbourhoods by Occupancy: \\n{ranking_neighbourhood_occupancy}")

# Visualization
plt.figure(figsize=(16, 8))
sns.barplot(x='distrito', y='ocupacion', data=df, estimator=sum, ci=None)
plt.title('Occupancy by District')

# Save the plots
# plt.savefig("occupancy_by_district.png")

# INSIGHT 6: 

"""
 - Ocupación Media: La ocupación media es aproximadamente del 56.93
Esto nos da una idea del rendimiento promedio de las propiedades.

- Top 5 Distritos por Ocupación: Los distritos con la mayor ocupación media son Arganzuela (64.21), Chamberí (59.51), Barajas (59.45), Moratalaz (59.35), y Salamanca (59.26).
- Top 5 Barrios por Ocupación: Los barrios con la mayor ocupación media son Atalaya (100), Valdemarín (81.75), Corralejos (75.36), Acacias (75.22), y Pavones (75.2).

- Probabilidad de Ocupación por Distrito: En el distrito de Arganzuela, por ejemplo, la probabilidad de tener una ocupación de 0 es del 5.77, de 1 es del 1.89, etc.
Este patrón puede variar para otros distritos y puede ser útil para entender la volatilidad de la ocupación.

- Top 5 Distritos en Ranking de Ocupación: Los distritos con mejor rendimiento en términos de ocupación son los mismos que los que tienen la mayor ocupación media, lo que sugiere que son consistentemente buenos en términos de demanda.
- Top 5 Barrios en Ranking de Ocupación: Al igual que los distritos, los barrios con mayor ocupación también tienen el mejor rendimiento, lo que podría hacerlos más atractivos para inversores o arrendadores.
"""

# ANÁLISIS GEOGRÁFICO SOBRE UN MAPA

# El análisis geográfico es una disciplina en si misma y de bastante complejidad.
# Pero afortunadamente hay una alternativa en Python que lo hace muy sencillo y cubre todo lo que necesitamos de forma práctica para nuestro fin.
# Es un paquete que se llama Folium y es una implementación de la tecnología Leaflet en Python.
# Lo único que necesitamos para usarlo es tener las coordenadas de latitud y longitud.

# https://python-visualization.github.io/folium/index.html

import folium

# Con folium no es necesario instalar mapas, ya los trae por defecto, lo único que tenemos que hacer para inicializar un mapa es pasarle las coordenadas de inicio y opcionalmente un nivel de zoom.
# Vamos a usar las coordenadas de la Puerta del Sol que ya teníamos.

# Coordenadas de inicio (Puerta del Sol)
lat_inicio, lon_inicio = 40.4167278, -3.7033387

# Filtrar datos para el distrito de San Blas
datos = df[df.distrito == 'San Blas - Canillejas'].copy()

# Categorizar el precio total en diferentes colores
datos['precio_total_disc'] = pd.qcut(datos['precio_total'], q=[0, .25, .5, .75, 1.], 
                              labels=['yellow', 'orange', 'blue', 'red'])

# Inicializar mapa
mapa = folium.Map(location=[lat_inicio, lon_inicio], zoom_start=12)

# Añadir marcadores circulares para cada piso en el distrito de San Blas
for _, piso in datos.iterrows():
    folium.CircleMarker(
        location=[piso['latitude'], piso['longitude']],
        popup=str(piso['precio_total']),
        fill=True,
        color=piso['precio_total_disc'],
        fill_opacity=1,
        radius=5
    ).add_to(mapa)

# Guardar el mapa en un archivo HTML si lo necesitas
mapa.save('mapa_circular_optimizado.html')
