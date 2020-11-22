#!/usr/bin/env python
# coding: utf-8

import streamlit as st

import numpy as np
import pandas as pd
import numpy_financial as npf
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.transform import dodge
from bokeh.io import output_file, show
from bokeh.models import FixedTicker
import math

st.title('Evaluación de créditos')

# Inputs del usuario
## Primer crédito [Monto, tasa anual, Plazo]
st.markdown('## **Paso 1:** Introduce los datos de tu crédito')
### Monto
st.markdown('### Monto')
monto_1 = st.number_input('', format='%f', key='monto_credito')
### Tasa anual
st.markdown('### Tasa anual de interés (Ejemplo: 54.6%)')
tasa_anual_1 = st.number_input('', format='%g',
                                key='tasa_original')
### Meses restantes
st.markdown('### Plazo restante en meses')
plazo_1 = st.number_input('', format='%f', key='plazo_original')

st.markdown('## **Paso 2:** Introduce los datos de las nuevas condiciones')
### Tasa anual
st.markdown('### Nueva tasa anual de interés (Ejemplo: 54.6%)')
tasa_anual_2 = st.number_input('', format='%g',
                                key='tasa_nueva')
### Meses restantes
st.markdown('### Nuevo plazo en meses')
plazo_2 = st.number_input('', format='%f', key='plaza_nueva')

st.markdown('## **Paso 3:** Resultados')
#Calculo del pago mensual
##Conertir variables
tasa_anual_1_mod = (1+tasa_anual_1/100)**(1/12)-1
tasa_anual_2_mod = (1+tasa_anual_2/100)**(1/12)-1

caso_original = npf.pmt(tasa_anual_1_mod, plazo_1, monto_1)*(-1)
caso_nuevo = npf.pmt(tasa_anual_2_mod, plazo_2, monto_1)*(-1)
##Con formato
formatted_caso_original = "${:,.2f}".format(caso_original)
formatted_caso_nuevo = "${:,.2f}".format(caso_nuevo)

#Parar proceso
valores_necesarios = [monto_1, tasa_anual_1, plazo_1, tasa_anual_2, plazo_2]
for i in valores_necesarios:
    if not i:
        st.warning('Por favor llena los parámetros')
        st.stop()

st.markdown('### Pagos')
#Credito caso_original
df_1 = pd.DataFrame()
perido_list = []
pago_list = []
year_list = []

for i in range(1, int(plazo_1)+1):
    pago_acumulado = caso_original*i
    periodo = i
    year = math.ceil(i/12)
    #Appendear
    perido_list.append(periodo)
    pago_list.append(pago_acumulado)
    year_list.append(year)

df_1['Periodo'] = perido_list
df_1['Pago acumulado'] = pago_list
df_1['Credito'] = 'Original'
df_1['year'] = year_list
##Agrupar por año
df_1_grouped = df_1.groupby(['year', 'Credito']).agg({'Pago acumulado': 'max'}).reset_index()
#Crédito Nuevo
df_2 = pd.DataFrame()
perido_list_2 = []
pago_list_2 = []
year_list_2 = []

for i in range(1, int(plazo_2)+1):
    pago_acumulado_2 = caso_nuevo*i
    periodo_2 = i
    year_2 = math.ceil(i/12)
    #Appendear
    perido_list_2.append(periodo_2)
    pago_list_2.append(pago_acumulado_2)
    year_list_2.append(year_2)


df_2['Periodo'] = perido_list_2
df_2['Pago acumulado'] = pago_list_2
df_2['Credito'] = 'Nuevo'
df_2['year'] = year_list_2
##Agrupar por año
df_2_grouped = df_2.groupby(['year', 'Credito']).agg({'Pago acumulado': 'max'}).reset_index()

#Unir tablas y pivotear
df = pd.concat([df_1_grouped, df_2_grouped])
pivot = df.pivot(index='year', columns='Credito', values='Pago acumulado').reset_index()
pivot = pivot.fillna(0)



#Crear gráfico
periodos = pivot['year'].astype('str').unique().tolist()
creditos = ['Original', 'Nuevo']
pagos_1 = pivot['Original'].tolist()
pagos_2 = pivot['Nuevo'].tolist()

data = {'Periodo' : periodos,
        'Original' : pagos_1,
        'Nuevo' : pagos_2}
source = ColumnDataSource(data=data)


p = figure(x_range=periodos, plot_height=250, title="Pago acumulado",
           x_axis_label='Año', y_axis_label='Pesos mexicanos',
           toolbar_location=None, tools="")
p.vbar(x=dodge('Periodo', -0.17, range=p.x_range), top='Original', width=0.3, source=source,
       color="#718dbf", legend_label="Original")
p.vbar(x=dodge('Periodo', 0.17, range=p.x_range), top='Nuevo', width=0.3, source=source,
       color="#e84d60", legend_label="Nuevo")

p.x_range.range_padding = 0.1
p.xgrid.grid_line_color = None
p.legend.location = "top_left"
p.legend.orientation = "horizontal"
p.title.align = 'center'
p.title.text_font_size = '20pt'
p.plot_height = 400
p.plot_width = 600


st.bokeh_chart(p, use_container_width=True)



st.markdown('### Pago mensual')
st.write('Crédito original: ', formatted_caso_original)
st.write('Crédito nuevo: ', formatted_caso_nuevo)

st.markdown('### Pago total')
total_original = "${:,.2f}".format(caso_original*plazo_1)
total_nuevo = "${:,.2f}".format(caso_nuevo*plazo_2)

st.write('Crédito original: ', total_original)
st.write('Crédito nuevo: ', total_nuevo)

st.markdown('### Pago de interés total')
interes_original = (caso_original*plazo_1)- monto_1
interes_nuevo = (caso_nuevo*plazo_2)- monto_1
formatted_interes_original = "${:,.2f}".format(interes_original)
formatted_interes_nuevo = "${:,.2f}".format(interes_nuevo)

st.write('Crédito original: ', formatted_interes_original)
st.write('Crédito nuevo: ', formatted_interes_nuevo)

st.markdown('### Ahorro nominal')
ahorro = (caso_original*plazo_1)-(caso_nuevo*plazo_2)
formatted_ahorro = "${:,.2f}".format(ahorro)
st.write('Total: ', formatted_ahorro)
