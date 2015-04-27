#!/usr/bin/python

#################################################################################################################################################################

def downloadWndData(date,code):
        def readurl(url):
           web=urll2.Request(url) ;
           try:
                htm = urll2.urlopen(web) ; cont=htm.read() ; #print dat
                f=open("tmpFle","w") ; f.write(cont); f.close();
           except urll2.HTTPError as e:
                url1=e.geturl() ; print "Error in Download :",url1 ; readurl(url1)
                #raise Exception('Error opening %s: %s' % (e.geturl(), e))
                pass
           except urll2.URLError as e:
                #url1=e.geturl() ; 
                print "Error in Download :",url ; readurl(url)
                #raise Exception('Error opening %s: %s' % (e.geturl(), e))
                pass
           except socket.error as e:
                print "Error in Download:",url ; readurl(url)

        wndCode=code ; reqDt=dt.datetime.strptime(date,"%Y/%m/%d") + dt.timedelta(days=-1);reqDt=reqDt.strftime("%Y/%m/%d")
        date1=dt.datetime.strptime(date,"%Y/%m/%d") ; date1=date1.strftime("%Y%m%d"); obsFle=main + "obsData/" + wndCode + date1 + ".csv"
        url="http://www.wunderground.com/history/airport/" + wndCode + "/" + reqDt + "/MonthlyHistory.html?format=1" ;
        readurl(url) ;     
        with open("tmpFle", "rb") as infile,open(obsFle, "wb") as outfile:
             csv_f1 = csv.reader(infile) ;  csv_f2 = csv.writer(outfile)
             conversion = set('<br />')  ;  csv_f1.next()
             for r in csv_f1:
                 newline = [''.join(' ' if c in conversion else c for c in entry) for entry in r]
                 csv_f2.writerow(newline)
        os.remove("tmpFle")

#####################################################################################################################################################################
def dataQcheck(date,code,id,nme):
        lid=str(id);wndCode=code ; reqDtt=dt.datetime.strptime(date,"%Y/%m/%d") + dt.timedelta(days=(0)) ; reqDtt=reqDtt.strftime("%Y%m%d")
        mxtmpBB=float(0) ; mntmpBB=float(0) ; mxhumBB=float(0) ; mnhumBB=float(0) ; cnt=0
        for i in range(0,3):
            
            prevDt=dt.datetime.strptime(date,"%Y/%m/%d") + dt.timedelta(days=-(i)) ; prevDt=prevDt.strftime("%Y%m%d")     ;print prevDt
            prevDtt=dt.datetime.strptime(prevDt,"%Y%m%d")                          ; prevDtt=prevDtt.strftime("%Y/%m/%d") ;print prevDtt
            reqDt=dt.datetime.strptime(prevDt,"%Y%m%d")  + dt.timedelta(days=-1)   ; reqDt=reqDt.strftime("%Y-%-m-%-d")   ;print reqDt

            reqDt1=dt.datetime.strptime(prevDt,"%Y%m%d") + dt.timedelta(days=-2) ;  reqDt1=reqDt1.strftime("%Y%m%d") ;
            reqDt2=dt.datetime.strptime(prevDt,"%Y%m%d") + dt.timedelta(days=-2) ;  reqDt2=reqDt2.strftime("%Y-%m-%d") ;
            reqDt3=dt.datetime.strptime(prevDt,"%Y%m%d") + dt.timedelta(days=-1) ;  reqDt3=reqDt3.strftime("%d%m%y") ;
            ################################################################################################################################# 
          
            obsFle=main+"obsData/" +wndCode + prevDt + ".csv"      ; print obsFle
            fcsFl=fcsFle + reqDt1 + ".csv"                         ; print fcsFl
            bsFle=main+"correctedFcst/3daysbiasfile"+reqDtt+".csv" ; print bsFle
            sp="^%s,%s,%s" %(lid,reqDt2,reqDt3)                    ; print sp
            if os.path.isfile(obsFle):
               print "File exist:"
            else:
               print "File do not exist:Download again",prevDtt,wndCode
               downloadWndData(prevDtt,wndCode)
            if os.path.isfile(fcsFl):
               print "Forecast File exist:"
            else:
               print "Forecast File do not exist: Exit Correction"
               quit()
            ##################################################################################################################################
            mxtmp=float(0)  ; mntmp=float(0)  ; mxhum=float(0)  ; mnhum=float(0); 
            mxtmpF=float(0) ; mntmpF=float(0) ; mxhumF=float(0) ; mnhumF=float(0);
            mxtmpB=float(0) ; mntmpB=float(0) ; mxhumB=float(0) ; mnhumB=float(0); 
            pattern=re.compile(reqDt) ; pattern1=re.compile(sp) ; 
	    with open (obsFle,'r') as f, open(bsFle,'a')as bsfile:
              csv_bf=csv.writer(bsfile);
              #print mxtmp,mntmp,mxhum,mnhum 
              ln_pos=f.tell() ; rows=list(f) ; nrows=len(rows) ; print nrows; f.seek(ln_pos)
              if nrows <= 1:
                 print "Error:Obs File doesnot have any values"
                 #mxtmp=0;mntmp=0;mxhum=0,mnhum=0;
                 #mxtmpF=0;mntmpF=0;mxhumF=0;mnhumF=0
                 #fdt=prevDt;mxtmpB=float(0);mntmpB=float(0);mxhumB=float(0);mnhumB=float(0);
                 #print mxtmp,mntmp,mxhum,mnhum
              else:
                 
                 #ln_pos=f.tell();f.next() ; line=f.next();ln=line.split(",");fs=ln[0];fs=fs[0:4];fs1=reqDt[0:4];
                 #if fs == fs1:
                 #   print "file is correct"
                 #else:
                 #   print "file is incorrect"
                 #   downloadWndData(date,wndCode)  
                 #f.seek(ln_pos)

                 hd=f.next(); hdr=hd.split(",") ; mxtphd=hdr[1];mntphd=hdr[3] ;
                  
                 for r in f:
                    if pattern.search(r):
                       d=r.split(",") ;#print len(d[1])
                       if len(d[1]) >0 and len(d[3]) >0 and len(d[7])>0 and len(d[9])>0:
                               print d[1],d[3],d[7],d[9],d[19]
                               if mxtphd.endswith("F"):
                                          mxxtmp=((float(d[1]))-32) / 1.80 ; mnntmp=((float(d[3]))-32) / 1.80 ;
                               else:
                                          mxxtmp=float(d[1]) ; mnntmp=float(d[3]) ;
                                                              
                               fdt=prevDt ; mxtmp=mxxtmp ; mntmp=mnntmp ; mxhum=float(d[7]);mnhum=float(d[9]);cnt=cnt+1
                               print fdt,mxxtmp,mnntmp,mxhum,mnhum
                               with open (fcsFl,'r') as f1:
                                    
                                    for rr in f1:
                                        
                                        if pattern1.search(rr):
                                            dd=rr.split(",") ; mxtmpF=float(dd[5]) ; mntmpF=float(dd[4]);mxhumF=float(dd[12]) ; mnhumF=float(dd[11]);
                                            print mxtmpF,mntmpF,mxhumF,mnhumF
                                            mxtmpB=mxtmpF-mxtmp ; mntmpB=mntmpF-mntmp ; mxhumB=mxhumF-mxhum ; mnhumB=mnhumF-mnhum ;
                                            #bias=[mxtmpB,mntmpB,mxhumB,mnhumB] ;
                        
                       else:
                               print "Error: Obs Data is not proper"
                               #mxtmp=0;mntmp=0;mxhum=0,mnhum=0;
                               #mxtmpF=0;mntmpF=0;mxhumF=0;mnhumF=0
                               #mxtmpB=float(0);mntmpB=float(0);mxhumB=float(0);mnhumB=float(0);
                               #print fdt,mxtmp,mntmp,mxhum,mnhum
                    #else:
                    #   print "Error: Pattern not found in obs file"
                 newline=[lid,nme,prevDt,reqDt1,mxtmpF,mxtmp,mxtmpB,mntmpF,mntmp,mntmpB,mxhumF,mxhum,mxhumB,mnhumF,mnhum,mnhumB]
                 csv_bf.writerow(newline);
              
            mxtmpBB=mxtmpBB+mxtmpB ; mntmpBB=mntmpBB+mntmpB ; mxhumBB=mxhumBB+mxhumB ; mnhumBB=mnhumBB+mnhumB 
       
        if cnt >0:
                  maxtB=round(mxtmpBB/cnt,2) ; mintB=round(mntmpBB/cnt,2) ; maxhB=round(mxhumBB/cnt,2) ; minhB=round(mnhumBB/cnt,2) ;
        else:
                  maxtB=mxtmpB ; mintB=mntmpB ; maxhB=mxhumB ; minhB=mnhumBB ;

        bias=[maxtB,mintB,maxhB,minhB] ; print bias 
        with open(bsFle,'a')as bsfile:
             csv_bf=csv.writer(bsfile)
             newline=[lid,nme,reqDtt,reqDtt,0,0,maxtB,0,0,mintB,0,0,maxhB,0,0,minhB]
             csv_bf.writerow(newline);
        return bias ;
####################################################################################################################################################################
def correctFcst(date,id,bias):
    lid=str(id) ; bias=bias ; reqDt=dt.datetime.strptime(date,"%Y/%m/%d");reqDt=reqDt.strftime("%Y%m%d") ;
    reqDt1=dt.datetime.strptime(date,"%Y/%m/%d") ; reqDt1=reqDt1.strftime("%Y-%m-%d") ;
    reqDt2=dt.datetime.strptime(date,"%Y/%m/%d") ; reqDt2=reqDt2.strftime("%d%m%y") ;

    fcsFl=fcsFle + reqDt + ".csv" ; crFle=main+ "correctedFcst/3daybiasCorfle"+reqDt+".csv"
    if os.path.isfile(fcsFl):
          print "Forecast File exist:"
    else:
          print "Forecast File do not exist: Exit Correction"
          quit()

    sp="^%s,%s" %(lid,reqDt1) ; #print sp
    pattern=re.compile(sp) ; #sp=lid + "," + reqDt1 +","+ reqDt2 ; print sp
    with open (fcsFl, 'r') as f1, open(crFle,"a") as f2:  
         csv_f2 = csv.writer(f2) 
         for r in f1:
             if pattern.search(r):
                d=r.rstrip(); d=d.split(",")  ; mxtmpF=float(d[5]) ; mntmpF=float(d[4]);mxhumF=float(d[12]) ; mnhumF=float(d[11]);prepF=float(d[14]) ;
                #print mxtmpF,mntmpF,mxhumF,mnhumF,prepF
                mxtmpC=int((mxtmpF-bias[0])) ; mntmpC=int((mntmpF-bias[1])) ; mxhumC=int((mxhumF-bias[2])) ; mnhumC=int((mnhumF-bias[3])) ;  
                #print mxtmpC,mntmpC,mxhumC,mnhumC
                if mxhumC >100:
                   mxhumC=98
                if mntmpC >= mxtmpC:
                     mntmpC= mxtmpC-5
                if mnhumC >= mxhumC:
                     mnhumC= mxhumC-15 
                #print mxtmpC,mntmpC,mxhumC,mnhumC
                newline=[d[0],d[1],d[2],d[3],mntmpC,mxtmpC,d[6],d[7],d[8],d[9],d[10],mnhumC,mxhumC,d[13],d[14],d[15],d[16]]                
                csv_f2.writerow(newline); 

#####################################################################################################################################################################
import os ; import sys ; import numpy as np ; import scipy as sp ; import datetime as dt ; import wget ;
import urllib as urll ; import time ; import urllib2 as urll2 ; import csv ; import re ; import socket ; import errno ; 
#################################################################################################################################################################
date=time.strftime("%Y/%m/%d") ; #date1=dt.datetime.strptime(date,"%Y/%m/%d") ; date1=date1.strftime("%Y%m%d") ;
#date=str(sys.argv[1]);date1=dt.datetime.strptime(date,"%Y/%m/%d") ; date1=date1.strftime("%Y%m%d") ;
main="/home/Data/WRF-NMM18/worldData/00test/"; fcsFle=main+"/internationalcities" ; 

with open("obsdata.lst","r") as lf:
     lst_f=csv.reader(lf)
     for loc in lst_f:
         lCode=loc[2] ; wndCode=loc[1] ; locNme=loc[0] ; #obsFle=main + "obsData/" + wndCode + date1 + ".csv" ; print lCode,wndCode 
         downloadWndData(date,wndCode)
         bias=dataQcheck(date,wndCode,lCode,locNme) 
         correctFcst(date,lCode,bias)
#################################################################################################################################################################
quit()

