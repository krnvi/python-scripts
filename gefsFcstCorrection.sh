#!/bin/bash

main=/home/OldData/gefsData ; scripts=$main/scripts ;
date=`date +%Y%m%d`
#date=$1  

cd ${scripts}
/usr/bin/python ${scripts}/gefsFcstCorrection.py $date



cat national_obsdata.lst | while IFS=, read loc wcode id ; do
grep "^$id," $main/24hourlyoutput/$date/24hourlygefscorrected$date.csv >>$main/24hourlyoutput/70loc_C_15day/24hourlygefscorrect$date.csv 
done
scp $main/24hourlyoutput/70loc_C_15day/24hourlygefscorrect$date.csv wrfwest@192.168.103.44:/home/commonpool/clients/70loc_C_15day/

exit 
