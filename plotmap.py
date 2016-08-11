"""
To install basemap, follow:
http://gnperdue.github.io/yak-shaving/osx/python/matplotlib/2014/05/01/basemap-toolkit.html

but may also need to do something like
sudo pip uninstall python-dateutil
sudo pip install python-dateutil==2.2
pip install Pillow

Call this script like
python plotmap.py -l US -z inputfile.csv -o outputfile.png

"""
from mpl_toolkits.basemap import Basemap 
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np
import pandas as pd
import math
import re
import sys
import argparse


def set_up_map_projection(locale):
    print "setting up map projection"
    if locale =='US':
        return Basemap(projection='merc', 
                        llcrnrlat=22, urcrnrlat=50,\
                        llcrnrlon=-125, urcrnrlon=-65, 
                        lat_ts=43, resolution='l')
    elif locale =='UK':
        return Basemap(projection='merc', 
                        llcrnrlat=48, urcrnrlat=60,\
                        llcrnrlon=-12, urcrnrlon=4, 
                        lat_ts=53, resolution='i')
    else:
        print 'Locale must be US or UK'
        sys.exit()

def draw(m_map, locale):
    print "drawing..."
    m_map.drawcountries()
    m_map.drawcoastlines()
    m_map.fillcontinents(color='antiquewhite', lake_color='aqua')
    m_map.shadedrelief()  # color ocean 
    m_map.drawmapboundary(fill_color='aqua')

    # draw parallels and meridians
    spacing = 10. if locale=='US' else 5.
    parallels = np.arange(-180., 180., spacing)
    m_map.drawparallels(parallels,labels=[False,True,True,False])
    meridians = np.arange(-180., 180., spacing)
    m_map.drawmeridians(meridians,labels=[True,False,False,True])

def read_csv(zipcodefile, locale):
    ZIPs = pd.read_csv(zipcodefile).iloc[:,0]
    ZIPs = ZIPs[~pd.isnull(ZIPs)]
    if locale=='UK': # some further processing of codes
        ZIPs = pd.Series([x.split()[0] for x in ZIPs])

    return ZIPs

# count number of letters by area
def zip_counts(zips):
    cts = zips.value_counts()
    zips = map(str, cts.axes[0].values)
    cts = dict(zip(zips, list(cts)))

    return cts

def color_zipcodes(m_map, maxcts, locale, cts):
    print "coloring zipcodes..."
    if maxcts == 0: maxcts = 0.25*max(map(int, cts.values()))
    if locale == 'US':
        m_map.readshapefile('shapefiles/tl_2015_us_zcta510/tl_2015_us_zcta510', 'zip', drawbounds = False)
        key = 'ZCTA5CE10'
    else:
        m_map.readshapefile('shapefiles/Districts/Districts', 'zip', drawbounds = False)
        key = 'name'
    for shapedict, shape in zip(m_map.zip_info, m_map.zip):
        zipcode = str(shapedict[key])
        if zipcode not in cts:
            col = '#ffffff'
        else:
            x = min(cts[zipcode], maxcts)/(1.0*maxcts)
            col = colors.rgb2hex((1., 1.-x, 1.-x))
        xx, yy = zip(*shape)
        plt.fill(xx, yy, color = col)


def plot_cities(m_map, lon1, lon2, lat1, lat2, name, xoffset = -80000, yoffset = 30000):
    print "plotting city..."
    xpt, ypt = m_map(lon1 + lon2/60.0, lat1 + lat2/60.0) 
    m_map.plot(xpt, ypt, 'k.')
    plt.text(xpt + xoffset, ypt + yoffset, name, size='6')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--locale', help='US or UK locale.')
    parser.add_argument('-m', '--max', help='full color saturation when letters >= maxcts, 0 for default ')
    parser.add_argument('-z', '--zipcode', help="input CSV file with single column zip codes, like: ZIPs/046ZIPs.csv")
    parser.add_argument('-o', '--out', help="path and name to output image, like: map.png")

    args = parser.parse_args()
    
    locale = args.locale if args.locale else 'US'
    maxcts = args.max if args.max else 0 
    zipcodefile = args.zipcode if args.zipcode else 'ZIPs/046ZIPs.csv' 
    outputfile = args.out if args.out else 'map.png'

    m = set_up_map_projection(locale)

    draw(m, locale)        
    zips = read_csv(zipcodefile, locale)
    cts = zip_counts(zips)
    color_zipcodes(m, maxcts, locale, cts)

    plot_cities(m, -87, -41, 41, 50, 'Chicago', -300000, 40000)
    plot_cities(m, 0, -7, 51, 30, 'London')
    plot_cities(m, -118, -15, 34, 3, 'Los Angeles', yoffset = 40000)

    plt.savefig(outputfile, dpi=300)
    print "saved file - DONE!"


if __name__ == "__main__":
    main()

