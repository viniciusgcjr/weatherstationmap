import folium
from folium.plugins import MarkerCluster
from glob import glob
from numpy import NaN
from pandas import to_numeric
from pandas import read_csv
import streamlit as st
from streamlit_folium import folium_static
 

stations = read_csv('inventario.csv', header=0, delimiter=',')
stations = stations.replace('#REF!', NaN)
stations = stations.replace('#N/D', NaN)

stations['LAT'] = to_numeric(stations['LAT'])
stations['LON'] = to_numeric(stations['LON'])
stations_without_nan = stations[stations['LAT'].notna()]

table = """
<!DOCTYPE html>
<html>
<head>
<style>
table {{
    width:100%;
    border-radius:10px;
}}
table, th, td {{
    border-collapse: collapse;
    
}}
th, td {{
    padding: 5px;
    text-align: left;
}}
#t01 tr:nth-child(odd) {{
    background-color:rgba(9, 0, 181, 0.2);
}}
#t01 tr:nth-child(even) {{
   background-color:rgba(186, 190, 204, 0.4);
}}
#t01 th {{
  background-color: #040054;
  color: white;
}}
table tr:hover td {{
  background-color: #ddd;
}}


<! -- Rounding borders of table -- >
table th:first-child {{
 border-radius: 5px 0 0 0;
}}
table th:last-child {{
  border-radius: 0 5px 0 0;
}}
table tr:last-child td:first-child {{
  border-radius: 0 0 0 5px;
}}
table tr:last-child td:last-child {{
  border-radius: 0 0 5px 0;
}}


</style>
</head>
<body>

<table id="t01">
  <tr>
    <th>{}</th>
    <th>{}</th>
  </tr>
  <tr>
    <td>{}</td>
    <td>{}</td>
  </tr>
  <tr>
    <td>{}</td>
    <td>{}</td>
  </tr>
  <tr>
    <td>{}</td>
    <td>{}</td>
  </tr>
  <tr>
    <td>{}</td>
    <td>{}</td>
  </tr>
  <tr>
    <td>{}</td>
    <td>{}</td>
  </tr>

</table>
</body>
</html>
""".format



st.set_page_config(page_title='Estações Apac', layout="centered", initial_sidebar_state='expanded')



#Base map
map = folium.Map(location=[-6.5, -37], zoom_start = 6, min_zoom=6)

#options of tiles
folium.TileLayer('openstreetmap').add_to(map)
folium.TileLayer('Stamen Terrain').add_to(map)
folium.TileLayer('cartodbdark_matter').add_to(map)

marker_cluster = MarkerCluster(name='Estações').add_to(map)

#Plot markers of the stations
for _, local in stations_without_nan.iterrows():
  iframe = folium.IFrame(table(
                        "ESTAÇÃO " , str(local['ESTAÇÃO']),
                        "ID " , str(local['Cód. IBGE/Apac']),    
                        "LATITUDE " , str(local['LAT']),
                        "LONGITUDE " , str(local['LON']),                      
                        "TIPO PCD " , str(local['TIPO PCD']), 
                        "TIPO COLETA " , str(local['TIPO COLETA'])
                               )
                          )

  popup = folium.Popup(iframe,
                     min_width=500,
                     max_width=750)

  pcd_icon = folium.features.CustomIcon('pcd_icon.jpg',
                                      icon_size=(50, 50))
                                      
  folium.Marker(location=[local['LAT'], local['LON']], 
                popup=popup, 
                icon=pcd_icon,
                tooltip='Clique para ver os detalhes').add_to(marker_cluster)

#Add style to regions
style_function = lambda x: {'fillColor': 'black', 'opacity':0.2, 'color':'black', 'weight':5, 'dashArray':'5, 5', 'fillOpacity':0.2}   #https://leafletjs.com/SlavaUkraini/reference.html#path-option

#add all regioes to map
files = glob('./mesoregioes_geojson/*.geojson')

for f in files:
  region = f.replace("\\", "/") #correction. Glob returns \ instead of /
  region_name = region.split('/')[-1].split('.')[0] #https://stackoverflow.com/questions/7336096/python-glob-without-the-whole-path-only-the-filename#answer-68415441
  layer = folium.GeoJson(region, control='true',   style_function=style_function, name=region_name)
  folium.GeoJsonTooltip(fields=["Regiao"]).add_to(layer)
  layer.add_to(map)
  
folium.LayerControl().add_to(map)
map
#map.save('testepy.html')

folium_static(map)
