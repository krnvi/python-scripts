#!/usr/bin/python

import os ; import sys ; import numpy as np ; import datetime as dt ; import csv ; import time ;

main="/home/OldData/gefsData/" ; scripts=main+'/scripts' ; corFcst=main+'/24hourlyoutput/'
#date=time.strftime("%Y%m%d");  
date=str(sys.argv[1]) ; spt=dt.datetime.strptime(date,"%Y%m%d")+dt.timedelta(days=7) ; spt=spt.strftime("%d%m%y") ;
corFle=corFcst+date+"/24hourlygefscorrected"+date+".csv" ; gefsFle=main+"/24hourlyoutput/"+date+"/24hourlygefs"+date+".csv" 
modFle="/home/Data/poolLatestWorkByModelTeam/output/correctedFile/24hourlycorrectedHeatIndex"+date+".csv"

os.chdir(corFcst)

G_fcst=np.genfromtxt(gefsFle, delimiter=',', dtype="S");C_fcst=np.genfromtxt(modFle,delimiter=',',dtype='S')

G_reqData=np.squeeze(G_fcst[np.array(np.where(G_fcst[:,2]==spt)).T],axis=None) ;
G_reqData=G_reqData[G_reqData[:,0].argsort()] ;

C_reqData1=np.squeeze(C_fcst[np.array(np.where(C_fcst[:,2]==spt)).T],axis=None)
C_reqData=np.squeeze(C_reqData1[np.array(np.where(np.in1d(C_reqData1[:,0],G_reqData[:,0]))).T],axis=None)
C_reqData=C_reqData[C_reqData[:,0].argsort()]

diff=C_reqData[:,3:7].astype(float)-G_reqData[:,3:7].astype(float)

K=np.empty((0,4))
for i in range(0,len(diff)):
    B=np.tile(diff[i],(9,1))
    K=np.append(K,B,axis=0,)
 
new_f=((G_fcst[:,3:7]).astype(float)+K).astype(int); new_Data= np.concatenate([G_fcst[:,0:3],new_f,G_fcst[:,7:]],axis=1)
np.savetxt(corFle, new_Data,fmt="%s",delimiter=",")
