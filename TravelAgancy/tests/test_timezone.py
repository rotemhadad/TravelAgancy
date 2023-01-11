from datetime import datetime
import pytz


utc_tz = pytz.timezone('UTC')
china_tz = pytz.timezone('America/New_York')
local_naive = datetime.now(tz=utc_tz)
print(local_naive)
local_aware = datetime.now() 
print(local_aware)


local_aware_to_naive = datetime.now(tz=china_tz)
print(local_aware_to_naive)
if local_aware_to_naive > local_naive:
    print('yes')


mySet = set()
if len(mySet) == 0:
    print('hahh')