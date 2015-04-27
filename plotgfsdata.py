import sys ; import numpy as np ; import scipy as sp ; import datetime ; import time
import matplotlib.pyplot as plt; from pylab import * ; from matplotlib import *
from mpl_toolkits.basemap import Basemap, cm, shiftgrid, maskoceans, interp, shapefile
import pygrib as pg ; from matplotlib.colors import from_levels_and_colors ;
from subprocess import call
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.axes3d import Axes3D
from matplotlib import animation
grb_f=pg.open('20150331/gfs.20150331.grb2')
#grb_f=pg.open('/home/Data/modelWRF/NMMV3.2.1/WPPV3/rrun/poutpost/2015040900/wrfpost2015040900')
   
grbmsgs=grb_f.read()[552::366] 
tmpmsgs = grb_f.select(name='Temperature',typeOfLevel='isobaricInhPa')

tmp=(np.array(grb_f.select(name="2 metre temperature")))
rf =(np.array(grb_f.select(name="Total Precipitation")))
u=(np.array(grb_f.select(name="10 metre U wind component")))
v=(np.array(grb_f.select(name="10 metre V wind component")))
lat, lon=tmp[1].latlons()

start_time = time.time()


temp=np.empty((0,lat.shape[1]))
rain=np.empty((0,lat.shape[1]))
uwnd=np.empty((0,lat.shape[1]))
vwnd=np.empty((0,lat.shape[1]))
for i in range(0,rf.shape[0]):
    temp=np.concatenate([temp,tmp[i].values-273.15],axis=0)
    rain=np.concatenate([rain,rf[i].values],axis=0)
    uwnd=np.concatenate([uwnd,u[i].values],axis=0)
    vwnd=np.concatenate([vwnd,v[i].values],axis=0)
temp=temp.reshape(rf.shape[0],lat.shape[0],lat.shape[1])
rain=rain.reshape(rf.shape[0],lat.shape[0],lat.shape[1])
uwnd=uwnd.reshape(rf.shape[0],lat.shape[0],lat.shape[1])
vwnd=vwnd.reshape(rf.shape[0],lat.shape[0],lat.shape[1])

print("--- %s seconds ---" % (time.time() - start_time))

""" Orthogonal Projection """
fig=plt.figure(figsize=(8,8),dpi=100); ax = fig.add_axes([0.1,0.1,0.8,0.8]) ; 
lat0=5 ; lon0=60
#m = Basemap(projection='ortho',lat_0=lat0,lon_0=lon0, resolution='c',area_thresh = 1000.) 
m = Basemap(projection='mill',llcrnrlat=-90,urcrnrlat=90,llcrnrlon=-180,urcrnrlon=180,resolution='l')
m = Basemap(projection='kav7',lon_0=0,resolution=None)

#m = Basemap(projection='ortho',lon_0=lon0,lat_0=lat0,resolution='l', \
       #            llcrnrx=0.,llcrnry=0.,urcrnrx=m1.urcrnrx/3,urcrnry=m1.urcrnry/3)

lons, data = m.shiftdata(lon, datain=temp[0,:,:], lon_0=None)
x, y=m(lons,lat)
Z=maskoceans(lons,lat,data,inlands=True, resolution='c', grid=2.5)
clevs=[-50,-40,-20,-10,0,5,10,15,20,25,30,35,40,45] ; cmap=plt.get_cmap('gist_rainbow')

#nice_cmap= plt.get_cmap('ocean_r')
#colors = nice_cmap([0,8, 16, 40, 60, 80,100,120,140]) 
#colors = nice_cmap([0,10,20,40,60,80,100,130,160]) 
#levels = [0, 5, 10, 15, 25,30,35,40] ; 
#cmap, norm = from_levels_and_colors(levels, colors, extend='both') 
#cs=m.pcolormesh(x,y,Z, cmap=cmap, norm=norm)

cs = (m.contourf(x,y,Z,clevs,cmap=plt.cm.jet))
#m.warpimage(image='venuscyl4.jpg')
#(m.readshapefile('ncfiles/subdiv/India_subdiv','ind',drawbounds=True, zorder=None, linewidth=1.0, color='k', antialiased=1, ax=None, default_encoding='utf-8'))
#(m.drawlsmask(land_color='grey',ocean_color='white',lakes=False))
#m.fillcontinents(color='white',lake_color='aqua')
(m.drawparallels(np.arange(-90,90.,45.), labels=[1,0,0,0])) 
(m.drawmeridians(np.arange(-180.,180.,60.), labels=[0,0,0,1]))
(m.drawmapboundary(fill_color='white')) 
(m.drawcoastlines(linewidth=0.25)) ; 
(m.drawcountries(linewidth=0.25));
(m.drawstates(linewidth=0.25)) 
cbar=(m.colorbar(cs,location='right', pad='5%')) ;
(cbar.set_label('degC')) ;# m.shaderelief() 
#m.arcgisimage(service='ESRI_Imagery_World_2D', xpixels = 1500, verbose= True)
(plt.title('Surface Temperature(degC)')); 
savefig('surfacetemp_globe.png', dpi=100);
plt.show()


""" SST """
fig=plt.figure(figsize=(8,8),dpi=100); ax = fig.add_axes([0.1,0.1,0.8,0.8]) ; 
lat0=5 ; lon0=60
m = Basemap(projection='ortho',lat_0=lat0,lon_0=lon0, resolution='c',area_thresh = 1000.) 
#m = Basemap(projection='mill',llcrnrlat=-90,urcrnrlat=90,llcrnrlon=-180,urcrnrlon=180,resolution='l')
#m = Basemap(projection='kav7',lon_0=0,resolution=None)
#m = Basemap(projection='ortho',lon_0=lon0,lat_0=lat0,resolution='l', \
       #            llcrnrx=0.,llcrnry=0.,urcrnrx=m1.urcrnrx/3,urcrnry=m1.urcrnry/3)

lons, data = m.shiftdata(lon, datain=temp[0,:,:], lon_0=None)
x, y=m(lons,lat)
Z=maskoceans(lons,lat,data,inlands=True, resolution='c', grid=2.5)
#clevs=[-50,-40,-20,-10,0,5,10,15,20,25,30,35,40,45] ; cmap=plt.get_cmap('hot_r')
clevs = [0, 5, 10, 15, 25,30,35,40] ;
#nice_cmap= plt.get_cmap('RdYlBu')
#colors = nice_cmap([0,8, 16, 40, 60, 80,100,120,140]) 
#colors = nice_cmap([0,10,20,40,60,80,100,130,160]) 
#levels = [0, 5, 10, 15, 25,30,35,40] ; 
#cmap, norm = from_levels_and_colors(levels, colors, extend='both') 
#cs=m.pcolormesh(x,y,data, cmap=cmap, norm=norm)

cs = (m.contourf(x,y,data,clevs,cmap=plt.cm.RdYlBu))
#m.warpimage(image='venuscyl4.jpg')
#(m.readshapefile('ncfiles/subdiv/India_subdiv','ind',drawbounds=True, zorder=None, linewidth=1.0, color='k', antialiased=1, ax=None, default_encoding='utf-8'))
(m.drawlsmask(land_color='grey',ocean_color='white',lakes=False))
m.fillcontinents(color='white',lake_color='white')
(m.drawparallels(np.arange(-90,90.,45.), labels=[1,0,0,0])) 
(m.drawmeridians(np.arange(-180.,180.,60.), labels=[0,0,0,1]))
(m.drawmapboundary(fill_color='white')) 
(m.drawcoastlines(linewidth=0.25)) ; 
(m.drawcountries(linewidth=0.25));
(m.drawstates(linewidth=0.25)) 
cbar=(m.colorbar(cs,location='right', pad='5%')) ;
(cbar.set_label('degC')) ;# m.shaderelief() 
#m.arcgisimage(service='ESRI_Imagery_World_2D', xpixels = 1500, verbose= True)
(plt.title('Sea Surface Temperature(degC)')); 
savefig('sst_globe.png', dpi=100);
plt.show()


""" rainfall """
fig=plt.figure(figsize=(8,8),dpi=100); ax = fig.add_axes([0.1,0.1,0.8,0.8]) ; 
lat0=5 ; lon0=60
#m = Basemap(projection='ortho',lat_0=lat0,lon_0=lon0, resolution='c',area_thresh = 1000.) 
m = Basemap(projection='mill',llcrnrlat=-90,urcrnrlat=90,llcrnrlon=-180,urcrnrlon=180,resolution='l')
#m = Basemap(projection='kav7',lon_0=0,resolution=None)

#m = Basemap(projection='ortho',lon_0=lon0,lat_0=lat0,resolution='l', \
       #            llcrnrx=0.,llcrnry=0.,urcrnrx=m1.urcrnrx/3,urcrnry=m1.urcrnry/3)

lons, data = m.shiftdata(lon, datain=rain[0:4,:,:].sum(axis=0), lon_0=None)


x, y=m(lons,lat)
Z=maskoceans(lons,lat,udata,inlands=True, resolution='c', grid=2.5)

clevs=[0,1,2.5,5,7.5,10,15,20,30,40,50,70,100,150,200,250,300,400,500,600,750]

cmap = cm.StepSeq
#cmap = cm.s3pcpn


#nice_cmap= plt.get_cmap('ocean_r')
#colors = nice_cmap([0,8, 16, 40, 60, 80,100,120,140]) 
#colors = nice_cmap([0,10,20,40,60,80,100,130,160]) 
#levels = [0, 5, 10, 15, 25,30,35,40] ; 
#cmap, norm = from_levels_and_colors(levels, colors, extend='both') 
#cs=m.pcolormesh(x,y,data, cmap=cmap, norm=norm)

cs = (m.contourf(x,y,data,clevs,cmap= cmap))
#m.warpimage(image='venuscyl4.jpg')
#(m.readshapefile('ncfiles/subdiv/India_subdiv','ind',drawbounds=True, zorder=None, linewidth=1.0, color='k', antialiased=1, ax=None, default_encoding='utf-8'))
#(m.drawlsmask(land_color='grey',ocean_color='white',lakes=False))
m.fillcontinents(color='white',lake_color='white')
(m.drawparallels(np.arange(-90,90.,45.), labels=[1,0,0,0])) 
(m.drawmeridians(np.arange(-180.,180.,60.), labels=[0,0,0,1]))
(m.drawmapboundary(fill_color='white')) 
(m.drawcoastlines(linewidth=0.25)) ; 
(m.drawcountries(linewidth=0.25));
(m.drawstates(linewidth=0.25)) 
cbar=(m.colorbar(cs,location='right', pad='5%')) ;
(cbar.set_label('mm')) ;# m.shaderelief() 
#m.arcgisimage(service='ESRI_Imagery_World_2D', xpixels = 1500, verbose= True)
(plt.title('Accumalated Precipitation')); 
savefig('Rainfall_globe.png', dpi=100);
plt.show()

