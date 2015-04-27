#!/usr/bin/env python
import os ; import sys ; import numpy as np ; import datetime as dt ; import csv ; import time ;import calendar as cl
from dateutil import rrule ; import calendar as cl ; import time ; import urllib2 as urll2 ; import re ; 

_from_date='20150202' ;_to_date='20150228' ; fcs_ldays=15 ;

fcs_from_date=dt.datetime.strptime(_from_date,'%Y%m%d') ; fcs_to_date=dt.datetime.strptime(_to_date,'%Y%m%d') ;

obs_from_date=(dt.datetime.strptime(_from_date,"%Y%m%d")+dt.timedelta(days=7)) #.strftime('%Y%m%d') ; 
obs_to_date  =(dt.datetime.strptime(_to_date,"%Y%m%d")+dt.timedelta(days=fcs_ldays)) #.strftime('%Y%m%d') ;

no_obs_days=(obs_to_date-obs_from_date).days+1
no_fcs_days=(fcs_to_date-fcs_from_date).days+1

obs_date_list=[x for x in rrule.rrule(rrule.HOURLY,dtstart=obs_from_date,until=obs_to_date)]
del obs_date_list[-1]

nat_id=np.genfromtxt("/home/OldData/IntCor/pradan/national_obsdata.lst",delimiter=',',dtype="S")
nat_idd=nat_id[nat_id[:,2].argsort(kind='mergesort')]


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
########## model fcst from file ############################################# 
mod_fcst=np.empty((0,33))
for date in rrule.rrule(rrule.DAILY,dtstart=fcs_from_date,until=fcs_to_date):
         date=date.strftime('%Y%m%d')
         modFle="/home/OldData/gefsData/24hourlyoutput/"+date+"/24hourlygefscorrected"+date+".csv" ; 
                 
         mod_fcst1=np.genfromtxt(modFle, delimiter=',', dtype="S");
         #mod_fcst1 = mod_fcst1[np.argsort(mod_fcst1[:,2],kind='mergesort')]
         mod_fcst1 = mod_fcst1[mod_fcst1[:,0].argsort(kind='mergesort')]
         mod_fcst=np.concatenate([mod_fcst,np.squeeze(mod_fcst1[np.array(np.where(np.in1d(mod_fcst1[:,0],nat_idd[:,2]))).T],axis=None)],axis=0)

mod_reqData=mod_fcst[mod_fcst[:,0].argsort(kind='mergesort')]
mod_Data=np.concatenate([mod_reqData[:,0:7],mod_reqData[:,8:10]],axis=1)     
sh_ftr0=nat_idd.shape[0] ; sh_ftr1=mod_Data.shape[0]/nat_idd.shape[0] ; sh_ftr2=mod_Data.shape[1] ;
mod_data=mod_Data.reshape(sh_ftr0,sh_ftr1,sh_ftr2) 
#mod_data=np.delete(mod_data,range(0,sh_ftr1,fcs_ldays),axis=1)
mod=mod_data[mod_data[:,0,0].argsort(kind='mergesort')]

######### obs data from data base ############################################# 
obs_Data=np.empty((0,7))
for nme,wnd,tid in nat_idd[:,:]:
    obs_dat=downloadWndData(obs_from_date,obs_to_date,wnd) 
    if obs_dat.shape[0] !=(no_obs_days+1) :   
       if obs_data.size == 0:
           data=np.empty((no_obs_days,6))
           data[:]=np.NAN
       else:
           dates=[dt.datetime.strptime(x,'%Y-%m-%d') for x in obs_dat[1:,0]]
           date_set = set(dates[0]+dt.timedelta(days=x) for x in range(int((dates[-1]-dates[0]).total_seconds()/60/60/24)+1))    
           mis_date = np.array([x.strftime('%Y-%m-%-d') for x in sorted(date_set-set(dates))]) 
           indx_misdate=np.array(np.nonzero(([x.days>1 for x in np.diff(dates)]))) +2       
           fil_data=np.empty((mis_date.shape[0],obs_dat.shape[1]))
           fil_data[:]=np.NAN ;fil_data=fil_data.astype(str)  ; fil_data[:,0]=mis_date
           #fil_data=fil_data.astype(str)  ; fil_data[:,0]=mis_date
           data=np.concatenate([obs_dat[0:indx_misdate,:],fil_data,obs_dat[indx_misdate:,:]])
    else:
       data=np.concatenate([obs_dat[1:,0:2],np.vstack([obs_dat[1:,3],obs_dat[1:,7],obs_dat[1:,9],obs_dat[1:,19]]).T],axis=1) 
       if '' in data:       
          fil_data=np.empty((data.shape[0],data.shape[1]-1))
          fil_data[:]=np.NAN ;fil_data=fil_data.astype(str)  ;
          data=np.concatenate([np.vstack(data[:,0]),fil_data],axis=1)
   
   
 
#    no_rws=data.shape[0]/no_obs_days ;no_clns=data.shape[1]
#    data=data.reshape(no_obs_days,no_rws,no_clns)
    I=((np.ones((data.shape[0],1))*[int(tid)]).astype(int)).astype(str) 
    D=np.concatenate([I,data],axis=1)
    obs_Data=np.concatenate([obs_Data,D],axis=0) ;
    
obs_data=obs_Data.reshape(nat_idd.shape[0],no_obs_days,obs_Data.shape[1])
obs_data=obs_data[obs_data[:,0,0].argsort(kind='mergesort')] 
obs=np.empty((nat_idd.shape[0],0,obs_data.shape[2]))
for i in range(0,mod.shape[1]/9):
    S=obs_data[:,i:i+9,:]
    obs=np.concatenate([obs,S],axis=1) 
    
diff=np.round(np.abs(mod[:,:,3:7].astype(float)-obs[:,:,2:6].astype(float))).astype(int)
diff=np.concatenate([mod[:,:,0:3],diff[:,:,:]],axis=2)
diff1=(np.ma.masked_where(diff==-9223372036854775808,diff)) 

diff_day1=diff[:,0::9,:]  
diff_day2=diff[:,1::9,:]
diff_day3=diff[:,2::9,:]
diff_day4=diff[:,3::9,:]
diff_day5=diff[:,4::9,:]
diff_day6=diff[:,5::9,:]
diff_day7=diff[:,6::9,:]
diff_day8=diff[:,7::9,:]
diff_day9=diff[:,8::9,:]

rmse_day1=np.concatenate([np.vstack(diff_day1[:,0,0]),np.round(np.sqrt(np.square(diff_day1[:,:,3:].astype(int)).mean(axis=1))).astype(int)],axis=1) 
rmse_day2=np.concatenate([np.vstack(diff_day2[:,0,0]),np.round(np.sqrt(np.square(diff_day2[:,:,3:].astype(int)).mean(axis=1))).astype(int)],axis=1) 
rmse_day3=np.concatenate([np.vstack(diff_day3[:,0,0]),np.round(np.sqrt(np.square(diff_day3[:,:,3:].astype(int)).mean(axis=1))).astype(int)],axis=1) 
rmse_day4=np.concatenate([np.vstack(diff_day4[:,0,0]),np.round(np.sqrt(np.square(diff_day4[:,:,3:].astype(int)).mean(axis=1))).astype(int)],axis=1) 
rmse_day5=np.concatenate([np.vstack(diff_day5[:,0,0]),np.round(np.sqrt(np.square(diff_day5[:,:,3:].astype(int)).mean(axis=1))).astype(int)],axis=1) 
rmse_day6=np.concatenate([np.vstack(diff_day6[:,0,0]),np.round(np.sqrt(np.square(diff_day6[:,:,3:].astype(int)).mean(axis=1))).astype(int)],axis=1) 
rmse_day7=np.concatenate([np.vstack(diff_day7[:,0,0]),np.round(np.sqrt(np.square(diff_day7[:,:,3:].astype(int)).mean(axis=1))).astype(int)],axis=1) 
rmse_day8=np.concatenate([np.vstack(diff_day8[:,0,0]),np.round(np.sqrt(np.square(diff_day8[:,:,3:].astype(int)).mean(axis=1))).astype(int)],axis=1) 
rmse_day9=np.concatenate([np.vstack(diff_day9[:,0,0]),np.round(np.sqrt(np.square(diff_day9[:,:,3:].astype(int)).mean(axis=1))).astype(int)],axis=1) 


#corc_day1=np.corrcoef(mod[0,0:218:7,3:8].astype(int),obs[0,0:218:7,2:7].astype(int),rowvar=0)





#b=pearsonr(A[0,:,0:5],B[0,:,0:5])



''' temperatue '''

tpcnt_day1=np.concatenate([np.vstack(diff_day1[:,0,0]),np.concatenate([np.round((((diff_day1[:,:,3:5].astype(int) <=1).sum(axis=1)).astype(float)/diff_day1.shape[1])*100).astype(int), \
            np.round((((diff_day1[:,:,3:5].astype(int) >1) & ( diff_day1[:,:,3:5].astype(int)  <=2 )).sum(axis=1)).astype(float)/diff_day1.shape[1]*100).astype(int), \
            np.round((((diff_day1[:,:,3:5].astype(int) >2) & ( diff_day1[:,:,3:5].astype(int)  <=3 )).sum(axis=1)).astype(float)/diff_day1.shape[1]*100).astype(int), \
            np.round((((diff_day1[:,:,3:5].astype(int) >3)).sum(axis=1)).astype(float)/diff_day1.shape[1]*100).astype(int)],axis=1)],axis=1) 

tpcnt_day2=np.concatenate([np.vstack(diff_day2[:,0,0]),np.concatenate([np.round((((diff_day2[:,:,3:5].astype(int) <=1).sum(axis=1)).astype(float)/diff_day2.shape[1])*100).astype(int), \
            np.round((((diff_day2[:,:,3:5].astype(int) >1) & ( diff_day2[:,:,3:5].astype(int)  <=2 )).sum(axis=1)).astype(float)/diff_day2.shape[1]*100).astype(int), \
            np.round((((diff_day2[:,:,3:5].astype(int) >2) & ( diff_day2[:,:,3:5].astype(int)  <=3 )).sum(axis=1)).astype(float)/diff_day2.shape[1]*100).astype(int), \
            np.round((((diff_day2[:,:,3:5].astype(int) >3)).sum(axis=1)).astype(float)/diff_day2.shape[1]*100).astype(int)],axis=1)],axis=1)
            
tpcnt_day3=np.concatenate([np.vstack(diff_day3[:,0,0]),np.concatenate([np.round((((diff_day3[:,:,3:5].astype(int) <=1).sum(axis=1)).astype(float)/diff_day3.shape[1])*100).astype(int), \
            np.round((((diff_day3[:,:,3:5].astype(int) >1) & ( diff_day3[:,:,3:5].astype(int)  <=2 )).sum(axis=1)).astype(float)/diff_day3.shape[1]*100).astype(int), \
            np.round((((diff_day3[:,:,3:5].astype(int) >2) & ( diff_day3[:,:,3:5].astype(int)  <=3 )).sum(axis=1)).astype(float)/diff_day3.shape[1]*100).astype(int), \
            np.round((((diff_day3[:,:,3:5].astype(int) >3)).sum(axis=1)).astype(float)/diff_day3.shape[1]*100).astype(int)],axis=1)],axis=1)
            
            
tpcnt_day4=np.concatenate([np.vstack(diff_day4[:,0,0]),np.concatenate([np.round((((diff_day4[:,:,3:5].astype(int) <=1).sum(axis=1)).astype(float)/diff_day4.shape[1])*100).astype(int), \
            np.round((((diff_day4[:,:,3:5].astype(int) >1) & ( diff_day4[:,:,3:5].astype(int)  <=2 )).sum(axis=1)).astype(float)/diff_day4.shape[1]*100).astype(int), \
            np.round((((diff_day4[:,:,3:5].astype(int) >2) & ( diff_day4[:,:,3:5].astype(int)  <=3 )).sum(axis=1)).astype(float)/diff_day4.shape[1]*100).astype(int), \
            np.round((((diff_day4[:,:,3:5].astype(int) >3)).sum(axis=1)).astype(float)/diff_day4.shape[1]*100).astype(int)],axis=1)],axis=1)

tpcnt_day5=np.concatenate([np.vstack(diff_day5[:,0,0]),np.concatenate([np.round((((diff_day5[:,:,3:5].astype(int) <=1).sum(axis=1)).astype(float)/diff_day5.shape[1])*100).astype(int), \
            np.round((((diff_day5[:,:,3:5].astype(int) >1) & ( diff_day5[:,:,3:5].astype(int)  <=2 )).sum(axis=1)).astype(float)/diff_day5.shape[1]*100).astype(int), \
            np.round((((diff_day5[:,:,3:5].astype(int) >2) & ( diff_day5[:,:,3:5].astype(int)  <=3 )).sum(axis=1)).astype(float)/diff_day5.shape[1]*100).astype(int), \
            np.round((((diff_day5[:,:,3:5].astype(int) >3)).sum(axis=1)).astype(float)/diff_day5.shape[1]*100).astype(int)],axis=1)],axis=1)

tpcnt_day6=np.concatenate([np.vstack(diff_day6[:,0,0]),np.concatenate([np.round((((diff_day6[:,:,3:5].astype(int) <=1).sum(axis=1)).astype(float)/diff_day6.shape[1])*100).astype(int), \
            np.round((((diff_day6[:,:,3:5].astype(int) >1) & ( diff_day6[:,:,3:5].astype(int)  <=2 )).sum(axis=1)).astype(float)/diff_day6.shape[1]*100).astype(int), \
            np.round((((diff_day6[:,:,3:5].astype(int) >2) & ( diff_day6[:,:,3:5].astype(int)  <=3 )).sum(axis=1)).astype(float)/diff_day6.shape[1]*100).astype(int), \
            np.round((((diff_day6[:,:,3:5].astype(int) >3)).sum(axis=1)).astype(float)/diff_day6.shape[1]*100).astype(int)],axis=1)],axis=1)

tpcnt_day7=np.concatenate([np.vstack(diff_day7[:,0,0]),np.concatenate([np.round((((diff_day7[:,:,3:5].astype(int) <=1).sum(axis=1)).astype(float)/diff_day7.shape[1])*100).astype(int), \
            np.round((((diff_day7[:,:,3:5].astype(int) >1) & ( diff_day7[:,:,3:5].astype(int)  <=2 )).sum(axis=1)).astype(float)/diff_day7.shape[1]*100).astype(int), \
            np.round((((diff_day7[:,:,3:5].astype(int) >2) & ( diff_day7[:,:,3:5].astype(int)  <=3 )).sum(axis=1)).astype(float)/diff_day7.shape[1]*100).astype(int), \
            np.round((((diff_day7[:,:,3:5].astype(int) >3)).sum(axis=1)).astype(float)/diff_day7.shape[1]*100).astype(int)],axis=1)],axis=1)

tpcnt_day8=np.concatenate([np.vstack(diff_day8[:,0,0]),np.concatenate([np.round((((diff_day8[:,:,3:5].astype(int) <=1).sum(axis=1)).astype(float)/diff_day8.shape[1])*100).astype(int), \
            np.round((((diff_day8[:,:,3:5].astype(int) >1) & ( diff_day8[:,:,3:5].astype(int)  <=2 )).sum(axis=1)).astype(float)/diff_day8.shape[1]*100).astype(int), \
            np.round((((diff_day8[:,:,3:5].astype(int) >2) & ( diff_day8[:,:,3:5].astype(int)  <=3 )).sum(axis=1)).astype(float)/diff_day8.shape[1]*100).astype(int), \
            np.round((((diff_day8[:,:,3:5].astype(int) >3)).sum(axis=1)).astype(float)/diff_day8.shape[1]*100).astype(int)],axis=1)],axis=1)
            
tpcnt_day9=np.concatenate([np.vstack(diff_day9[:,0,0]),np.concatenate([np.round((((diff_day9[:,:,3:5].astype(int) <=1).sum(axis=1)).astype(float)/diff_day9.shape[1])*100).astype(int), \
            np.round((((diff_day9[:,:,3:5].astype(int) >1) & ( diff_day9[:,:,3:5].astype(int)  <=2 )).sum(axis=1)).astype(float)/diff_day9.shape[1]*100).astype(int), \
            np.round((((diff_day9[:,:,3:5].astype(int) >2) & ( diff_day9[:,:,3:5].astype(int)  <=3 )).sum(axis=1)).astype(float)/diff_day9.shape[1]*100).astype(int), \
            np.round((((diff_day9[:,:,3:5].astype(int) >3)).sum(axis=1)).astype(float)/diff_day9.shape[1]*100).astype(int)],axis=1)],axis=1)


locs=(nat_idd[np.array(np.where(np.in1d(tpcnt_day1[:,0],nat_idd[:,2]))).T,0])

maxt=np.concatenate([locs,np.vstack(tpcnt_day1[:,0]),tpcnt_day1[:,1::2],tpcnt_day2[:,1::2],tpcnt_day3[:,1::2],tpcnt_day4[:,1::2],tpcnt_day5[:,1::2],tpcnt_day6[:,1::2],tpcnt_day7[:,1::2],tpcnt_day8[:,1::2],tpcnt_day9[:,1::2]],axis=1)
maxt=maxt[maxt[:,0].argsort(kind='mergesort')] ; 
mint=np.concatenate([locs,np.vstack(tpcnt_day1[:,0]),tpcnt_day1[:,2::2],tpcnt_day2[:,2::2],tpcnt_day3[:,2::2],tpcnt_day4[:,2::2],tpcnt_day5[:,2::2],tpcnt_day6[:,2::2],tpcnt_day7[:,2::2],tpcnt_day8[:,2::2],tpcnt_day9[:,2::2]],axis=1)
mint=mint[mint[:,0].argsort(kind='mergesort')] ;
temp=np.concatenate([maxt,mint],axis=0) ;
            
''' Relative Humidity & wind speed '''
C_r=np.zeros((nat_idd.shape[0],9)).astype(int)

rhwscnt_day1=np.concatenate([np.vstack(diff_day1[:,0,0]),np.concatenate([np.round((((diff_day1[:,:,5:].astype(int) <=10).sum(axis=1)).astype(float)/diff_day1.shape[1])*100).astype(int), \
            np.round((((diff_day1[:,:,5:].astype(int) >10) & ( diff_day1[:,:,5:].astype(int)  <=20 )).sum(axis=1)).astype(float)/diff_day1.shape[1]*100).astype(int), \
            np.round((((diff_day1[:,:,5:].astype(int) >20)).sum(axis=1)).astype(float)/diff_day1.shape[1]*100).astype(int)],axis=1)],axis=1) 
            
rhwscnt_day2=np.concatenate([np.vstack(diff_day2[:,0,0]),np.concatenate([np.round((((diff_day2[:,:,5:].astype(int) <=10).sum(axis=1)).astype(float)/diff_day2.shape[1])*100).astype(int), \
            np.round((((diff_day2[:,:,5:].astype(int) >10) & ( diff_day2[:,:,5:].astype(int)  <=20 )).sum(axis=1)).astype(float)/diff_day2.shape[1]*100).astype(int), \
            np.round((((diff_day2[:,:,5:].astype(int) >20)).sum(axis=1)).astype(float)/diff_day2.shape[1]*100).astype(int)],axis=1)],axis=1) 
            
rhwscnt_day3=np.concatenate([np.vstack(diff_day3[:,0,0]),np.concatenate([np.round((((diff_day3[:,:,5:].astype(int) <=10).sum(axis=1)).astype(float)/diff_day3.shape[1])*100).astype(int), \
            np.round((((diff_day3[:,:,5:].astype(int) >10) & ( diff_day3[:,:,5:].astype(int)  <=20 )).sum(axis=1)).astype(float)/diff_day3.shape[1]*100).astype(int), \
            np.round((((diff_day3[:,:,5:].astype(int) >20)).sum(axis=1)).astype(float)/diff_day3.shape[1]*100).astype(int)],axis=1)],axis=1) 
            
rhwscnt_day4=np.concatenate([np.vstack(diff_day4[:,0,0]),np.concatenate([np.round((((diff_day4[:,:,5:].astype(int) <=10).sum(axis=1)).astype(float)/diff_day4.shape[1])*100).astype(int), \
            np.round((((diff_day4[:,:,5:].astype(int) >10) & ( diff_day4[:,:,5:].astype(int)  <=20 )).sum(axis=1)).astype(float)/diff_day4.shape[1]*100).astype(int), \
            np.round((((diff_day4[:,:,5:].astype(int) >20)).sum(axis=1)).astype(float)/diff_day4.shape[1]*100).astype(int)],axis=1)],axis=1) 
            
rhwscnt_day5=np.concatenate([np.vstack(diff_day3[:,0,0]),np.concatenate([np.round((((diff_day3[:,:,5:].astype(int) <=10).sum(axis=1)).astype(float)/diff_day3.shape[1])*100).astype(int), \
            np.round((((diff_day3[:,:,5:].astype(int) >10) & ( diff_day3[:,:,5:].astype(int)  <=20 )).sum(axis=1)).astype(float)/diff_day3.shape[1]*100).astype(int), \
            np.round((((diff_day3[:,:,5:].astype(int) >20)).sum(axis=1)).astype(float)/diff_day3.shape[1]*100).astype(int)],axis=1)],axis=1)             
            
rhwscnt_day6=np.concatenate([np.vstack(diff_day6[:,0,0]),np.concatenate([np.round((((diff_day6[:,:,5:].astype(int) <=10).sum(axis=1)).astype(float)/diff_day6.shape[1])*100).astype(int), \
            np.round((((diff_day6[:,:,5:].astype(int) >10) & ( diff_day6[:,:,5:].astype(int)  <=20 )).sum(axis=1)).astype(float)/diff_day6.shape[1]*100).astype(int), \
            np.round((((diff_day6[:,:,5:].astype(int) >20)).sum(axis=1)).astype(float)/diff_day6.shape[1]*100).astype(int)],axis=1)],axis=1) 
            
rhwscnt_day7=np.concatenate([np.vstack(diff_day7[:,0,0]),np.concatenate([np.round((((diff_day7[:,:,5:].astype(int) <=10).sum(axis=1)).astype(float)/diff_day7.shape[1])*100).astype(int), \
            np.round((((diff_day7[:,:,5:].astype(int) >10) & ( diff_day7[:,:,5:].astype(int)  <=20 )).sum(axis=1)).astype(float)/diff_day7.shape[1]*100).astype(int), \
            np.round((((diff_day7[:,:,5:].astype(int) >20)).sum(axis=1)).astype(float)/diff_day7.shape[1]*100).astype(int)],axis=1)],axis=1)

rhwscnt_day8=np.concatenate([np.vstack(diff_day8[:,0,0]),np.concatenate([np.round((((diff_day8[:,:,5:].astype(int) <=10).sum(axis=1)).astype(float)/diff_day8.shape[1])*100).astype(int), \
            np.round((((diff_day8[:,:,5:].astype(int) >10) & ( diff_day8[:,:,5:].astype(int)  <=20 )).sum(axis=1)).astype(float)/diff_day8.shape[1]*100).astype(int), \
            np.round((((diff_day8[:,:,5:].astype(int) >20)).sum(axis=1)).astype(float)/diff_day8.shape[1]*100).astype(int)],axis=1)],axis=1)

rhwscnt_day9=np.concatenate([np.vstack(diff_day9[:,0,0]),np.concatenate([np.round((((diff_day9[:,:,5:].astype(int) <=10).sum(axis=1)).astype(float)/diff_day9.shape[1])*100).astype(int), \
            np.round((((diff_day9[:,:,5:].astype(int) >10) & ( diff_day9[:,:,5:].astype(int)  <=20 )).sum(axis=1)).astype(float)/diff_day9.shape[1]*100).astype(int), \
            np.round((((diff_day9[:,:,5:].astype(int) >20)).sum(axis=1)).astype(float)/diff_day9.shape[1]*100).astype(int)],axis=1)],axis=1)            

maxrh=np.concatenate([locs,np.vstack(rhwscnt_day1[:,0]),rhwscnt_day1[:,1::2],rhwscnt_day2[:,1::2],rhwscnt_day3[:,1::2],rhwscnt_day4[:,1::2],rhwscnt_day5[:,1::2],rhwscnt_day6[:,1::2],rhwscnt_day7[:,1::2],rhwscnt_day8[:,1::2],rhwscnt_day9[:,1::2],C_r],axis=1)
maxrh=maxrh[maxrh[:,0].argsort(kind='mergesort')] ;
minrh=np.concatenate([locs,np.vstack(rhwscnt_day1[:,0]),rhwscnt_day1[:,2::2],rhwscnt_day2[:,2::2],rhwscnt_day3[:,2::2],rhwscnt_day4[:,2::2],rhwscnt_day5[:,2::2],rhwscnt_day6[:,2::2],rhwscnt_day7[:,2::2],rhwscnt_day8[:,2::2],rhwscnt_day9[:,2::2],C_r],axis=1)
minrh=minrh[minrh[:,0].argsort(kind='mergesort')] ;
#maxws=np.concatenate([locs,np.vstack(rhwscnt_day1[:,0]),rhwscnt_day1[:,3::3],rhwscnt_day2[:,3::3],rhwscnt_day3[:,3::3],rhwscnt_day4[:,3::3],rhwscnt_day5[:,3::3],rhwscnt_day6[:,3::3],rhwscnt_day7[:,3::3],rhwscnt_day8[:,3::3],rhwscnt_day9[:,3::3],C_r],axis=1)
#maxws=maxws[maxws[:,0].argsort(kind='mergesort')] ;
rhws=np.concatenate([maxrh,minrh],axis=0)            


''' Rainfall '''

rf_day1=np.concatenate([mod[:,0::9,0:3],mod[:,0::9,8].reshape(nat_idd.shape[0],no_fcs_days,1),obs[:,0::9,0:2],obs[:,0::9,6].reshape(nat_idd.shape[0],no_fcs_days,1)],axis=2)  
rf_day2=np.concatenate([mod[:,1::9,0:3],mod[:,1::9,8].reshape(nat_idd.shape[0],no_fcs_days,1),obs[:,1::9,0:2],obs[:,1::9,6].reshape(nat_idd.shape[0],no_fcs_days,1)],axis=2)  
rf_day3=np.concatenate([mod[:,2::9,0:3],mod[:,2::9,8].reshape(nat_idd.shape[0],no_fcs_days,1),obs[:,2::9,0:2],obs[:,2::9,6].reshape(nat_idd.shape[0],no_fcs_days,1)],axis=2)  
rf_day4=np.concatenate([mod[:,3::9,0:3],mod[:,3::9,8].reshape(nat_idd.shape[0],no_fcs_days,1),obs[:,3::9,0:2],obs[:,3::9,6].reshape(nat_idd.shape[0],no_fcs_days,1)],axis=2)  
rf_day5=np.concatenate([mod[:,4::9,0:3],mod[:,4::9,8].reshape(nat_idd.shape[0],no_fcs_days,1),obs[:,4::9,0:2],obs[:,4::9,6].reshape(nat_idd.shape[0],no_fcs_days,1)],axis=2)  
rf_day6=np.concatenate([mod[:,5::9,0:3],mod[:,5::9,8].reshape(nat_idd.shape[0],no_fcs_days,1),obs[:,5::9,0:2],obs[:,5::9,6].reshape(nat_idd.shape[0],no_fcs_days,1)],axis=2)  
rf_day7=np.concatenate([mod[:,6::9,0:3],mod[:,6::9,8].reshape(nat_idd.shape[0],no_fcs_days,1),obs[:,6::9,0:2],obs[:,6::9,6].reshape(nat_idd.shape[0],no_fcs_days,1)],axis=2)  
rf_day8=np.concatenate([mod[:,7::9,0:3],mod[:,7::9,8].reshape(nat_idd.shape[0],no_fcs_days,1),obs[:,7::9,0:2],obs[:,7::9,6].reshape(nat_idd.shape[0],no_fcs_days,1)],axis=2)  
rf_day9=np.concatenate([mod[:,8::9,0:3],mod[:,8::9,8].reshape(nat_idd.shape[0],no_fcs_days,1),obs[:,8::9,0:2],obs[:,8::9,6].reshape(nat_idd.shape[0],no_fcs_days,1)],axis=2)  

rfcnt_day1=np.concatenate([np.vstack([rf_day1[:,0,0],np.round((((((rf_day1[:,:,3].astype(int) ==0) & (rf_day1[:,:,6].astype(float) ==0 )) | ((rf_day1[:,:,3].astype(int) >0) & (rf_day1[:,:,6].astype(float) >0))).sum(axis=1)).astype(float)/rf_day1.shape[1])*100).astype(int), \
                          np.round(((((rf_day1[:,:,3].astype(int) <=0) & (rf_day1[:,:,6].astype(float) >0)).sum(axis=1)).astype(float)/rf_day1.shape[1])*100).astype(int), \
                          np.round(((((rf_day1[:,:,3].astype(int) >0) & (rf_day1[:,:,6].astype(float) <=0)).sum(axis=1)).astype(float)/rf_day1.shape[1])*100).astype(int)]).T],axis=0)   

rfcnt_day2=np.concatenate([np.vstack([rf_day2[:,0,0],np.round((((((rf_day2[:,:,3].astype(int) ==0) & (rf_day2[:,:,6].astype(float) ==0 )) | ((rf_day2[:,:,3].astype(int) >0) & (rf_day2[:,:,6].astype(float) >0))).sum(axis=1)).astype(float)/rf_day2.shape[1])*100).astype(int), \
                          np.round(((((rf_day2[:,:,3].astype(int) <=0) & (rf_day2[:,:,6].astype(float) >0)).sum(axis=1)).astype(float)/rf_day2.shape[1])*100).astype(int), \
                          np.round(((((rf_day2[:,:,3].astype(int) >0) & (rf_day2[:,:,6].astype(float) <=0)).sum(axis=1)).astype(float)/rf_day2.shape[1])*100).astype(int)]).T],axis=0)   

rfcnt_day3=np.concatenate([np.vstack([rf_day3[:,0,0],np.round((((((rf_day3[:,:,3].astype(int) ==0) & (rf_day3[:,:,6].astype(float) ==0 )) | ((rf_day3[:,:,3].astype(int) >0) & (rf_day3[:,:,6].astype(float) >0))).sum(axis=1)).astype(float)/rf_day3.shape[1])*100).astype(int), \
                          np.round(((((rf_day3[:,:,3].astype(int) <=0) & (rf_day3[:,:,6].astype(float) >0)).sum(axis=1)).astype(float)/rf_day3.shape[1])*100).astype(int), \
                          np.round(((((rf_day3[:,:,3].astype(int) >0) & (rf_day3[:,:,6].astype(float) <=0)).sum(axis=1)).astype(float)/rf_day3.shape[1])*100).astype(int)]).T],axis=0)   

rfcnt_day4=np.concatenate([np.vstack([rf_day4[:,0,0],np.round((((((rf_day4[:,:,3].astype(int) ==0) & (rf_day4[:,:,6].astype(float) ==0 )) | ((rf_day4[:,:,3].astype(int) >0) & (rf_day4[:,:,6].astype(float) >0))).sum(axis=1)).astype(float)/rf_day4.shape[1])*100).astype(int), \
                          np.round(((((rf_day4[:,:,3].astype(int) <=0) & (rf_day4[:,:,6].astype(float) >0)).sum(axis=1)).astype(float)/rf_day4.shape[1])*100).astype(int), \
                          np.round(((((rf_day4[:,:,3].astype(int) >0) & (rf_day4[:,:,6].astype(float) <=0)).sum(axis=1)).astype(float)/rf_day4.shape[1])*100).astype(int)]).T],axis=0)   

rfcnt_day5=np.concatenate([np.vstack([rf_day5[:,0,0],np.round((((((rf_day5[:,:,3].astype(int) ==0) & (rf_day5[:,:,6].astype(float) ==0 )) | ((rf_day5[:,:,3].astype(int) >0) & (rf_day5[:,:,6].astype(float) >0))).sum(axis=1)).astype(float)/rf_day5.shape[1])*100).astype(int), \
                          np.round(((((rf_day5[:,:,3].astype(int) <=0) & (rf_day5[:,:,6].astype(float) >0)).sum(axis=1)).astype(float)/rf_day5.shape[1])*100).astype(int), \
                          np.round(((((rf_day5[:,:,3].astype(int) >0) & (rf_day5[:,:,6].astype(float) <=0)).sum(axis=1)).astype(float)/rf_day5.shape[1])*100).astype(int)]).T],axis=0)   

rfcnt_day6=np.concatenate([np.vstack([rf_day6[:,0,0],np.round((((((rf_day6[:,:,3].astype(int) ==0) & (rf_day6[:,:,6].astype(float) ==0 )) | ((rf_day6[:,:,3].astype(int) >0) & (rf_day6[:,:,6].astype(float) >0))).sum(axis=1)).astype(float)/rf_day6.shape[1])*100).astype(int), \
                          np.round(((((rf_day6[:,:,3].astype(int) <=0) & (rf_day6[:,:,6].astype(float) >0)).sum(axis=1)).astype(float)/rf_day6.shape[1])*100).astype(int), \
                          np.round(((((rf_day6[:,:,3].astype(int) >0) & (rf_day6[:,:,6].astype(float) <=0)).sum(axis=1)).astype(float)/rf_day6.shape[1])*100).astype(int)]).T],axis=0)   

rfcnt_day7=np.concatenate([np.vstack([rf_day7[:,0,0],np.round((((((rf_day7[:,:,3].astype(int) ==0) & (rf_day7[:,:,6].astype(float) ==0 )) | ((rf_day7[:,:,3].astype(int) >0) & (rf_day7[:,:,6].astype(float) >0))).sum(axis=1)).astype(float)/rf_day7.shape[1])*100).astype(int), \
                          np.round(((((rf_day7[:,:,3].astype(int) <=0) & (rf_day7[:,:,6].astype(float) >0)).sum(axis=1)).astype(float)/rf_day7.shape[1])*100).astype(int), \
                          np.round(((((rf_day7[:,:,3].astype(int) >0) & (rf_day7[:,:,6].astype(float) <=0)).sum(axis=1)).astype(float)/rf_day7.shape[1])*100).astype(int)]).T],axis=0)   

rfcnt_day8=np.concatenate([np.vstack([rf_day8[:,0,0],np.round((((((rf_day8[:,:,3].astype(int) ==0) & (rf_day8[:,:,6].astype(float) ==0 )) | ((rf_day8[:,:,3].astype(int) >0) & (rf_day8[:,:,6].astype(float) >0))).sum(axis=1)).astype(float)/rf_day8.shape[1])*100).astype(int), \
                          np.round(((((rf_day8[:,:,3].astype(int) <=0) & (rf_day8[:,:,6].astype(float) >0)).sum(axis=1)).astype(float)/rf_day8.shape[1])*100).astype(int), \
                          np.round(((((rf_day8[:,:,3].astype(int) >0) & (rf_day8[:,:,6].astype(float) <=0)).sum(axis=1)).astype(float)/rf_day8.shape[1])*100).astype(int)]).T],axis=0)   

rfcnt_day9=np.concatenate([np.vstack([rf_day9[:,0,0],np.round((((((rf_day9[:,:,3].astype(int) ==0) & (rf_day9[:,:,6].astype(float) ==0 )) | ((rf_day9[:,:,3].astype(int) >0) & (rf_day9[:,:,6].astype(float) >0))).sum(axis=1)).astype(float)/rf_day9.shape[1])*100).astype(int), \
                          np.round(((((rf_day9[:,:,3].astype(int) <=0) & (rf_day9[:,:,6].astype(float) >0)).sum(axis=1)).astype(float)/rf_day9.shape[1])*100).astype(int), \
                          np.round(((((rf_day9[:,:,3].astype(int) >0) & (rf_day9[:,:,6].astype(float) <=0)).sum(axis=1)).astype(float)/rf_day9.shape[1])*100).astype(int)]).T],axis=0)   


rain=np.concatenate([locs,rfcnt_day1[:,:],rfcnt_day2[:,1:],rfcnt_day3[:,1:],rfcnt_day4[:,1:],rfcnt_day5[:,1:],rfcnt_day6[:,1:],rfcnt_day8[:,1:],rfcnt_day7[:,1:],rfcnt_day8[:,1:],C_r],axis=1)
rain=rain[rain[:,0].argsort(kind='mergesort')] ;
acc_trwr=np.concatenate([temp,rhws,rain],axis=0) ;
np.savetxt('gefs07-15daysFcstAccuracy.csv', acc_trwr,fmt="%s",delimiter=",") ;










