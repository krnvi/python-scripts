# -*- coding: utf-8 -*-
"""
Created on Wed Jan 14 18:10:01 2015

@author: operational
"""

def dates_from_to(_from_date, _to_date):
    """Get the last day of every month in a range between two datetime values.
    Return a generator
    """
    start_month = _from_date.month
    tot_months = (_to_date.year-_from_date.year)*12 + _to_date.month

    for month in range(start_month, tot_months + 1):
        # Get years in the date range, add it to the start date's year
        _yr = (month-1)/12 + _from_date.year
        _mon = (month-1) % 12 + 1
        #print _mon ; print _yr
        _day=cl.monthrange(_yr,_mon)[1] ; 
        
        yield dt.datetime(_yr, _mon, _day).strftime('%Y/%m/%d')  #-dt.timedelta(days=1)
        

_from_date=dt.datetime.strptime('20100201','%Y%m%d') ; _to_date=dt.datetime.strptime('20141231','%Y%m%d') ;
_dates=dates_from_to(_from_date,_to_date)
for _dte in _dates:
    print _dte
#_tot_yr=((_to_date.year)-(_from_date.year))    ; _tot_mon=((_to_date.year)-(_from_date.year))*12 ;
        