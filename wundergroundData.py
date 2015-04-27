#!/usr/bin/env python

##########                   Wunderground Data Downloader v-1.0               #################
# A python software to download data from wuderground website with a GUI interface
# It works on python 2.7, requires numpy, urllib2 and Tkinter modules
# The wunderground code database wgdb should be kept in the same directory
# The wgdb is adapted from pyhton module station-master written by Patrick Marsh <patrick.marsh@noaa.gov>

# written : Vineeth krishnan 
# date    : 31/03/2015  
# Email   : vineethpk@outlook.com   
#############################################################################################
import os ; import sys ; import datetime as dt ; import time ; import re ; 
from math import radians,cos; import calendar as cl ;from wgdb import wgdb ;

try:
   import numpy as np ; 
except:
   print "Couldn't find numpy, Please install "      
   quit()
try:   
   import urllib2 as urll2 ; 
except:
   print "Couldn't find urllib2, Please install"
   quit()
try:
   import Tkinter as tk ;
   from Tkinter import * ; from ttk import Style
   import tkMessageBox
except:
   print "Couldn't find Tkinter, Please install"
   quit()
##############################################################################################


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

def readInputs(S1,S2,S3,E1,E2,E3,LT,LO):
    sy=S1.get() ; sm=S2.get() ;sd=S3.get()   ; ey=E1.get() ; em=E2.get() ;ed=E3.get()
    lat=float(LT.get()); lon=float(LO.get()) ; sdte=sy+sm+sd ;edte=ey+em+ed;_point=(lon,lat); 
    _from_date=dt.datetime.strptime(sdte,'%Y%m%d') ; _to_date=dt.datetime.strptime(edte,'%Y%m%d')
    if _to_date < _from_date:
        tkMessageBox.showinfo("Hello Friend", "Date Entered is incorrect")
        return None
    if not -90 <= lat <= 90 :
        tkMessageBox.showinfo("Hello Friend", "Lattitude should be b/w -90 to 90")
        return None
    if not -180 <= lon <= 180 :
        tkMessageBox.showinfo("Hello Friend", "Longitude should be b/w -180 to 180")
        return None
    _lon_lat,_wnd_code=nearest_point(_point)  ;    
    data=downloadWndData(_from_date,_to_date,_wnd_code) 
    fnme=os.getcwd()+'/wunderground_data_'+str(lat)+'_'+str(lon)+'.csv'
    np.savetxt(fnme, data,fmt="%s",delimiter=",")
    tkMessageBox.showinfo("Hello Friend", "Download Completed")
    return None
def main():
    """ Gui interface """
    
    root=tk.Tk() ; 
    root.title("WDD")
    root.geometry("1068x748")
    root.resizable(width='False', height='False')

    topframe=tk.Frame(root,width=1024, height=150,bg="black",relief='flat')
    topframe.pack_propagate(False)
    topframe.pack(side="top", fill="both", expand=0, padx=4)

    var=StringVar()
    label1=Label(topframe,textvariable=var,bg='black',fg='white',relief='flat',font=('helivicta', 20)) 
    var.set("WUNDERGROUND DATA DOWNLOD")
    label1.place(x=260,y=55)

    f1=tk.LabelFrame(root,height=600,width=500,bg='red',bd=5,relief='flat',fg='orange')
    f1.place(x=4,y=151)

    f2=tk.LabelFrame(f1,height=200,width=400,bg='black',bd=5,relief='flat',text='DATE',fg='orange')
    f2.pack_propagate(False)
    f2.place(x=30,y=40)

    label2=tk.Label(f2,text="START-DATE",bg='black',fg='orange',relief='flat', font=('Arial', 12))
    label2.place(x=20, y=35, width=100, height=25) 

    label3=tk.Label(f2,text="END-DATE",bg='black',fg='orange',relief='flat',font=('Arial', 12))
    label3.place(x=20,y=95, width=100,height=25)

    y=tk.Label(f2,text='YYYY',fg='blue',font=('Arial', 10),bg='black')
    y.place(x=210,y=20)

    m=tk.Label(f2,text='MM',fg='blue',font=('Arial', 10),bg='black')
    m.place(x=250,y=20)

    d=tk.Label(f2,text='DD',fg='blue',font=('Arial', 10),bg='black')
    d.place(x=282,y=20)

    S1=tk.Entry(f2, width=4)
    S1.place(x=210,y=37)
    
    
    S2=tk.Entry(f2, width=3)
    S2.place(x=250,y=37)
    
    
    S3=tk.Entry(f2, width=3)
    S3.place(x=282,y=37)
    

    E1=tk.Entry(f2, width=4)
    E1.place(x=210,y=97)
   
    
    E2=tk.Entry(f2, width=3)
    E2.place(x=250,y=97)
    
    
    E3=tk.Entry(f2, width=3)
    E3.place(x=282,y=97)
    

    f3=tk.LabelFrame(f1,height=200,width=400,bg='black',bd=5,relief='flat',text='CO-ORDINATES(DEG-DECIMAL)',fg='orange')
    f3.pack_propagate(False)
    f3.place(x=30,y=290)

    label4=tk.Label(f3,text="LATTITUDE",bg='black',fg='orange',relief='flat', font=('Arial', 12))
    label4.place(x=20, y=35, width=100, height=25) 

    label5=tk.Label(f3,text="LONGITUDE",bg='black',fg='orange',relief='flat',font=('Arial', 12))
    label5.place(x=20,y=95, width=100,height=25)

    LT=tk.Entry(f3, width=6)
    LT.place(x=210,y=37)
    
       
    LO=tk.Entry(f3, width=6)
    LO.place(x=210,y=97)
    
    
    leftframe=tk.LabelFrame(root,height=598,width=1100,bg='pink',fg='red',relief='flat')
    leftframe.pack_propagate(False)
    leftframe.place(x=506,y=153)


    b=tk.Button(f1,text='submit',command= lambda: readInputs(S1,S2,S3,E1,E2,E3,LT,LO))
    b.place(x=200,y=500)
    
    q=tk.Button(f1,text='quit',command=root.destroy)
    q.place(x=300,y=500)
    root.mainloop()

if __name__=='__main__':
    main() 
    #quit()
 