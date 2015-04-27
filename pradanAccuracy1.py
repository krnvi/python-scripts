#!/usr/bin/env python
import os ; import sys ; import numpy as np ; import datetime as dt ; import csv ; import time ;import calendar as cl
from dateutil import rrule ; import MySQLdb ;

_from_date='20150101' ;_to_date='20150131' ; fcs_ldays=8 ;
fcs_from_date=dt.datetime.strptime(_from_date,'%Y%m%d') ; fcs_to_date=dt.datetime.strptime(_to_date,'%Y%m%d') ;
obs_from_date=(dt.datetime.strptime(_from_date,"%Y%m%d")+dt.timedelta(days=1)) #.strftime('%Y%m%d') ; 
obs_to_date  =(dt.datetime.strptime(_to_date,"%Y%m%d")+dt.timedelta(days=fcs_ldays)) #.strftime('%Y%m%d') ;
no_obs_days=(obs_to_date-obs_from_date).days
no_fcs_days=(fcs_to_date-fcs_from_date).days+1
obs_date_list=[x for x in rrule.rrule(rrule.HOURLY,dtstart=obs_from_date,until=obs_to_date)]
del obs_date_list[-1]

pradan_id=np.genfromtxt("/home/OldData/IntCor/pradan/pradan.lst",delimiter=',',dtype="S")
pradan_idd=pradan_id[pradan_id[:,1].argsort(kind='mergesort')]

########## model fcst from file ############################################# 
mod_fcst=np.empty((0,33))
for date in rrule.rrule(rrule.DAILY,dtstart=fcs_from_date,until=fcs_to_date):
         date=date.strftime('%Y%m%d')
         #modFle="/home/Data//poolLatestWorkByModelTeam/output/correctedFile/correctedfilesweb/24hourlycorrectedHeatIndex"+date+".csv"
         modFle="/home/OldData/IntCor/pradan/24hourlycorrectedHeatIndex"+date+".csv"
         mod_fcst1=np.genfromtxt(modFle, delimiter=',', dtype="S");
         #mod_fcst1 = mod_fcst1[np.argsort(mod_fcst1[:,2],kind='mergesort')]
         mod_fcst1 = mod_fcst1[mod_fcst1[:,0].argsort(kind='mergesort')]
         mod_fcst=np.concatenate([mod_fcst,np.squeeze(mod_fcst1[np.array(np.where(np.in1d(mod_fcst1[:,0],pradan_id[:,1]))).T],axis=None)],axis=0)

mod_reqData=mod_fcst[mod_fcst[:,0].argsort(kind='mergesort')]
mod_Data=np.concatenate([mod_reqData[:,0:7],mod_reqData[:,8:10]],axis=1)     
sh_ftr0=pradan_id.shape[0] ; sh_ftr1=mod_Data.shape[0]/pradan_id.shape[0] ; sh_ftr2=mod_Data.shape[1] ;
mod_data=mod_Data.reshape(sh_ftr0,sh_ftr1,sh_ftr2) 
mod_data=np.delete(mod_data,range(0,sh_ftr1,fcs_ldays),axis=1)
mod=mod_data[mod_data[:,0,0].argsort(kind='mergesort')]

######### obs data from data base #############################################
obs_Data=np.empty((0,10))
for did,tid,nme in pradan_id[:,0:3]:
    obsFle="/home/OldData/IntCor/pradan/obsJanuary2015/"+nme+'.csv'
    obs_dat=np.genfromtxt(obsFle,delimiter=',',dtype="S")
    data=obs_dat[24:,:]    
    
    if data.shape[0] !=(no_obs_days*24) :
       dates=[dt.datetime.strptime(x,'%Y-%m-%d %H:%M:%S') for x in data[:,0]]
       date_set = set(dates[0]+dt.timedelta(hours=x) for x in range(int((dates[-1]-dates[0]).total_seconds()/60/60)+1))    
       mis_date = np.array([x.strftime('%Y-%m-%d %H:%M:%S') for x in sorted(date_set-set(dates))]) 
       indx_misdate=np.array(np.nonzero(([x.days for x in np.diff(dates)])))+1       
       fil_data=np.empty((mis_date.shape[0],data.shape[1]))
       fil_data[:]=np.NAN ;fil_data=fil_data.astype(str)  ; fil_data[:,0]=mis_date
       #fil_data=fil_data.astype(str)  ; fil_data[:,0]=mis_date
       data=np.concatenate([data[0:indx_misdate,:],fil_data,data[indx_misdate:,:]])
    else:
        data=data
    #data1=(np.ma.masked_invalid(data[:,1:].astype(float))).astype(str) 
    #data=np.concatenate([np.vstack(data[:,0]),data1],axis=1)
    no_rws=data.shape[0]/no_obs_days ;no_clns=data.shape[1]
    data=data.reshape(no_obs_days,no_rws,no_clns)
    I=((np.ones((data.shape[0],2))*[int(tid),int(did)]).astype(int)).astype(str) 
    tim=data[:,0,0]

#    mxdata=np.round((data[:,:,1:].astype(float)).max(axis=1)).astype(int) 
#    mndata=np.round(data[:,:,1:].astype(float).min(axis=1)).astype(int)  
#    sumrfl=np.round(data[:,:,3].astype(float).sum(axis=1)).astype(int)
    
    mxdata=((data[:,:,1:6].astype(float)).max(axis=1))
    mndata=(data[:,:,1:6].astype(float).min(axis=1))  
    sumrfl=np.round(data[:,:,4].astype(float).sum(axis=1)).astype(int)    
    
#    mxdata=np.round(np.nanmax(data[:,:,1:].astype(float),axis=1)).astype(int) 
#    mndata=np.round(data[:,:,1:].astype(float).nanmin(axis=1)).astype(int)  
#    sumrfl=np.round(data[:,:,3].astype(float).nansum(axis=1)).astype(int)
    D=np.concatenate([I,np.vstack([tim,mxdata[:,0],mndata[:,1],mxdata[:,2],mndata[:,2],mxdata[:,4],mndata[:,4],sumrfl]).T],axis=1)
    obs_Data=np.concatenate([obs_Data,D],axis=0) ;


obs_data=obs_Data.reshape(pradan_id.shape[0],no_obs_days,10)
obs_data=obs_data[obs_data[:,0,0].argsort(kind='mergesort')]
obs=np.empty((pradan_id.shape[0],0,10))
for i in range(0,mod.shape[1]/7):
    S=obs_data[:,i:i+7,:]
    obs=np.concatenate([obs,S],axis=1) 
    
diff=np.round(np.abs(mod[:,:,3:8].astype(float)-obs[:,:,3:8].astype(float))).astype(int)
#diff=(np.ma.masked_where(diff==-9223372036854775808,diff))
diff=np.concatenate([mod[:,:,0:3],diff[:,:,:]],axis=2)


diff_day1=diff[:,0::7,:]  
diff_day2=diff[:,1::7,:]
diff_day3=diff[:,2::7,:]
diff_day4=diff[:,3::7,:]
diff_day5=diff[:,4::7,:]
diff_day6=diff[:,5::7,:]
diff_day7=diff[:,6::7,:]

rmse_day1=np.concatenate([np.vstack(diff_day1[:,0,0]),np.round(np.sqrt(np.square(diff_day1[:,:,3:].astype(int)).mean(axis=1))).astype(int)],axis=1) 
rmse_day2=np.concatenate([np.vstack(diff_day2[:,0,0]),np.round(np.sqrt(np.square(diff_day2[:,:,3:].astype(int)).mean(axis=1))).astype(int)],axis=1) 
rmse_day3=np.concatenate([np.vstack(diff_day3[:,0,0]),np.round(np.sqrt(np.square(diff_day3[:,:,3:].astype(int)).mean(axis=1))).astype(int)],axis=1) 
rmse_day4=np.concatenate([np.vstack(diff_day4[:,0,0]),np.round(np.sqrt(np.square(diff_day4[:,:,3:].astype(int)).mean(axis=1))).astype(int)],axis=1) 
rmse_day5=np.concatenate([np.vstack(diff_day5[:,0,0]),np.round(np.sqrt(np.square(diff_day5[:,:,3:].astype(int)).mean(axis=1))).astype(int)],axis=1) 
rmse_day6=np.concatenate([np.vstack(diff_day6[:,0,0]),np.round(np.sqrt(np.square(diff_day6[:,:,3:].astype(int)).mean(axis=1))).astype(int)],axis=1) 
rmse_day7=np.concatenate([np.vstack(diff_day7[:,0,0]),np.round(np.sqrt(np.square(diff_day7[:,:,3:].astype(int)).mean(axis=1))).astype(int)],axis=1) 


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

locs=(pradan_idd[np.array(np.where(np.in1d(tpcnt_day1[:,0],pradan_idd[:,1]))).T,2])

maxt=np.concatenate([locs,np.vstack(tpcnt_day1[:,0]),tpcnt_day1[:,1::2],tpcnt_day2[:,1::2],tpcnt_day3[:,1::2],tpcnt_day4[:,1::2],tpcnt_day5[:,1::2],tpcnt_day6[:,1::2],tpcnt_day7[:,1::2]],axis=1)
maxt=maxt[maxt[:,0].argsort(kind='mergesort')] ;
mint=np.concatenate([locs,np.vstack(tpcnt_day1[:,0]),tpcnt_day1[:,2::2],tpcnt_day2[:,2::2],tpcnt_day3[:,2::2],tpcnt_day4[:,2::2],tpcnt_day5[:,2::2],tpcnt_day6[:,2::2],tpcnt_day7[:,2::2]],axis=1)
mint=mint[mint[:,0].argsort(kind='mergesort')] ;
temp=np.concatenate([maxt,mint],axis=0) ;
            
''' Relative Humidity & wind speed '''
C_r=np.zeros((pradan_id.shape[0],7)).astype(int)

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


maxrh=np.concatenate([locs,np.vstack(rhwscnt_day1[:,0]),rhwscnt_day1[:,1::3],rhwscnt_day2[:,1::3],rhwscnt_day3[:,1::3],rhwscnt_day4[:,1::3],rhwscnt_day5[:,1::3],rhwscnt_day6[:,1::3],rhwscnt_day7[:,1::3],C_r],axis=1)
maxrh=maxrh[maxrh[:,0].argsort(kind='mergesort')] ;
minrh=np.concatenate([locs,np.vstack(rhwscnt_day1[:,0]),rhwscnt_day1[:,2::3],rhwscnt_day2[:,2::3],rhwscnt_day3[:,2::3],rhwscnt_day4[:,2::3],rhwscnt_day5[:,2::3],rhwscnt_day6[:,2::3],rhwscnt_day7[:,2::3],C_r],axis=1)
minrh=minrh[minrh[:,0].argsort(kind='mergesort')] ;
maxws=np.concatenate([locs,np.vstack(rhwscnt_day1[:,0]),rhwscnt_day1[:,3::3],rhwscnt_day2[:,3::3],rhwscnt_day3[:,3::3],rhwscnt_day4[:,3::3],rhwscnt_day5[:,3::3],rhwscnt_day6[:,3::3],rhwscnt_day7[:,3::3],C_r],axis=1)
maxws=maxws[maxws[:,0].argsort(kind='mergesort')] ;
rhws=np.concatenate([maxrh,minrh,maxws],axis=0)            


''' Rainfall '''

rf_day1=np.concatenate([mod[:,0::7,0:3],mod[:,0::7,8].reshape(pradan_id.shape[0],no_fcs_days,1),obs[:,0::7,0:3],obs[:,0::7,9].reshape(pradan_id.shape[0],no_fcs_days,1)],axis=2)  
rf_day2=np.concatenate([mod[:,1::7,0:3],mod[:,1::7,8].reshape(pradan_id.shape[0],no_fcs_days,1),obs[:,1::7,0:3],obs[:,1::7,9].reshape(pradan_id.shape[0],no_fcs_days,1)],axis=2)  
rf_day3=np.concatenate([mod[:,2::7,0:3],mod[:,2::7,8].reshape(pradan_id.shape[0],no_fcs_days,1),obs[:,2::7,0:3],obs[:,2::7,9].reshape(pradan_id.shape[0],no_fcs_days,1)],axis=2)  
rf_day4=np.concatenate([mod[:,3::7,0:3],mod[:,3::7,8].reshape(pradan_id.shape[0],no_fcs_days,1),obs[:,3::7,0:3],obs[:,3::7,9].reshape(pradan_id.shape[0],no_fcs_days,1)],axis=2)  
rf_day5=np.concatenate([mod[:,4::7,0:3],mod[:,4::7,8].reshape(pradan_id.shape[0],no_fcs_days,1),obs[:,4::7,0:3],obs[:,4::7,9].reshape(pradan_id.shape[0],no_fcs_days,1)],axis=2)  
rf_day6=np.concatenate([mod[:,5::7,0:3],mod[:,5::7,8].reshape(pradan_id.shape[0],no_fcs_days,1),obs[:,5::7,0:3],obs[:,5::7,9].reshape(pradan_id.shape[0],no_fcs_days,1)],axis=2)  
rf_day7=np.concatenate([mod[:,6::7,0:3],mod[:,6::7,8].reshape(pradan_id.shape[0],no_fcs_days,1),obs[:,6::7,0:3],obs[:,6::7,9].reshape(pradan_id.shape[0],no_fcs_days,1)],axis=2)  

rfcnt_day1=np.concatenate([np.vstack([rf_day1[:,0,0],np.round((((((rf_day1[:,:,3].astype(int) ==0) & (rf_day1[:,:,7].astype(int) ==0 )) | ((rf_day1[:,:,3].astype(int) >0) & (rf_day1[:,:,7].astype(int) >0))).sum(axis=1)).astype(float)/rf_day1.shape[1])*100).astype(int), \
                          np.round(((((rf_day1[:,:,3].astype(int) <=0) & (rf_day1[:,:,7].astype(int) >0)).sum(axis=1)).astype(float)/rf_day1.shape[1])*100).astype(int), \
                          np.round(((((rf_day1[:,:,3].astype(int) >0) & (rf_day1[:,:,7].astype(int) <=0)).sum(axis=1)).astype(float)/rf_day1.shape[1])*100).astype(int)]).T],axis=0)   

rfcnt_day2=np.concatenate([np.vstack([rf_day2[:,0,0],np.round((((((rf_day2[:,:,3].astype(int) ==0) & (rf_day2[:,:,7].astype(int) ==0 )) | ((rf_day2[:,:,3].astype(int) >0) & (rf_day2[:,:,7].astype(int) >0))).sum(axis=1)).astype(float)/rf_day2.shape[1])*100).astype(int), \
                          np.round(((((rf_day2[:,:,3].astype(int) <=0) & (rf_day2[:,:,7].astype(int) >0)).sum(axis=1)).astype(float)/rf_day2.shape[1])*100).astype(int), \
                          np.round(((((rf_day2[:,:,3].astype(int) >0) & (rf_day2[:,:,7].astype(int) <=0)).sum(axis=1)).astype(float)/rf_day2.shape[1])*100).astype(int)]).T],axis=0)   

rfcnt_day3=np.concatenate([np.vstack([rf_day3[:,0,0],np.round((((((rf_day3[:,:,3].astype(int) ==0) & (rf_day3[:,:,7].astype(int) ==0 )) | ((rf_day3[:,:,3].astype(int) >0) & (rf_day3[:,:,7].astype(int) >0))).sum(axis=1)).astype(float)/rf_day3.shape[1])*100).astype(int), \
                          np.round(((((rf_day3[:,:,3].astype(int) <=0) & (rf_day3[:,:,7].astype(int) >0)).sum(axis=1)).astype(float)/rf_day3.shape[1])*100).astype(int), \
                          np.round(((((rf_day3[:,:,3].astype(int) >0) & (rf_day3[:,:,7].astype(int) <=0)).sum(axis=1)).astype(float)/rf_day3.shape[1])*100).astype(int)]).T],axis=0)   

rfcnt_day4=np.concatenate([np.vstack([rf_day4[:,0,0],np.round((((((rf_day4[:,:,3].astype(int) ==0) & (rf_day4[:,:,7].astype(int) ==0 )) | ((rf_day4[:,:,3].astype(int) >0) & (rf_day4[:,:,7].astype(int) >0))).sum(axis=1)).astype(float)/rf_day4.shape[1])*100).astype(int), \
                          np.round(((((rf_day4[:,:,3].astype(int) <=0) & (rf_day4[:,:,7].astype(int) >0)).sum(axis=1)).astype(float)/rf_day4.shape[1])*100).astype(int), \
                          np.round(((((rf_day4[:,:,3].astype(int) >0) & (rf_day4[:,:,7].astype(int) <=0)).sum(axis=1)).astype(float)/rf_day4.shape[1])*100).astype(int)]).T],axis=0)   

rfcnt_day5=np.concatenate([np.vstack([rf_day5[:,0,0],np.round((((((rf_day5[:,:,3].astype(int) ==0) & (rf_day5[:,:,7].astype(int) ==0 )) | ((rf_day5[:,:,3].astype(int) >0) & (rf_day5[:,:,7].astype(int) >0))).sum(axis=1)).astype(float)/rf_day5.shape[1])*100).astype(int), \
                          np.round(((((rf_day5[:,:,3].astype(int) <=0) & (rf_day5[:,:,7].astype(int) >0)).sum(axis=1)).astype(float)/rf_day5.shape[1])*100).astype(int), \
                          np.round(((((rf_day5[:,:,3].astype(int) >0) & (rf_day5[:,:,7].astype(int) <=0)).sum(axis=1)).astype(float)/rf_day5.shape[1])*100).astype(int)]).T],axis=0)   

rfcnt_day6=np.concatenate([np.vstack([rf_day6[:,0,0],np.round((((((rf_day6[:,:,3].astype(int) ==0) & (rf_day6[:,:,7].astype(int) ==0 )) | ((rf_day6[:,:,3].astype(int) >0) & (rf_day6[:,:,7].astype(int) >0))).sum(axis=1)).astype(float)/rf_day6.shape[1])*100).astype(int), \
                          np.round(((((rf_day6[:,:,3].astype(int) <=0) & (rf_day6[:,:,7].astype(int) >0)).sum(axis=1)).astype(float)/rf_day6.shape[1])*100).astype(int), \
                          np.round(((((rf_day6[:,:,3].astype(int) >0) & (rf_day6[:,:,7].astype(int) <=0)).sum(axis=1)).astype(float)/rf_day6.shape[1])*100).astype(int)]).T],axis=0)   

rfcnt_day7=np.concatenate([np.vstack([rf_day7[:,0,0],np.round((((((rf_day7[:,:,3].astype(int) ==0) & (rf_day7[:,:,7].astype(int) ==0 )) | ((rf_day7[:,:,3].astype(int) >0) & (rf_day7[:,:,7].astype(int) >0))).sum(axis=1)).astype(float)/rf_day7.shape[1])*100).astype(int), \
                          np.round(((((rf_day7[:,:,3].astype(int) <=0) & (rf_day7[:,:,7].astype(int) >0)).sum(axis=1)).astype(float)/rf_day7.shape[1])*100).astype(int), \
                          np.round(((((rf_day7[:,:,3].astype(int) >0) & (rf_day7[:,:,7].astype(int) <=0)).sum(axis=1)).astype(float)/rf_day7.shape[1])*100).astype(int)]).T],axis=0)   
rain=np.concatenate([locs,rfcnt_day1[:,:],rfcnt_day2[:,1:],rfcnt_day3[:,1:],rfcnt_day4[:,1:],rfcnt_day5[:,1:],rfcnt_day6[:,1:],rfcnt_day7[:,1:],C_r],axis=1)
rain=rain[rain[:,0].argsort(kind='mergesort')] ;
acc_trwr=np.concatenate([temp,rhws,rain],axis=0) ;
np.savetxt('tmpFle.csv', acc_trwr,fmt="%s",delimiter=",") ;










