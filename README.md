# DUSTMETER

* the setup will present a [BACNET](https://en.wikipedia.org/wiki/BACnet) device with a collection of [AnalogInputObjects](http://www.bacnet.org/Bibliography/ES-7-96/ES-7-96.htm).
* The AnalogInputObjects are the readout of the remote DustMeters which are bridged by RS232-Ethernet adapters.

## Hardware device
* [DYLOS DC1700 air quality monitor](http://www.dylosproducts.com/dc1700.html)
* [USR-TCP232-302](http://www.usriot.com/user-manual-usr-tcp232-302-user-manual/) on TCP server mode listening at 8888 port

## Software dependencies:
* python 2.7
* [bacpypes](https://github.com/JoelBender/bacpypes) 0.16.3

### Install bacpypes
```
pip2.7 install bacpypes==0.16.3
```

## How to run:
```
python2.7 dustserver.py
```
Please make sure previous seesion of dustserer.py have exited and relased the network port.

## Note:
BACNET DeviceObject ID can be calculated by 22 bits (LSB) of the MAC address

## Repository
Updated code is available by [github repository](https://github.com/eyiliu/dustmeter)