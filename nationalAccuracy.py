#!/usr/bin/python

#####################################################################################################################################################################
def dataQcheck(date,code,id):
        lid=str(id);wndCode=code ; reqDt=dt.datetime.strptime(date,"%Y/%m/%d") + dt.timedelta(days=-1);reqDt=reqDt.strftime("%Y-%-m-%-d") ;
        reqDt1=dt.datetime.strptime(date,"%Y/%m/%d")+ dt.timedelta(days=-1) ; reqDt1=reqDt1.strftime("%Y-%m-%d") ;
        reqDt2=dt.datetime.strptime(date,"%Y/%m/%d")+ dt.timedelta(days=-1) ; reqDt2=reqDt2.strftime("%d%m%y") ;
        reqDt3=dt.datetime.strptime(date,"%Y/%m/%d") + dt.timedelta(days=-1); reqDt3=reqDt3.strftime("%Y%m%d");
        print obsFle ; print reqDt
        #os.system('cat %s |grep %s '%(obsFle,reqDt)) ; 
        pattern=re.compile(reqDt) ; sp="^%s,%s,%s" %(lid,reqDt1,reqDt2);pattern1=re.compile(sp)
	with open (obsFle,'r') as f:
             ln_pos=f.tell() ; rows=list(f) ; nrows=len(rows) ; f.seek(ln_pos)
             if nrows <= 1:
                 fdt=reqDt;mxtmp=float(0.1);mntmp=float(0.1);
                 mxhum=float(0.1);mnhum=float(0.1);prep=float(0.1);
                 print mxtmp,mntmp,mxhum,mnhum,prep
             else:
                 ln_pos=f.tell();f.next() ; line=f.next();ln=line.split(",");fs=ln[0];fs=fs[0:4];fs1=reqDt[0:4];
                 if fs == fs1:
                    print "file is correct"
                 else:
                    print "file is incorrect"
                     
                 f.seek(ln_pos)
                 hd=f.next(); hdr=hd.split(",") ; mxtphd=hdr[1];mntphd=hdr[3] ;
                 #fdt=reqDt; mxtmp=float(0) ; mntmp=float(0) ; mxhum=float(0);mnhum=float(0);prep=float(0) 
                 for r in f:
                     if pattern.search(r):
                        d=r.split(",") ;#print len(d[1])
                        if len(d[1]) >0 and len(d[3]) and len(d[7]) and len(d[9]):
                               #print d[1],d[3],d[7],d[9],d[19]
                               fdt=d[0] ; mxtmp=float(d[1]) ; mntmp=float(d[3]) ; mxhum=float(d[7]);mnhum=float(d[9]);prep=d[19];
                               print fdt,mxtmp,mntmp,mxhum,mnhum,prep
                         
                               if mxtphd.endswith("F"):
                                          mxtmp=((mxtmp)-32) / 1.80 ; mntmp=((mntmp)-32) / 1.80 ;         
                               else:
                                          mxtmp=mxtmp ; mntmp=mntmp ;
                        else:
                               
                               fdt=reqDt ; mxtmp=float(0.1);mntmp=float(0.1);mxhum=float(0.1);mnhum=float(0.1);prep=float(0.1);
                               #print fdt,mxtmp,mntmp,mxhum,mnhum,prep
                   
        odata=[fdt,mxtmp,mntmp,mxhum,mnhum,prep] ;#print odata 
        return odata ;
####################################################################################################################################################################
def findBias(date,id,nme,data):
    lid=str(id) ; obsdat=data ; reqDt=dt.datetime.strptime(date,"%Y/%m/%d") + dt.timedelta(days=-2); reqDt=reqDt.strftime("%Y%m%d") ; 
    reqDtt=dt.datetime.strptime(date,"%Y/%m/%d") + dt.timedelta(days=-1); reqDtt=reqDtt.strftime("%Y%m%d") ;
    reqDt1=dt.datetime.strptime(date,"%Y/%m/%d") + dt.timedelta(days=-2) ;  reqDt1=reqDt1.strftime("%Y-%m-%d") ;
    reqDt2=dt.datetime.strptime(date,"%Y/%m/%d") + dt.timedelta(days=-1) ;  reqDt2=reqDt2.strftime("%d%m%y") ;
    header="id,locNme,date,fday,fmxt,omxt,Bmxt,fmnt,omnt,Bmnt,fmxr,omxr,Bmxr,fmnr,omnr,bmnr"
    fcsFl=fcsFle + reqDt + "00.csv" ; bsFle=main+"correctedFcst/national_bias"+reqDtt+"00.csv" ; print fcsFl
    sp="^%s,%s,%s" %(lid,reqDt1,reqDt2) ; print sp ; print obsdat
    pattern=re.compile(sp) ;#sp=lid + ',' + reqDt1 +','+ reqDt2 ; #print sp
    with open (fcsFl,'r') as f1, open(bsFle,"a") as f2:
         csv_f2=csv.writer(f2);  #csv_f2.writenow(header) 
         for r in f1:
             if pattern.search(r):
                print r
                d=r.split(",") ; mxtmpF=float(d[3]) ; mntmpF=float(d[4]);mxhumF=float(d[5]) ; mnhumF=float(d[6]);prepF=float(d[9]) ;
                #print mxtmpF,mntmpF,mxhumF,mnhumF,prepF
                mxtmpB=mxtmpF-obsdat[1] ; mntmpB=mntmpF-obsdat[2] ; mxhumB=mxhumF-obsdat[3] ; mnhumB=mnhumF-obsdat[4] ;  #print mxtmpB,mntmpB,mxhumB,mnhumB
                bias=[mxtmpB,mntmpB,mxhumB,mnhumB] ;
                #print bias
                newline=[d[0],nme,d[1],mxtmpF,obsdat[1],mxtmpB,mntmpF,obsdat[2],mntmpB,mxhumF,obsdat[3],mxhumB,mnhumF,obsdat[4],mnhumB]
                #print newline
                csv_f2.writerow(newline);
    return bias
####################################################################################################################################################################
import os ; import sys ; import numpy as np ; import scipy as sp ; import datetime as dt ; import wget ;
import urllib as urll ; import time ; import urllib2 as urll2 ; import csv ; import re ;
#################################################################################################################################################################
#date=time.strftime("%Y/%m/%d") ; 
date=str(sys.argv[1]);
date1=dt.datetime.strptime(date,"%Y/%m/%d") ; date1=date1.strftime("%Y%m%d") ;
main="/home/Data/poolLatestWorkByModelTeam/nationalCor/"; lstFle=main+"/scripts/national_obsdata.lst";
fcsFle="/home/Data/poolLatestWorkByModelTeam/nationalCor/correctedFcst/24hourly"
with open("national_obsdata.lst","r") as lf:
     lst_f=csv.reader(lf)
     for loc in lst_f:
         lCode=loc[2] ; wndCode=loc[1] ; locNme=loc[0] ; obsFle=main + "obsData/" + wndCode + date1 + ".csv" ; print lCode,wndCode 
         obsData=dataQcheck(date,wndCode,lCode) 
         bias=findBias(date,lCode,locNme,obsData)
    
#################################################################################################################################################################
quit()

