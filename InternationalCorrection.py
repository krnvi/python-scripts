#!/home/Data/python/python/bin/python2.7

#################################################################################################################################################################

def downloadWndData(date,code):
        def readurl(url):
           web=urll2.Request(url) ;
           try:
                htm = urll2.urlopen(web) ; cont=htm.read() ; #print dat
                f=open("tmpFle","w") ; f.write(cont); f.close();
           except urll2.HTTPError as e:
                url1=e.geturl() ; print url1 ; readurl(url1)
                #raise Exception('Error opening %s: %s' % (e.geturl(), e))
                #print "Error"
                pass
           except urll2.URLError as e:
                url1=e.geturl() ; print url1 ; readurl(url1)
                #raise Exception('Error opening %s: %s' % (e.geturl(), e))
                pass

        wndCode=code ; reqDt=dt.datetime.strptime(date,"%Y/%m/%d") + dt.timedelta(days=-1);date=reqDt.strftime("%Y/%m/%d")
        url="http://www.wunderground.com/history/airport/" + wndCode + "/" + date + "/MonthlyHistory.html?format=1" ;
        readurl(url)

	#web=urll.URLopener() ; web.retrieve(url,"tmpFle")
	#web=wget.download(url, out=outFle)
	with open("tmpFle", "rb") as infile, open(obsFle, "wb") as outfile:
	     csv_f1 = csv.reader(infile) ;  csv_f2 = csv.writer(outfile) 
	     conversion = set('<br />')  ;  csv_f1.next() 
	     for r in csv_f1:
        	 newline = [''.join(' ' if c in conversion else c for c in entry) for entry in r] 
	         csv_f2.writerow(newline)
	os.remove("tmpFle")

#####################################################################################################################################################################
def dataQcheck(date,code,id):
        lid=str(id);wndCode=code ; reqDt=dt.datetime.strptime(date,"%Y/%m/%d") + dt.timedelta(days=-1);reqDt=reqDt.strftime("%Y-%m-%-d") ;
        reqDt1=dt.datetime.strptime(date,"%Y/%m/%d")+ dt.timedelta(days=-2) ; reqDt1=reqDt1.strftime("%Y-%m-%d") ;
        reqDt2=dt.datetime.strptime(date,"%Y/%m/%d")+ dt.timedelta(days=-1) ; reqDt2=reqDt2.strftime("%d%m%y") ;
        reqDt3=dt.datetime.strptime(date,"%Y/%m/%d") + dt.timedelta(days=-2); reqDt3=reqDt3.strftime("%Y%m%d")
        fcsFl=fcsFle + reqDt3 + ".csv" ; print fcsFl ; print obsFle ; print reqDt 
        #os.system('cat %s |grep %s '%(obsFle,reqDt)) ; 
        pattern=re.compile(reqDt) ; sp="^%s,%s,%s" %(lid,reqDt1,reqDt2);pattern1=re.compile(sp) ; print sp
	with open (obsFle,'r') as f:
             ln_pos=f.tell() ; rows=list(f) ; nrows=len(rows) ; f.seek(ln_pos)
             if nrows <= 1:
                 with open (fcsFl,'r') as f1:
                      for rr in f1:
                          if pattern1.search(rr):
                             dd=rr.rstrip(); dd=dd.split(",");fdt=reqDt;mxtmp=float(dd[5]);mntmp=float(dd[4]);
                             mxhum=float(dd[12]);mnhum=float(dd[11]);prep=float(dd[14]);
                             #print mxtmp,mntmp,mxhum,mnhum,prep
             else:
 
                 ln_pos=f.tell();f.next() ; line=f.next();ln=line.split(",");fs=ln[0];fs=fs[0:4];fs1=reqDt[0:4];
                 if fs == fs1:
                    print "file is correct"
                 else:
                    print "file is incorrect"
                    downloadWndData(date,wndCode)  
                 f.seek(ln_pos)
                 hd=f.next(); hdr=hd.split(",") ; mxtphd=hdr[1];mntphd=hdr[3] ;
                 #fdt=reqDt; mxtmp=float(0) ; mntmp=float(0) ; mxhum=float(0);mnhum=float(0);prep=float(0) 
                 for r in f:
                     if pattern.search(r):
                        d=r.split(",") ;#print len(d[1])
                        if len(d[1]) >0 and len(d[3]) and len(d[7]) and len(d[9]):
                               #print d[1],d[3],d[7],d[9],d[19]
                               fdt=d[0] ; mxtmp=float(d[1]) ; mntmp=float(d[3]) ; mxhum=float(d[7]);mnhum=float(d[9]);prep=d[19];
                               #print fdt,mxtmp,mntmp,mxhum,mnhum,prep
                         
                               if mxtphd.endswith("F"):
                                          mxtmp=((mxtmp)-32) / 1.80 ; mntmp=((mntmp)-32) / 1.80 ;         
                               else:
                                          mxtmp=mxtmp ; mntmp=mntmp ;
                        else:
                               
                               with open (fcsFl,'r') as f1:
                                    for rr in f1:
                                        if pattern1.search(rr):
                                              dd=rr.rstrip(); dd=dd.split(","); fdt=20141116 ; mxtmp=float(dd[5]);mntmp=float(dd[4]);
                                              
                                              mxhum=float(dd[12]);mnhum=float(dd[11]);prep=float(dd[14]);
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
    fcsFl=fcsFle + reqDt + ".csv" ; bsFle=main+"correctedFcst/biasfile"+reqDtt+".csv" ; print fcsFl
    sp="^%s,%s,%s" %(lid,reqDt1,reqDt2) ;print sp
    pattern=re.compile(sp) ;#sp=lid + ',' + reqDt1 +','+ reqDt2 ; #print sp
    with open (fcsFl,'r') as f1, open(bsFle,"a") as f2:
         csv_f2=csv.writer(f2);  #csv_f2.writenow(header) 
         for r in f1:
             if pattern.search(r):
                d=r.split(",") ; mxtmpF=float(d[5]) ; mntmpF=float(d[4]);mxhumF=float(d[12]) ; mnhumF=float(d[11]);prepF=float(d[14]) ;
                #print mxtmpF,mntmpF,mxhumF,mnhumF,prepF
                mxtmpB=mxtmpF-obsdat[1] ; mntmpB=mntmpF-obsdat[2] ; mxhumB=mxhumF-obsdat[3] ; mnhumB=mnhumF-obsdat[4] ;  #print mxtmpB,mntmpB,mxhumB,mnhumB
                bias=[mxtmpB,mntmpB,mxhumB,mnhumB] ;
                newline=[d[0],nme,d[1],d[3],mxtmpF,obsdat[1],mxtmpB,mntmpF,obsdat[2],mntmpB,mxhumF,obsdat[3],mxhumB,mnhumF,obsdat[4],mnhumB]
                csv_f2.writerow(newline);
    return bias
####################################################################################################################################################################
def correctFcst(date,id,bias):
    lid=str(id) ; bias=bias ; reqDt=dt.datetime.strptime(date,"%Y/%m/%d");reqDt=reqDt.strftime("%Y%m%d") ;
    reqDt1=dt.datetime.strptime(date,"%Y/%m/%d") ; reqDt1=reqDt1.strftime("%Y-%m-%d") ;
    reqDt2=dt.datetime.strptime(date,"%Y/%m/%d") ; reqDt2=reqDt2.strftime("%d%m%y") ;

    fcsFl=fcsFle + reqDt + ".csv" ; crFle=main+"correctedFcst/corfle"+reqDt+".csv" ; print fcsFl
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
import urllib as urll ; import time ; import urllib2 as urll2 ; import csv ; import re ; 
#################################################################################################################################################################
date=time.strftime("%Y/%m/%d") ; #date=str(sys.argv[1]);
date1=dt.datetime.strptime(date,"%Y/%m/%d") ; date1=date1.strftime("%Y%m%d") ;
#fcsFle="/home/Data/WRF-NMM18/worldData/00test/internationalcities" ; 
main="/home/Data/WRF-NMM18/worldData/00test/" ; fcsFle=main + "internationalcities" ;
with open("obsdata.lst","r") as lf:
     lst_f=csv.reader(lf)
     for loc in lst_f:
         lCode=loc[2] ; wndCode=loc[1] ; locNme=loc[0] ; obsFle=main + "obsData/" + wndCode + date1 + ".csv" ; print lCode,wndCode 
         downloadWndData(date,wndCode)
         obsData=dataQcheck(date,wndCode,lCode) 
         bias=findBias(date,lCode,locNme,obsData)
         correctFcst(date,lCode,bias)
#################################################################################################################################################################
quit()

