from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np
import pandas as pd
import math
import re
import sys

# parameters
LOCALE = 'US'
MAXCTS = 100 # full color saturation when letters >= MAXCTS, 0 for default 
ZIPCODEFILE = 'ZIPs/046ZIPs.csv' # single column CSV with ZIPs of each letter
OUTPUTFILE = 'map.png' # path/name of output image 

# set up the map projection 
if LOCALE=='US':
    m = Basemap(projection='merc', 
                llcrnrlat=22, urcrnrlat=50,\
                llcrnrlon=-125, urcrnrlon=-65, 
                lat_ts=43, resolution='l')
elif LOCALE=='UK':
    m = Basemap(projection='merc', 
                llcrnrlat=48, urcrnrlat=60,\
                llcrnrlon=-12, urcrnrlon=4, 
                lat_ts=53, resolution='i')
else:
    print 'Locale must be US or UK'
    sys.exit()
    
# draw political boundaries
m.drawcountries()

# draw coastlines
m.drawcoastlines()

# color continents
m.fillcontinents(color='antiquewhite', lake_color='aqua')

# color ocean 
m.shadedrelief()

# draw a boundary around the map
m.drawmapboundary(fill_color='aqua')

# draw parallels and meridians
spacing = 10. if LOCALE=='US' else 5.
parallels = np.arange(-180., 180., spacing)
m.drawparallels(parallels,labels=[False,True,True,False])
meridians = np.arange(-180., 180., spacing)
m.drawmeridians(meridians,labels=[True,False,False,True])

# read in the CSV of ZIP codes (or postal codes) 
ZIPs = pd.read_csv(ZIPCODEFILE).iloc[:,0]
ZIPs = ZIPs[~pd.isnull(ZIPs)]
if LOCALE=='UK': # some further processing of codes
    ZIPs = pd.Series([x.split()[0] for x in ZIPs])

# count number of letters by area
cts = ZIPs.value_counts()
zips = map(str, cts.axes[0].values)
cts = dict(zip(zips, list(cts)))

# color the ZIP codes 
if MAXCTS==0: MAXCTS = 0.25*max(map(int, cts.values()))
if LOCALE=='US':
    m.readshapefile('shapefiles/tl_2015_us_zcta510/tl_2015_us_zcta510', 'zip', drawbounds = False)
    key = 'ZCTA5CE10'
else:
    m.readshapefile('shapefiles/Districts/Districts', 'zip', drawbounds = False)
    key = 'name'
for shapedict, shape in zip(m.zip_info, m.zip):
    zipcode = str(shapedict[key])
    if zipcode not in cts:
        col = '#ffffff'
    else:
        x = min(cts[zipcode], MAXCTS)/(1.0*MAXCTS)
        col = colors.rgb2hex((1., 1.-x, 1.-x))
    xx, yy = zip(*shape)
    plt.fill(xx, yy, color = col)

# function to mark cities
def plot_cities(lon1, lon2, lat1, lat2, name, xoffset = -80000, yoffset = 30000):
    xpt, ypt = m(lon1 + lon2/60.0, lat1 + lat2/60.0) 
    m.plot(xpt, ypt, 'k.')
    plt.text(xpt + xoffset, ypt + yoffset, name, size='6')

plot_cities(-87, -41, 41, 50, 'Chicago', -300000, 40000)
plot_cities(0, -7, 51, 30, 'London')
plot_cities(-118, -15, 34, 3, 'Los Angeles', yoffset = 40000)

# save map
plt.savefig(OUTPUTFILE, dpi=300)



