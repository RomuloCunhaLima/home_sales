import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
import geopandas
import plotly.express as px
from datetime import datetime
import seaborn as sns

# definição de layout para ficar mais cumprido
st.set_page_config(layout='wide')
st.set_option('deprecation.showPyplotGlobalUse', False)
data=pd.read_csv('kc_house_data.csv')


st.title('Home Sales (Empresa ficticia) Compra e Venda de Imóveis usando tecnologia. ')


# ================================
# Data Overview
# =================================
# filtro em todas as  colunas
f_attributes = st.sidebar.multiselect('Enter columns', data.columns)
f_zipcode = st.sidebar.multiselect('Enter zipcode', data['zipcode'].unique())

st.title('Visão Geral dos dados')
df=data
if (f_zipcode != []) & (f_attributes != []):
    df = data.loc[data['zipcode'].isin(f_zipcode), f_attributes]

elif (f_zipcode != []) & (f_attributes == []):
    df = data.loc[data['zipcode'].isin(f_zipcode), :]

elif (f_zipcode == []) & (f_attributes != []):
    df = data.loc[:, f_attributes]

else:
    df = data.copy()

st.dataframe(df.head())
st.title('Fiz algumas hipóteses para otimizar a compra e venda de imóveis da empresa ')
c1,c2=st.beta_columns(( 1,1 ))

c1.header('H1: Imóveis que possuem vista para água, são 30% mais caros, na média')
df=data[['waterfront','price']].groupby('waterfront').median().reset_index()
sns.barplot(x='waterfront', y='price', data=df)
c1.pyplot()
c2.header('Quantidade de casas com vista para o mar')
sns.countplot(x='waterfront',data=data)
c2.pyplot()



st.header('RESPOSTA H1: O Fato da casa ter vista para o mar tem um impacto muito grande no valor da casa. A mediana de preço de casas com vista para o mar é 211.11% maior do que a que não tem vista para o mar')

st.header('RESPOSTA H2: Imóveis sem porão são 18.41% maior do que imoveis com porão')
st.header('H3: Imóveis com data de construção menor que 1955, são 50% mais baratos, na média.')
c1,c2=st.beta_columns(( 1,1 ))

df=data[['yr_built','price']].groupby('yr_built').median().reset_index()
sns.lineplot(x='yr_built',y='price',data=df)
c1.pyplot()

data['yr_u1955']=data['yr_built'].apply(lambda x: 'old' if x<1955 else 'new')
df= data[['yr_u1955','price']].groupby('yr_u1955').median().reset_index()
sns.barplot(x='yr_u1955', y='price', data=df)
c2.pyplot()

# definição de layout para ficar mais cumprido

st.header('RESPOSTA H3: No grafico de linhas é dificil ter uma conclusão sobre isso, mas no gráfico de barras verificamos que os valores são semelhantes, com uma diferença de apenas 2000')


c1,c2=st.beta_columns(( 1,1 ))
c1.header('Relação entre quantidade de banheiro e preço')
data['bathrooms'] = data['bathrooms'].round(0).astype(int)
banheiro=data[['bathrooms', 'price']].groupby('bathrooms').median().reset_index()
sns.barplot(x='bathrooms',y='price',data=banheiro)
c1.pyplot()

c2.header('Quantidade de casas por quantidade de banheiros')
sns.countplot(x='bathrooms',data=data)
c2.pyplot()
st.header('Quanto maior a quantiade de banheiros maior o preço das casas, mas não se tem uma quantidade relevante de casas com um numero de banheiros maior do que 3')
c1,c2=st.beta_columns(( 1,1 ))
data = data.drop(data[data['bedrooms'] == 33].index) # drop house with 33 bedooms

c1.header('Relação entre quantidade de quartos e preço')
df=data[['bedrooms', 'price']].groupby('bedrooms').median().reset_index()
dormitorio=df[['bedrooms', 'price']].groupby('bedrooms').mean().reset_index()
sns.barplot(x='bedrooms',y='price',data=dormitorio)
c1.pyplot()

c2.header('Relação entre quantidade de casas com certa quantidade de banheiros')
sns.countplot(x='bedrooms',data=data)
c2.pyplot()

st.header('A releção entre o número de quartos é semelhandte ao caso de banheiros, temos um crescimento positivo no numero de quartos em relação preço, mas a maioria das casas possuem entre 3 e 4 quartos')
c1,c2=st.beta_columns(( 1,1 ))
c1.header('H2: Imóveis sem porão tem a área do lote "sqrt_lot" 50% maiores do que com porão.')
data['porao']=data['sqft_basement'].apply(lambda x: 'tem_porao' if x>0 else 'nao_tem_porao')
df=data[['porao', 'sqft_lot']].groupby('porao').mean().reset_index()
sns.barplot(x='porao', y='sqft_lot', data=df)
c1.pyplot()

st.title('O proximo objetivo será Agrupar os imóveis por vendas em suas respectivas sazonalidades durante o periodo de 2014-05-02 e 2015-05-27:')
st.header('Verão: de junho a agosto')
st.header('Outono: de setembro a novembro')
st.header('Inverno: de dezembro a fevereiro')
st.header('Primavera: de março a maio')

data['date'] = pd.to_datetime( data['date'] ).dt.strftime( '%Y-%m-%d' )
data['sazonalidade']=data['date'].apply(lambda x: 'verao' if '2014-06-01' <=x< '2014-09-01' else 'outono' if '2014-09-01'<=x< '2014-12-01'
                                                   else 'inverno' if '2014-12-01'<=x< '2015-03-01' else 'primavera')
sazonalidade=data[['sazonalidade', 'price']].groupby('sazonalidade').median().reset_index()

sns.barplot(x='sazonalidade',y='price',data=sazonalidade)
st.pyplot()

st.header('A mediana dos valores das vendas na estação da primavera é 8.14% maior do que no inverno, então o ideal seria comprar no inverno e vender na primavera')


houses= data[['id','lat','long', 'price']].copy()
fig= px.scatter_mapbox(houses,lat='lat',lon='long',size='price', color_continuous_scale=px.colors.cyclical.IceFire,size_max=15, zoom=10)
fig.update_layout(mapbox_style='open-street-map')
fig.update_layout(height=600, margin={'r':0, 'l':0, 't':0, 'b':0}) # rigth, left, top, botom
st.pyplot()

df=data[['zipcode','price']].groupby('zipcode').median().reset_index()
df.columns=['zipcode','preco_mediana_regiao']
data_compra=pd.merge(df, data[['id', 'zipcode', 'price', 'waterfront']], how='left', on='zipcode')
data_compra['comprar'] = data_compra[['preco_mediana_regiao','price']].apply(lambda x: 'comprar' if int(x['preco_mediana_regiao'])< int(x['price']) else 'nao_comprar', axis=1)
st.dataframe(data_compra)


