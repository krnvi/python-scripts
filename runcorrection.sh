#!/bin/bash

main=/home/Data/WRF-NMM18/worldData/00test/ ; scripts=$main/scripts
#dt=`date -d"${1:0:8}" +%Y%m%d` ;
dt=`date +%Y%m%d`
echo `date`
cd ${scripts}
/usr/bin/python ${scripts}/InternationalCorrection-3daybias.py

echo `date`

nolines=`wc -l < $main/correctedFcst/3daybiasCorfle${dt}.csv`
if [ ${nolines} -eq 5032 ] ; then 
   echo "Correction completed successfully"
   sed -n "1, 1p" $main/internationalcities${dt}.csv >$main/correctedFcst/internationalcities${dt}.csv
   cat $main/correctedFcst/3daybiasCorfle${dt}.csv >>$main/correctedFcst/internationalcities${dt}.csv
   sed -n "5034, 662177p" $main/internationalcities${dt}.csv >>$main/correctedFcst/internationalcities${dt}.csv


   dos2unix $main/correctedFcst/internationalcities${dt}.csv

   /usr/bin/scp -r $main/correctedFcst/internationalcities${dt}.csv wrfwest@192.168.103.44:/home/commonpool/modeloutput/worldcity
   cp -r $main/correctedFcst/internationalcities${dt}.csv /home/commonpool/modeloutput/worldcity
else
   echo "Correction unsuccessfull:Row Forecast file will be copied"
   /usr/bin/scp -r $main/internationalcities${dt}.csv wrfwest@192.168.103.44:/home/commonpool/modeloutput/worldcity
   cp -r $main/internationalcities${dt}.csv /home/commonpool/modeloutput/worldcity
fi

cd $scripts
sh accuracy.sh 

exit 
