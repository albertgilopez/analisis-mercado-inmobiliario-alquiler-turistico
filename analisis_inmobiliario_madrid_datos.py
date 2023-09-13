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

# %matplotlib inline # para que los gráficos aparezcan en Jupyter Notebook
# %config IPCompleter.greedy=True # cuando pulsamos la tecla tabuladora que autocomplete

# ENTENDER LOS FICHEROS

# En la web de AirBnB podemos ver la descripción de las tablas:

listings = pd.read_csv('DatosCaso1/listings.csv')

print(listings.head())
print(listings.info())

listings_det = pd.read_csv('DatosCaso1/listings.csv.gz',compression='gzip') # el archivo de listing con más detalles

print(listings_det.head())
print(listings_det.info())

# - Son los mismos registros pero el fichero de detalle tiene más columnas.
# - Podríamos unirlas mediante el campo ID

# Vamos a revisar el archivo reviews agregado (la fecha en la que se ha puesto una reseña en el inmueble)

"""reviews = pd.read_csv('DatosCaso1/reviews.csv')

print(reviews.head())
print(reviews.info())

reviews_det = pd.read_csv('DatosCaso1/reviews.csv.gz',compression = 'gzip')

print(reviews_det.head())
print(reviews_det.info())"""

# - Son los mismos registros pero el fichero de detalle tiene más columnas.
# - Realmente esta info de las reseñas no nos aporta nada a nuestro objetivo, así que no usaremos estas tablas

# Vamos a revisar el archivo calendar (a futuro)

"""calendar = pd.read_csv('DatosCaso1/calendar.csv.gz',compression = 'gzip')

print(calendar.head(30))
print(calendar.info())"""

# - Esta tabla se proyecta hacia el futuro, y parece contener la disponibilidad de reservas
# - No es información que nos sirva a nuestros fines y por tanto no la usaremos. Podríamos utilizar la availability del fichero listing

# Vamos a revisar el archivo neighbourhoods

"""neigh = pd.read_csv('DatosCaso1/neighbourhoods.csv')

print(neigh.head(5))
print(neigh.info())"""

# - Es simplemente un maestro de vecindario y grupo de vecindario
# - En principio no la usaremos, ya que tanto el vecindario como su grupo ya están incorporados en otras tablas

# Vamos a revisar el archivo neighbourhoods_geo 

"""neigh_geo = pd.read_json('DatosCaso1/neighbourhoods.geojson')

print(neigh_geo.head(5))
print(neigh_geo.info())"""

# - Más pensado para hacer una elaboración de mapas más detallada (geometría)

# CREACIÓN DE UNA BASE DE DATOS

# Usaremos una base de datos sqlite, sin servidor y sin configuración, un formato ideal para almacenar proyectos "propios".
# Lectura recomendada para entender mejor los pros y contras de Sqlite: https://www.hostgator.mx/blog/sqlite-que-es-y-diferencias-con-mysql/

import sqlalchemy as sa

con = sa.create_engine('sqlite:///DatosCaso1/airbnb.db')

# Creamos las tablas y cargamos los datos

listings.to_sql('listings', con = con, if_exists = 'replace')
listings_det.to_sql('listings_det', con = con, if_exists = 'replace')

# CREACIÓN DEL DATAMART ANALÍTICO

# 1. Acceder a la base de datos
# 2. Importar los datos como dataframes de Pandas
# 3. Realizar la calidad de datos
# 4. Crear el datamart analítico
# 5. Guardarlo como una tabla en la base de datos para no tener que repetir el proceso

# Si desconociéramos los nombres de las tablas que están en la base de datos, la doc de SqlAlchemy nos dice que podemos usar la función inspect: https://docs.sqlalchemy.org/en/14/core/reflection.html#fine-grained-reflection-with-inspector

from sqlalchemy import inspect

insp = inspect(con)
tablas = insp.get_table_names()
print(tablas)

listings = pd.read_sql('listings', con)
listings_det = pd.read_sql('listings_det', con)

# Si hubieran muchas tablas podrías utilizar
# for tabla in tablas:
#     exec(f'{tabla} = pd.read_sql(tabla, con)')

# Y también podríamos revisar las dimensiones de cada tabla de forma automática para ver que han cargado bien.
# for cada in tablas:
#     print(cada + ': ' + str(eval(cada).shape))

# DATOS EXTERNOS

# En nuestros datos no tenemos el precio de compra de un inmueble, pero habíamos visto que es una de las palancas principales.
# En esta página tenemos justo la info que necesitamos: https://www.idealista.com/sala-de-prensa/informes-precio-vivienda/venta/madrid-comunidad/madrid-provincia/madrid/
# Podemos extraerla de forma sencilla con el plugin instant data scraper de Chrome, y guardarla en nuestra carpeta Datos con el nombre 'precios_idealista.read_csv'
# Cargamos los datos, quitamos el primer registro y seleccionamos solo las columnas de precio y distrito

precio_m2 = pd.read_csv('DatosCaso1/precios_idealista.csv')

print(precio_m2.head())
print(precio_m2.info())

precio_m2 = pd.read_csv('DatosCaso1/precios_idealista.csv') \
	.loc[1:,['table__cell','icon-elbow']] \
    .rename(columns = {'table__cell':'precio_m2','icon-elbow':'distrito'})

print(precio_m2)

# Limpiamos el precio quitando la unidad, quitando los puntos de separador de miles y cambiando el tipo a entero

precio_m2['precio_m2'] = precio_m2.precio_m2.str.split(expand = True)[0].str.replace('.','',regex=False).astype('int')

print(precio_m2)

# CALIDAD DE DATOS

print(listings.head())
print(listings.info())

# VARIABLES Y TIPOS

# Vamos a eliminar aquellas variables que no necesitaremos directamente para nuestros objetivos.

a_eliminar = ['index',
              'host_name',
              'number_of_reviews',
              'last_review',
              'reviews_per_month',
              'number_of_reviews_ltm',
              'license'
             ]

listings.drop(columns = a_eliminar, inplace=True)

print(listings)

# Viendo los tipos de datos debemos pasar algunas variasbles a objeto (neighbourhood_group, neighbourhood, room_type) a categóricas.

for variable in ['neighbourhood_group','neighbourhood','room_type']:
    listings[variable] = listings[variable].astype('category')

print(listings.info())

# ANÁLISIS DE NULOS

# Por la columna Non-null del info() vemos que solo name tiene 3 nulos.
# Los revisamos pero vemos que no supone un problema, así que los dejamos.

print(listings[listings.name.isna()])

# ANÁLISIS DE DUPLICADOS

# Comprobamos si hay algún registro duplicado

print(listings.duplicated().sum())

# ANÁLISIS DE VARIASBLES CATEGÓRICAS

# Vamos a analizar los valores y las frecuencias de las variables categóricas

print(listings.neighbourhood_group.value_counts())
print(listings.neighbourhood.value_counts())
print(listings.room_type.value_counts())

# Vemos que hay hoteles. Nuestra empresa no se plantea comprar hoteles, así que tenemos que eliminar estos registros.

listings = listings.loc[listings.room_type != 'Hotel room']
print(listings.room_type.value_counts())

# ANÁLISIS DE VARIABLES NUMÉRICAS

# De las variables numéricas tiene sentido analizar desde price hasta availability_365, osea desde las posiciones de columnas de la 8 a la 11

print(listings.iloc[:,8:12].describe().T)

# - En el precio hay que revisar mínimos y máximos
# - En minimum_nights hay que revisar los máximos
# - En calculated_host_listings_count hay que revisar los máximos

# Revisamos mínimos y máximos en el precio

listings.price.plot.kde()
# plt.show()

# Revisamos los máximos

plt.figure(figsize=(16,8))
listings.price.loc[listings.price > 1000].value_counts().sort_index().plot.bar()
plt.xticks(size = 10);
# plt.show()

# - El valor 9999 normalmente suele ser una forma de imputar nulos, pero en este caso su frecuencia no está muy lejos de otros valores que pueden ser válidos, como el 8000, así que no lo vamos a tocar

# Revisamos los valores cercanos a cero

plt.figure(figsize=(16,8))
listings.price.loc[listings.price < 30].value_counts().sort_index().plot.bar()
plt.xticks(size = 10);
# plt.show()

# - Hay un pico en 20 euros, y parece que por debajo de esa cantidad sería difícil obtener rentabilidad, así que vamos a descartar los inmuebles que se alquilan por debajo de 20 euros

listings = listings.loc[listings.price > 19]
print(listings)

# Para minimum_nights y alculated_host_listings_count habría que hacer un ejercicio similar.

listings.minimum_nights.plot.kde()
# plt.show()

# Graficando los máximos en la columna 'minimum_nights' para un rango específico (entre 30 y 180)

plt.figure(figsize=(16, 8))
listings['minimum_nights'].loc[listings['minimum_nights'] >= 30].value_counts().sort_index().plot.bar()
plt.title('Frecuencia de Mínimas Noches entre 30 y 180')
plt.xlabel('Mínimas Noches')
plt.ylabel('Frecuencia')
plt.xticks(size=10)
# plt.show()

# Por rentabilidad nos puede interesar como mínimo los inmuebles que se ocupan al menos 30 días al año (habría que verlo con la dirección)

listings.calculated_host_listings_count.plot.kde()
# plt.show()

# Graficando los máximos en la columna 'calculated_host_listings_count'
plt.figure(figsize=(16, 8))
listings['calculated_host_listings_count'].value_counts().sort_index().plot.bar()
plt.title('Frecuencia de Calculated Host Listings Count')
plt.xlabel('Calculated Host Listings Count')
plt.ylabel('Frecuencia')
plt.xticks(size=10)
# plt.show()

# - Vemos que hay host que tienen hasta casi 200 inmuebles, esto pueden ser empresas de la competencia que se dedican al mismo negocio que nosotros

# Vamos a trabajar la tabla listings_det

print(listings_det.head())
print(listings_det.info())

# VARIABLES Y TIPOS

# Vamos a seleccionar solo aquellas variables que nos aporten información relevante para nuestros objetivos.

a_incluir = ['id',
              'description',
              'host_is_superhost',
              'accommodates',
              'bathrooms',
              'bedrooms',
              'beds',
              'number_of_reviews',
              'review_scores_rating',
              'review_scores_communication',
              'review_scores_location'
             ]

listings_det = listings_det.loc[:,a_incluir]

print(listings_det)

# Pasamos host_is_superhost a categórica.

listings_det['host_is_superhost'] = listings_det['host_is_superhost'].astype('category')
    
listings_det.info()

# ANÁLISIS DE NULOS

print(listings_det.isna().sum())

# - bathrooms está totalmente a nulos, por tanto la eliminamos
# - description no pasa nada porque tenga nulos, así que la dejamos
# - host_is_superhost tiene muy pocos nulos y no es una variables super relevante, así que la dejamos
# - beds: podemos intentar imputarla a partir de accomodates
# - bedrooms sí es una variable importante para nosotros, podemos intentar imputar los nulos a través de proxies como accomodates o beds

# Vamos a ver si podemos hacer una imputación de beds a partir del número de personas que se pueden acomodar.

print(pd.crosstab(listings_det.beds, listings_det.accommodates))

# Parece que sí podríamos hacer una asignación mas o menos directa. Leyendo la matriz en vertical vemos que:

# - una o dos personas se suelen corresponder con una cama
# - tres o cuatro personas se suelen corresponder con dos camas
# - cinco o seis personas se suelen corresponder con tres camas
# - a más de 6 personas le vamos a poner cuatro camas

# Repasamos el número de nulos y la frecuencia de cada valor

print(listings_det['beds'].value_counts(dropna = False))

# Creamos una función para imputar los nulos de beds en base a accommodates

def imputar_nulos(registro):

    #Lista de condiciones

    condiciones = [(registro.accommodates <= 2),
               (registro.accommodates > 2) & (registro.accommodates <= 4),
               (registro.accommodates > 4) & (registro.accommodates <= 6),
               (registro.accommodates > 6)]

    resultados = [1,2,3,4]
    
    return(np.select(condiciones,resultados, default = -999))

listings_det.loc[listings_det.beds.isna(),'beds'] = listings_det.loc[listings_det.beds.isna()].apply(imputar_nulos, axis = 1).astype('int64')
print(listings_det.beds.value_counts(dropna = False))

# Ahora vamos a ver si podemos hacer una imputación de bedrooms.
# Empezamos por cruzar el número de habitaciones con el número de personas que se pueden acomodar.

print(pd.crosstab(listings_det.bedrooms, listings_det.accommodates))

# No parece muy fiable. Vamos a contrastarlo con el número de camas.

print(pd.crosstab(listings_det.bedrooms, listings_det.beds, dropna=False))

# Aquí sí podríamos hacer una asignación más directa. Leyendo la matriz en vertical vemos que:

# - cero, una o dos camas se suele corresponder con una habitación
# - tres o cuatro camas se suele corresponder con dos habitaciones
# - cinco o seis camas se suele corresponder con tres habitaciones
# - a más camas le vamos a poner cuatro habitaciones

# Vamos a modificar la función que habíamos creado para imputar los nulos de bedrooms a partir de beds. Primero hacemos el conteo de bedrooms:

print(listings_det.bedrooms.value_counts(dropna = False))

def imputar_nulos(registro):

    #Lista de condiciones

    condiciones = [(registro.beds <= 2),
               (registro.beds > 2) & (registro.beds <= 4),
               (registro.beds > 4) & (registro.beds <= 6),
               (registro.beds > 6)]

    resultados = [1,2,3,4]
    
    return(np.select(condiciones,resultados, default = -999))

listings_det.loc[listings_det.bedrooms.isna(),'bedrooms'] = listings_det.loc[listings_det.bedrooms.isna()].apply(imputar_nulos, axis = 1).astype('int64')

print(listings_det.bedrooms.value_counts(dropna = False))

# Y por último borramos bathrooms:

listings_det.drop(columns = 'bathrooms', inplace = True)
print(listings_det)

# ANÁLISIS DE DUPLICADOS

# Comprobamos si hay algún registro duplicado

print(listings_det.duplicated().sum())

# ANÁLISIS DE VARIABLES CATEGÓRICAS

# Vamos a analizar los valores y las frecuencias de las variables categóricas

print(listings_det.host_is_superhost.value_counts())

# ANÁLISIS DE VARIABLES NUMÉRICAS

print(listings_det.describe(include = 'number').T)

# No vemos nada extraño. En este punto ya hemos detectado y corregido los principales problemas de calidad de datos así que pasamos a crear el datamart analítico integrando nuestras tablas

# DATAMART ANALÍTICO

# Tenemos 2 tablas principales:

# - listings
# - listings_det

# Y sabemos que ambas comparten el campo ID, por tanto podemos cruzarlas por él.
# La tabla principal es listings, ya que la de detalle lo que hace es darnos datos adicionales.

# Además tambien tenemos la tabla del precio, que en este caso cruza conceptualmente con listings a través del distrito (neighbourhood_group).
# Aunque no hemos comprobado todavía que los literales sean iguales, por tanto quizá será necesario hacer alguna corrección manual.

# Vamos a empezar por las 2 principales. Dado que va a mandar la tabla listings el resultado final tendrá que tener tantas filas como listings y tantas columnas como las de ambas tablas (menos 1 por el ID que se quedará como una única variable)

print(listings.shape)
print(listings_det.shape)

# Es decir, si sale bien la tabla final tendrá 17710 filas y 21 columnas.

df = pd.merge(left = listings, right = listings_det, how = 'left', on = 'id')
print(df)

# Ahora vamos a ver cómo podemos incorporar la información externa del precio por metro cuadrado.
# Para ello lo primero es analizar los valores de la variable distrito en ambas tablas, ya que necesitan coincidir para que podamos cruzarlos.
# En df la variable es categórica, así que para sacar los niveles tenemos que usar .categories

distritos1 = pd.Series(df.neighbourhood_group.unique().categories).sort_values()
print(distritos1)

distritos2 = precio_m2.distrito
print(distritos2)

# Comparando parece todo igual excepto:

# - Fuencarral - El Pardo
# - Moncloa - Aravaca
# - San Blas - Canillejas

# Por tanto vamos a reemplazar estos valores en precio_m2 para que sean iguales a los de df y podamos cruzarlos

precio_m2.distrito = precio_m2.distrito.map({'Fuencarral':'Fuencarral - El Pardo',
                        'Moncloa':'Moncloa - Aravaca',
                        'San Blas':'San Blas - Canillejas'}) \
                    .fillna(precio_m2.distrito)

print(precio_m2)

# Ahora sí que ya podemos cruzarlos. Manda df.

df = pd.merge(left = df, right = precio_m2, how = 'left', left_on='neighbourhood_group', right_on='distrito')
print(df)

# Comprobamos que no se hayan generado nulos en la unión.
print(df.precio_m2.isna().sum())

# GUARDAR EN LA BASE DE DATOS

# Ahora que ya tenemos el tablón de análisis vamos a guardarlo en la base de datos para que cada vez que queramos hacer análisis no tengamos que repetir todo el procesamiento de este notebook

df.to_sql('df', con = con, if_exists = 'replace')



