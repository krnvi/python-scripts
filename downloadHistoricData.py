#!/usr/bin/env python

#################################################################################################################################################################

import os ; import sys ; import numpy as np ; import datetime as dt ;
import calendar as cl ; import time ; import urllib2 as urll2 ; import re ; 
from wgdb import wgdb ;from math import radians,cos 

def nearest_point(_point):
      _icao=wgdb()
      _earth_radius_m = 6371000 ;icao=_icao[:,0:2].astype(float) ; point=_point
      _dist_lon = np.radians(icao[:,0]) - radians(point[0]) 
      _dist_lat = np.radians(icao[:,1]) - radians(point[1])
      _a = np.square(np.sin(_dist_lat/2.0)) + cos(radians(point[1])) * np.cos(np.radians(icao[:,1])) * np.square(np.sin(_dist_lon/2.0))
      _c = 2 * np.arcsin(np.minimum(np.sqrt(_a), np.repeat(1, len(_a))))
      _dist = np.vstack(_earth_radius_m * _c) ;
      _min_indx=np.argmin(_dist) ;
           
      _near_lon_lat=np.concatenate([icao[_min_indx,:],(_dist[_min_indx]/1000)],axis=1) ; 
      _near_wnd_code=_icao[_min_indx,2]
      return _near_lon_lat,_near_wnd_code

def downloadWndData(_from_date,_to_date,_wnd_code):
  
      def readurl(url):
           web=urll2.Request(url) ;
           try:
                htm = urll2.urlopen(web) ; cont=re.sub('<br />','',htm.read()) ; 
                data=np.genfromtxt(cont.split('\n'),dtype='S',delimiter=',')
                if '' not in data[1:,1:]:
                    mxthd=data[0,1] ; mnthd=data[0,3]; 
                    if mxthd.endswith("F"):
                              maxtmp=data[1:,1].astype(float)  ; mintmp=data[1:,3].astype(float)
                              data[1:,1]=((maxtmp)-32) / 1.80  ; data[1:,3]=((mintmp)-32) / 1.80 ;
                              
                #np.savetxt('tmpFle', data,fmt="%s",delimiter=",") 
                header=data[:1,0:] ; data=data[1:,:]
           except urll2.HTTPError as e:
                url1=e.geturl() ; print "Error in Download :HTTPError",url1 ; readurl(url1)
                #raise Exception('Error opening %s: %s' % (e.geturl(), e))
                pass
           except urll2.URLError as e:
                print "Error in Download :URLError" ; readurl(url)
                #raise Exception('Error opening %s: %s' % (e.geturl(), e))
                pass
           except urll2.socket.error as e:
                print "Error in Download:Socket Error"; readurl(url)
           return header,data
            
      def dates_from_to(_from_date, _to_date):
                start_month = _from_date.month
                tot_months = (_to_date.year-_from_date.year)*12 + _to_date.month

                for month in range(start_month, tot_months + 1):
                      # Get years in the date range, add it to the start date's year
                      _yr = (month-1)/12 + _from_date.year
                      _mon = (month-1) % 12 + 1
                      #print _mon ; print _yr
                      _day=cl.monthrange(_yr,_mon)[1] ; 
                      yield dt.datetime(_yr, _mon, _day).strftime('%Y/%m/%d')     
                
      _dates=dates_from_to(_from_date,_to_date) ;
      data=np.empty((0,23))
      for _dte in _dates:
            #print _dte
            url="http://www.wunderground.com/history/airport/" + _wnd_code + "/" + _dte + "/MonthlyHistory.html?format=1" ;
            #print url
            header,data1=readurl(url)
            data=np.concatenate([data,data1],axis=0) ; 
      sp1=str(_from_date.year)+'-'+str(_from_date.month)+'-'+str(_from_date.day)
      sp2=str(_to_date.year)+'-'+str(_to_date.month)+'-'+str(_to_date.day) 
      ind1=np.array(np.where(data[:,0]==sp1)).T;ind2=(np.array(np.where(data[:,0]==sp2)).T)+1
      data=data[ind1:ind2,:]                  
      data=np.concatenate([header,data],axis=0)         
      return data

def main():
    _point=(77, 28) ;  sdte='20150201' ; edte='20150205'
    _lon_lat,_wnd_code=nearest_point(_point) ; #print _wnd_code ;
    _from_date=dt.datetime.strptime(sdte,'%Y%m%d') ; _to_date=dt.datetime.strptime(edte,'%Y%m%d') ;#_wnd_code='VIDP'
    data=downloadWndData(_from_date,_to_date,_wnd_code)
    np.savetxt('tmpFle.csv', data,fmt="%s",delimiter=",")
       
if __name__=='__main__':
   main() 
   #quit()

