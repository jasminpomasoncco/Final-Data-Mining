# -*- coding: utf-8 -*-
"""Trabajo Final - Data Mining.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1PE6TDqoJemUhRh4Hi0C4h5op1H3uQbzH
"""

!pip install pyfim

from fim import *
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random
from graphviz import *

pd.set_option('display.max_colwidth', None)

df1 = pd.read_csv("Compras.csv",delimiter=';')
df1.head()

print(df1.columns)
print(df1.shape)

"""# **PREPROCESAMIENTO DE LA DATA**"""

df1.info()

df1.isnull().sum()

na_ratio = ((df1.isnull().sum() / len(df1))*100)
print(na_ratio)

df1.dropna(subset=['Itemname'],inplace=True)

df1.duplicated().sum()

df1.drop_duplicates(inplace=True)

na_ratio = ((df1.isnull().sum() / len(df1))*100)
print(na_ratio)

df1['Price'] = df1['Price'].str.replace(',', '.').astype(float)

df1 = df1[(df1['Quantity']>0) & (df1['Price']>0)]

df1 = df1[df1['Itemname'].notnull()]

na_ratio = ((df1.isnull().sum() / len(df1))*100)
print(na_ratio)

df1 = df1.fillna('#NV')

df1['TotalPrice'] = df1['Quantity'] * df1['Price']

df1.head()

df1.info()

unique_items = df1['Itemname'].unique()
print('Items únicos: ', len(unique_items))
print(unique_items)

CountOfItem = df1['Itemname'].value_counts()
sortedItems = CountOfItem.sort_values(ascending=False)
print('top 10 items:\n',sortedItems.head(10))

"""# **VISUALIZACIÓN DE LA DATA**"""

print('Items únicos: ', len(unique_items))
unique_items = df1['Itemname'].unique()
print(unique_items)

unique_boletas = df1['BillNo'].unique()
print('Boletas únicas: ', len(unique_boletas))
print(unique_boletas)

import plotly.express as px

item_freq = df1['Itemname'].value_counts().sort_values(ascending=False).head(20)

# top 20 items
fig = px.bar(item_freq, x=item_freq.index, y=item_freq.values, color=item_freq.index,
             labels={'x': 'Item name', 'y': 'Frequency (absolute)'}, title='Absolute Item Frequency Plot')

fig.update_layout(xaxis={'categoryorder':'total descending'},
                  xaxis_title='Item name', yaxis_title='Frequency (absolute)',
                  title='Absolute Item Frequency Plot',
                  xaxis_type='category',height = 600)

fig.show()

def to_transactionnal(df, column_trans, column_items):
  transactions = []
  for v in df[column_trans].unique():
    transactions.append(list(df[df[column_trans] == v][column_items].values))
  return transactions

trans = to_transactionnal(df1, 'BillNo', 'Itemname')
print(len(trans))

trans

print('La factura {} contiene los siguientes items {}'.format(0,trans[0]))
print('La factura {} contiene los siguientes items {}'.format(10,trans[10]))
print('La factura {} contiene los siguientes items {}'.format(100,trans[100]))
print('La factura {} contiene los siguientes items {}'.format(1000,trans[1000]))
print('La factura {} contiene los siguientes items {}'.format(5000,trans[5000]))
print('La factura {} contiene los siguientes items {}'.format(10000,trans[10000]))

#PARA UN SUPPORT DE 1% Y MÍNIMO 2 ITEMS
r1 = fpgrowth(trans, supp=1, zmin=2)
df = pd.DataFrame(r1)
df.columns = ['Itemset', 'Freq']
df.sort_values(by='Freq', ascending=False)

#Mining closed itemsets with 1% for min_freq and 2 for min_size
r2 = fpgrowth(trans, target='c', supp=1, zmin=2)
df2 = pd.DataFrame(r2)
df2.columns = ['Itemset', 'Freq']
df2.sort_values(by='Freq', ascending=False)

r3 = fpgrowth(trans, target='m', supp=1, zmin=2)
df3 = pd.DataFrame(r3)
df3.columns = ['Itemset', 'Freq']
df3.sort_values(by='Freq', ascending=False)

"""# **Mining Association Rules**

Support 0.5% and confidence 40%
"""

re = fpgrowth(trans, target='r', supp=1.5, conf=40, report='aSC')
print('Hay {} reglas'.format(len(re)))
df_re = pd.DataFrame(re)
df_re.columns = ['Consecuente', 'Antecendente', 'Freq', 'Freq(%)', 'Conf']
df_re.sort_values(by='Conf', ascending=False)

rf = fpgrowth(trans, target='r', supp=1, conf= 50, report='scl')
df_rf = pd.DataFrame(rf)
df_rf.columns = ['Consequent', 'Antecedent', 'Freq', 'Conf', 'Lift']
df_rf.sort_values(by='Conf', ascending=False)

def reglas(trans_, supp_values=[0.5,1,1.5], conf_=40):
  for supp_ in supp_values:
    r = fpgrowth(trans_, target = 'r', supp=supp_, conf= conf_, report='scl')
    df_rules = pd.DataFrame(r)
    df_rules.columns = ['Consequent', 'Antecedent', 'Freq', 'Conf', 'Lift']

    #filtrar los valores de lift mayores a 1
    filtered_lift = df_rules[df_rules['Lift']>1]['Lift']
    #Calcular el promedio de lift y conf
    avg_lift = filtered_lift.mean()
    avg_conf = df_rules['Conf'].mean()
    #contar el número de registros
    num_rows = len(df_rules)

    print(f"Iteración con supp={supp_}, número de registros: {num_rows}")
    print(f"Promedio de lift (excluyendo lift <= 1): {avg_lift}")
    print(f"Promedio de conf: {avg_conf}")
    print(" ")

reglas(trans)

#from apyori import apriori

#rules=apriori(transactions=trans,min_support=0.001,min_confidence=0.5,min_lift=3,min_length=2,max_length=3)
#results=list(rules)
#def inspect(results):
#    lhs=[tuple(result[2][0][0])[0] for result in results]
#    rhs=[tuple(result[2][0][1])[0] for result in results]
#    supports=[result[1] for result in results]
#    confidences=[result[2][0][2] for result in results]
#    lifts=[result[2][0][3] for result in results]

#    return list(zip(lhs,rhs,supports,confidences,lifts))
#result=pd.DataFrame(inspect(results),columns=['Left Hand Side','Right Hand Side','Support','Confidence','Lift'])
#result.sort_values(by='Lift',ascending=False)

#closed
r_c = fpgrowth(trans, target='c', supp=1)
df_c = pd.DataFrame(r_c)
df_c.columns = ['Itemset', 'Freq']
df_c

def support(x, labels, trans):
  s = []
  for t in range(len(trans)):
    if set(x).issubset(set(trans[t])):
      s.append(labels[t])
  return s

pd.set_option('display.max_colwidth', None)
labels = df1['BillNo'].unique()
df_c['Support'] = [support(x, labels, trans) for x in df_c['Itemset'].values]
print(labels)
df_c

import plotly.express as px

df_rf['Antecedent'] = df_rf['Antecedent'].apply(list)
df_rf['Consequent'] = df_rf['Consequent'].apply(list)

fig = px.scatter(df_rf, x="Freq", y="Conf", size="Lift",
                 color="Lift", hover_name="Consequent",
                 title='Market Basket Analysis - Support vs. Confidence',
                 labels={'Freq': 'Support', 'Conf': 'Confidence'})

fig.update_layout(
    xaxis_title='Support',
    yaxis_title='Confidence',
    coloraxis_colorbar_title='Lift',
    showlegend=True
)
fig.show()

import networkx as nx
import plotly.graph_objects as go

G = nx.DiGraph()

for idx, row in df_rf.iterrows():
    G.add_node(tuple(row['Antecedent']), color='skyblue')
    G.add_node(tuple(row['Consequent']), color='orange')
    G.add_edge(tuple(row['Antecedent']), tuple(row['Consequent']), weight=row['Freq'])

pos = nx.spring_layout(G)

edge_x = []
edge_y = []
for edge in G.edges(data=True):
    x0, y0 = pos[edge[0]]
    x1, y1 = pos[edge[1]]
    edge_x.append(x0)
    edge_x.append(x1)
    edge_x.append(None)
    edge_y.append(y0)
    edge_y.append(y1)
    edge_y.append(None)

edge_trace = go.Scatter(
    x=edge_x, y=edge_y,
    line=dict(width=0.5, color='#888'),
    hoverinfo='none',
    mode='lines')

node_x = []
node_y = []
for node in G.nodes():
    x, y = pos[node]
    node_x.append(x)
    node_y.append(y)

node_trace = go.Scatter(
    x=node_x, y=node_y,
    mode='markers',
    hoverinfo='text',
    marker=dict(
        showscale=True,
        colorscale='YlGnBu',
        size=10,
        colorbar=dict(
            thickness=15,
            title='Node Connections',
            xanchor='left',
            titleside='right'
        )
    )
)

layout = go.Layout(
    showlegend=False,
    hovermode='closest',
    margin=dict(b=0, l=0, r=0, t=0),
)

fig = go.Figure(data=[edge_trace, node_trace], layout=layout)

fig.show()

"""# **Emerging Patterns**"""

unique_items = df1['Country'].unique()
print('Países: ', len(unique_items))
print(unique_items)

grouped = df1.groupby('Country')
RowsPerCountry = grouped.size()

RowsPerCountry = RowsPerCountry.sort_values(ascending=False)

print("Number of rows per country:")
print(RowsPerCountry)

df_uk = df1[df1['Country'] == 'United Kingdom']
trans_uk = to_transactionnal(df_uk, 'BillNo', 'Itemname')
print(len(trans_uk))
df_uk

print(len(trans_uk))
trans_uk

"""# **Dataset for the rest**"""

df_siembra_not_uk = df1[df1['Country'] != 'United Kingdom']
trans_not_uk = to_transactionnal(df_siembra_not_uk, 'BillNo', 'Itemname')
print(len(trans_not_uk))
trans_not_uk

"""# **Mining Itemsets for both**"""

def all_itemsets(trans_, supp_, conf_):
  r = fpgrowth(trans_, target='r', supp=supp_, conf= conf_, report='scl')
  df_items = pd.DataFrame(r)
  df_items.columns = ['Consequent', 'Antecedent', 'Freq', 'Conf', 'Lift']
  df_items.sort_values(by='Lift', ascending=False, inplace=True)
  #df_items['Itemset'] = [str(sorted(x)) for x in df_items['Itemset'].values]
  return df_items

df_itemsets_uk = all_itemsets(trans_uk, 1, 50)
df_itemsets_not_uk = all_itemsets(trans_not_uk, 1, 50)

df_itemsets_uk

df_itemsets_not_uk

def all_itemsets2(trans_, supp_):

  r = fpgrowth(trans_, supp=supp_, report='aS')
  df_items = pd.DataFrame(r)
  df_items.columns = ['Itemset', 'Freq', 'Freq(%)']
  df_items['Size'] = [len(x) for x in df_items['Itemset'].values]
  df_items.sort_values(by='Freq', ascending=False, inplace=True)
  #df_items['Itemset'] = [str(sorted(x)) for x in df_items['Itemset'].values]
  return df_items

df_itemsets_uk2 = all_itemsets2(trans_uk, 1)
df_itemsets_not_uk2 = all_itemsets2(trans_not_uk, 1)

df_itemsets_uk2

df_itemsets_not_uk2

"""# **Emerging: UK vs The rest**"""

emerging_df = df_itemsets_uk2.join(df_itemsets_not_uk2.set_index('Itemset'),
                                     on='Itemset',
                                     lsuffix='_uk', rsuffix='_nuk',
                                     how='outer').fillna(0) #Se llenan con 0's dónde no estén presente nada
emerging_df['GrowthRate_uk'] = (emerging_df['Freq(%)_uk'] / emerging_df['Freq(%)_nuk'])
emerging_df.sort_values(by='GrowthRate_uk', ascending=False, inplace=True)
emerging_df

emerging_df[emerging_df['GrowthRate_uk'] < np.inf]

umbral = 2
em_df_c = emerging_df[emerging_df['GrowthRate_uk'] < np.inf]
em_df_c[em_df_c['GrowthRate_uk'] >= umbral]

"""# **JEP**"""

emerging_df[emerging_df['GrowthRate_uk'] == np.inf].sort_values(by='Freq_uk', ascending=False)

"""# **Emerging: The rest vs UK**"""

emerging_df['GrowthRate_nuk'] = (emerging_df['Freq(%)_nuk'] / emerging_df['Freq(%)_uk'])
emerging_df

emerging_df[emerging_df['GrowthRate_nuk'] < np.inf].sort_values(by='GrowthRate_nuk', ascending=False)

"""# **JEP**"""

emerging_df[emerging_df['GrowthRate_nuk'] == np.inf].sort_values(by='Freq_nuk', ascending=False)

"""# **SKYPATTERS**"""

!pip install paretoset

from paretoset import paretoset
import plotly.express as px

emerging_df

labels = df1['BillNo'].unique()
emerging_df['Precio'] = [support(x,labels, trans_uk) for x in emerging_df['Itemset'].values]
emerging_df

precio_promedio_por_factura = df1.groupby('BillNo')['TotalPrice'].mean().reset_index()
precio_promedio_por_factura.columns = ['BillNo', 'Precio_Prom']

factura_a_precio = dict(zip(precio_promedio_por_factura['BillNo'], precio_promedio_por_factura['Precio_Prom']))

def reemplazar_facturas_por_precios(facturas):
    precios = [factura_a_precio[factura] for factura in facturas if factura in factura_a_precio]
    if precios:
        return sum(precios) / len(precios)
    else:
        return None

def safe_eval(value):
    if isinstance(value, str):
        return eval(value)
    elif isinstance(value, list):
        return value
    else:
        return []

emerging_df['Precio'] = emerging_df['Precio'].apply(safe_eval)
emerging_df['Precio_Prom'] = emerging_df['Precio'].apply(reemplazar_facturas_por_precios)

emerging_df.drop(columns=['Precio'], inplace=True)

emerging_df

emerging_df

emerging_df['Itemset'] = emerging_df['Itemset'].apply(list)
emerging_df

emerging_df = emerging_df[['Itemset', 'Freq_uk', 'GrowthRate_uk', 'Size_uk', 'Precio_Prom']]
emerging_df

mask = paretoset(emerging_df[['Freq_uk', 'Size_uk', 'GrowthRate_uk', 'Precio_Prom']], sense=['max', 'max', 'max','min'])
sky_itemsets = emerging_df[mask]
print(len(sky_itemsets))
sky_itemsets

sky_itemsets['GrowthRate_uk'].values

import plotly.express as px

df_ = sky_itemsets[['Freq_uk', 'Size_uk', 'GrowthRate_uk', 'Precio_Prom']]
fig = px.parallel_coordinates(df_,
                              color='Precio_Prom',
                              labels=['Freq_uk', 'Size_uk', 'GrowthRate_uk', 'Precio_Prom'])
fig.show()

from sklearn.preprocessing import MinMaxScaler

for column in ['Freq_uk', 'GrowthRate_uk', 'Size_uk', 'Precio_Prom']:
    sky_itemsets[column].replace([np.inf, -np.inf], np.nan, inplace=True)
    max_finite_value = sky_itemsets[column].max()
    sky_itemsets[column].fillna(max_finite_value, inplace=True)

scaler = MinMaxScaler()
sky_itemsets[['Freq_uk', 'GrowthRate_uk', 'Size_uk', 'Precio_Prom']] = scaler.fit_transform(
    sky_itemsets[['Freq_uk', 'GrowthRate_uk', 'Size_uk', 'Precio_Prom']]
)

sky_itemsets.head()

import plotly.graph_objects as go


def radar_chart_all(df_, dimensions_):
    fig = go.Figure()
    for row_ in range(len(df_)):
        fig.add_trace(go.Scatterpolar(
            r=df_.iloc[row_, 1:].values,
            theta=dimensions_,
            fill='toself',
            name=str(df_.iloc[row_, 0])
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, df_.iloc[:, 1:].values.max()]
            )
        ),
        showlegend=True,
        legend=dict(
            font=dict(
                size=10
            )
        ),
        width=1500,
        height=1500
    )
    fig.show()

radar_chart_all(sky_itemsets.head(5), sky_itemsets.columns[1:])

radar_chart_all(sky_itemsets[sky_itemsets['GrowthRate_uk'] > 0.5], sky_itemsets.columns[1:])

radar_chart_all(sky_itemsets[(sky_itemsets['GrowthRate_uk'] > 0.5) & (sky_itemsets['GrowthRate_uk'] < 0.9)], sky_itemsets.columns[1:])