from django.test import TestCase

# Create your tests here.

import requests
from math import radians, cos, sin, asin, sqrt

#使用百度API
def geocodeB(address):
    base = url = "http://api.map.baidu.com/geocoder?address=" + address + "&output=json&key=f247cdb592eb43ebac6ccd27f796e2d2"
    response = requests.get(base)
    answer = response.json()
    return answer['result']['location']['lng'],answer['result']['location']['lat']

#计算两点间距离-m
def geodistance(lng1,lat1,lng2,lat2):
    lng1, lat1, lng2, lat2 = map(radians, [lng1, lat1, lng2, lat2])
    dlon=lng2-lng1
    dlat=lat2-lat1
    a=sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    dis=2*asin(sqrt(a))*6371*1000
    return dis

if __name__ == "__main__":
    adders1 = geocodeB('深圳')
    print(adders1)
    adders2 = geocodeB('广州')
    print(adders2)
    print('-'*10)
    lng1, lat1 = adders1
    lng2, lat2 = adders2
    length = geodistance(lng1,lat1,lng2,lat2)
    print('距离等于 ： ', length)


