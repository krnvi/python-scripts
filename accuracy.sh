#!/bin/bash

main=/home/Data/poolLatestWorkByModelTeam/nationalCor/ ; scripts=$main/scripts
#dt=`date -d"${1:0:8}" +%Y%m%d` ;
dt=`date +%Y%m%d` ; date=`date +%Y/%m/%d`

prevdt=`date -d"$dt -1days" +%Y%m%d`00 ; EMAIL_ID="vineethpk@skymet.net basanta.samal@skymetweather.com gpsharma@skymet.net" 
#gpsharma@skymet.net
cd ${scripts}
python ${scripts}/nationalAccuracy.py $date

cd $main/correctedFcst

cat national_bias${prevdt}.csv | awk -F, '$5!="0.1"{print $0}' >>$main/national_bias${prevdt:0:10}.csv

echo "national accuracy files" | mutt -a $main/national_bias${prevdt:0:10}.csv -s "national accuracy files " -- $EMAIL_ID

#scp $main/national_bias${prevdt:0:8}.csv operational@192.168.103.195:/home/Data/dataPortalImages/images/shortcompare/
rm $main/national_bias${prevdt:0:8}.csv
exit 
