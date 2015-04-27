#!/bin/bash

main=/home/Data/poolLatestWorkByModelTeam/nationalCor/ ; scripts=$main/scripts
#dt=`date -d"${1:0:8}" +%Y%m%d` ;
dt=`date +%Y%m%d` ; date=`date +%Y%m%d`
prevdt1=`date -d"$dt -1days" +%Y%m%d`
prevdt=`date -d"$dt -2days" +%Y%m%d` ; EMAIL_ID="basanta106@gmail.com vineethpk@skymet.net basanta.samal@skymetweather.com gpsharma@skymet.net maheshpalawat@skymet.net" 

cd ${scripts}
python -W ignore ${scripts}/pradanDailyAccuracy.py $date

cd $main/pradan

#cat national_bias${prevdt}.csv | awk -F, '$5!="0.1"{print $0}' >>$main/national_bias${prevdt:0:10}.csv

echo "pradan accuracy " | mutt -a $main/pradan/pradanDailyBias_${prevdt:0:8}.csv -s "pradan accuracy files " -- $EMAIL_ID

#rm $main/national_bias${prevdt:0:8}.csv

scp -r $main/pradan/pradanDailyObs_${prevdt1:0:8}.csv wrfwest@192.168.103.44:/home/commonpool/pradan/
scp -r $main/pradan/pradanDailyBias_${prevdt1:0:8}.csv wrfwest@192.168.103.44:/home/commonpool/pradan/
exit 
