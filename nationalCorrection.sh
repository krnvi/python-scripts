#!/bin/bash

main=/home/Data/poolLatestWorkByModelTeam/nationalCor/ ; scripts=$main/scripts ; cfcst=$main/correctedFcst
date=`date +%Y%m%d`00 ; date1=`date -d"${date:0:8} + 0days" +%Y/%m/%d`
#date=$1\00 ; date1=`date -d"${date:0:8} + 0days" +%Y/%m/%d`

cd ${cfcst}
cp /home/Data/modelWRF/CommonPool/output//24hourly${date}.csv ./uncorrectTmpfile.csv
cat $scripts/national_obsdata.lst | while IFS=, read loc wndcode pid ; do 
cat ./uncorrectTmpfile.csv | grep "^$pid," >>correctTmpfile.csv
sed "/^$pid,/d" ./uncorrectTmpfile.csv >>Tmpfile.csv
mv Tmpfile.csv uncorrectTmpfile.csv
done

cd ${scripts}
/usr/bin/python ${scripts}/nationalCorrection-3daybias.py $date1

nolinC=`wc -l < $main/correctedFcst/3daybiasCorfle${date}.csv`
nolinU=`wc -l < ${cfcst}/uncorrectTmpfile.csv`
if [ ${nolinC} -eq 544 ]; then
   
     cd ${cfcst}
     sed -n "1, 1p" ${cfcst}/uncorrectTmpfile.csv >${cfcst}/24hourly${date}.csv
     cat ${cfcst}/3daybiasCorfle${date}.csv >>${cfcst}/24hourly${date}.csv
     sed -n "2, ${nolinU}p" ${cfcst}/uncorrectTmpfile.csv >>${cfcst}/24hourly${date}.csv

     dos2unix ${cfcst}/24hourly${date}.csv
     rm uncorrectTmpfile.csv correctTmpfile.csv 
else
     echo "Correction Failed"
     exit
fi

cd ${scripts}
sh accuracy.sh
exit 
