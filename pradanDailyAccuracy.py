#!/usr/bin/env python
import os ; import sys ; import numpy as np ; import datetime as dt ; import csv ; import time ;import calendar as cl
from dateutil import rrule ; import MySQLdb ;

_a_date=str(sys.argv[1]) ;_to_date=_a_date ; fcs_ldays=1 ;
fcs_gen_date=dt.datetime.strptime(_a_date,'%Y%m%d')+dt.timedelta(days=-2) ; 
fcs_to_date=dt.datetime.strptime(_a_date,'%Y%m%d')+dt.timedelta(days=-1) ;

obs_from_date=(dt.datetime.strptime(_a_date,"%Y%m%d")+dt.timedelta(days=-1)) #.strftime('%Y%m%d') ; 
obs_to_date  =(dt.datetime.strptime(_a_date,"%Y%m%d")+dt.timedelta(days=0)) #.strftime('%Y%m%d') ;
no_obs_days=(obs_to_date-obs_from_date).days ; 
no_fcs_days=(fcs_to_date-fcs_gen_date).days ;


obs_date_list=[x for x in rrule.rrule(rrule.HOURLY,dtstart=obs_from_date,until=obs_to_date)]
del obs_date_list[-1]

pradan_id=np.genfromtxt("/home/OldData/IntCor/pradan/pradan.lst",delimiter=',',dtype="S")
pradan_idd=pradan_id[pradan_id[:,1].argsort(kind='mergesort')]

########## model fcst from file ############################################# 
mod_fcst=np.empty((0,33))
date=fcs_gen_date.strftime('%Y%m%d')
modFle="/home/Data/poolLatestWorkByModelTeam/output/correctedFile/24hourlycorrectedHeatIndex"+date+".csv"
mod_fcst1=np.genfromtxt(modFle, delimiter=',', dtype="S");
mod_fcst1 = mod_fcst1[mod_fcst1[:,0].argsort(kind='mergesort')]
mod_fcst=np.concatenate([mod_fcst,np.squeeze(mod_fcst1[np.array(np.where(np.in1d(mod_fcst1[:,0],pradan_id[:,1]))).T],axis=None)],axis=0)

mod_reqData=mod_fcst[mod_fcst[:,0].argsort(kind='mergesort')]
mod_Data=np.concatenate([mod_reqData[:,0:7],mod_reqData[:,8:10]],axis=1)     
sh_ftr0=pradan_id.shape[0] ; sh_ftr1=mod_Data.shape[0]/pradan_id.shape[0] ; sh_ftr2=mod_Data.shape[1] ;
mod_data=mod_Data.reshape(sh_ftr0,sh_ftr1,sh_ftr2) 
mod_data=mod_data[:,1,:] 
mod=mod_data[mod_data[:,0].argsort(kind='mergesort')] 

######### obs data from data base #############################################
obs_Data=np.empty((0,11))
for did,tid in pradan_id[:,0:2]:
    db=MySQLdb.connect(host ="192.168.103.56", user = "swims_readonly", passwd = "sky@swims#read", db = "aws")
    cursr=db.cursor() ; 
    sqlstmt="SELECT DATA_DATE,PYRANO,LEAF_WETNESS,HUMIDITY,RAIN,WIND_MAX from STATION_DATA where STATION_ID=%s and  \
                                        DATA_DATE>=%s and DATA_DATE<%s"%(did,obs_from_date.strftime('%Y%m%d'),obs_to_date.strftime('%Y%m%d')) ;
    usqlstmt="SELECT DATA_DATE,PYRANO,LEAF_WETNESS,HUMIDITY,RAIN,WIND_MAX from STATION_DATA where STATION_ID=%s and IS_UPDATED=1 and \
                                        DATA_DATE>=%s and DATA_DATE<%s"%(did,obs_from_date.strftime('%Y%m%d'),obs_to_date.strftime('%Y%m%d')) ;                                  
    cursr.execute(sqlstmt) ;data=np.array(cursr.fetchall(),dtype="S") ; #print data.shape
    datcnt=np.round(np.array((data.shape[0]))).astype(int)
    if data.shape !=(no_obs_days*24,6) :
       if data.size == 0:
           data=np.empty((no_obs_days*24,6))
           data[:]=np.NAN
       else:
           dates=list(np.unique(([dt.datetime.strptime(dt.datetime.strptime(x,'%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H'),'%Y-%m-%d %H') for x in data[:,0]])))
           dates1=np.array(np.unique(([dt.datetime.strptime(dt.datetime.strptime(x,'%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H'),'%Y-%m-%d %H') \
           for x in data[:,0]]),return_index=True))
           date_set = set(obs_date_list[0]+dt.timedelta(hours=x) for x in range(int((obs_date_list[-1]-obs_date_list[0]).total_seconds()/60/60)+1))   
           #mis_date = np.array([x.strftime('%Y-%m-%d %H:%M:%S') for x in sorted(date_set-set(dates))]) 
           mis_date = ([x for x in sorted(date_set-set(dates))])
           indx_misdate=np.array(np.squeeze(np.where(np.in1d(obs_date_list,mis_date))),ndmin=1).T
           indx_prsdate=np.array(np.squeeze(np.where(np.in1d(obs_date_list,dates))),ndmin=1).T
           dat=np.empty((int(indx_prsdate.shape[0])+ int(indx_misdate.shape[0]),data.shape[1])).astype("S")         
           dat[:]=np.NAN ; dat[(indx_prsdate),:]=data[np.array(dates1[1],dtype=int),:]  ; dat[(indx_misdate),0]=mis_date
           data=dat ;
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
#    sumrfl=np.round(data[:,:,4].astype(float).sum(axis=1)).astype(int)
    
#    mxdata=((data[:,:,1:].astype(float)).max(axis=1))
#    mndata=(data[:,:,1:].astype(float).min(axis=1))  
#    sumrfl=np.round(data[:,:,4].astype(float).sum(axis=1)).astype(int)    
    
    mxdata=(np.nanmax(data[:,:,1:].astype(float),axis=1)).astype(int) 
    mndata=(np.nanmin(data[:,:,1:].astype(float),axis=1)).astype(int)  
    sumrfl=(np.nansum(data[:,:,4].astype(float),axis=1)).astype(int)    
    
    D=np.concatenate([I,np.vstack([tim,mxdata[:,0],mndata[:,1],mxdata[:,2],mndata[:,2],mxdata[:,4],mndata[:,4],sumrfl,datcnt]).T],axis=1)
    obs_Data=np.concatenate([obs_Data,D],axis=0) ;
    cursr.close()
    db.close()
#obs_data=obs_Data.reshape(pradan_id.shape[0],no_obs_days,10)
obs_data=obs_Data[obs_Data[:,0].argsort(kind='mergesort')]
obs=obs_data ;
#obs=np.empty((pradan_id.shape[0],0,10)) 
#for i in range(0,mod.shape[1]/7):
#    S=obs_data[:,i:i+7,:]
#    obs=np.concatenate([obs,S],axis=1) 
    
diff=np.round(np.abs(mod[:,3:8].astype(float)-obs[:,3:8].astype(float))).astype(int)
#diff=(np.ma.masked_where(diff==-9223372036854775808,diff))
diff=np.concatenate([mod[:,0:3],diff[:,:]],axis=1)
locs=(pradan_idd[np.array(np.where(np.in1d(diff[:,0],pradan_idd[:,1]))).T,2])
diff=np.concatenate([locs,diff[:,:]],axis=1)
header="LocName,id,fcsGendate,fcsdate,mxtbias,mntbias,mxhunbias,mnhumbias,mxwsbias"
header=np.vstack(np.array(header.split(","))).T 
bias=np.concatenate([header,diff],axis=0)
afle="/home/Data/poolLatestWorkByModelTeam/nationalCor/pradan/pradanDailyBias_"+fcs_gen_date.strftime("%Y%m%d")+".csv"
np.savetxt(afle, bias,fmt="%s",delimiter=",") ;

ofle="/home/Data/poolLatestWorkByModelTeam/nationalCor/pradan/pradanDailyObs_"+obs_from_date.strftime("%Y%m%d")+".csv"
locs1=(pradan_idd[np.array(np.where(np.in1d(obs[:,0],pradan_idd[:,1]))).T,2])
header1="LocName,id,date,maxt,mint,mxhum,mnhum,maxws,minws,sumrf,obscnt"
header1=np.vstack(np.array(header1.split(","))).T 
obs1=np.concatenate([header1,np.concatenate([locs,np.vstack(obs[:,0]),obs[:,2:]],axis=1)],axis=0)
np.savetxt(ofle, obs1,fmt="%s",delimiter=",") ;
