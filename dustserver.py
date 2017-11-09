#!/usr/bin/env python

import netifaces
import time
import threading

import dustmeter

from bacpypes.core import run
from bacpypes.debugging import bacpypes_debugging, ModuleLogger
from bacpypes.errors import ExecutionError

from bacpypes.primitivedata import Real, CharacterString, Unsigned, Boolean
from bacpypes.basetypes import EngineeringUnits
from bacpypes.object import AnalogInputObject, Property

from bacpypes.app import BIPSimpleApplication
from bacpypes.service.device import LocalDeviceObject
from bacpypes.service.object import ReadWritePropertyMultipleServices

class dataThread(threading.Thread):
    def __init__(self, meters, objs):
        threading.Thread.__init__(self)
        threading.Thread.setName(self, 'dataThread')
        self.meters = meters
        self.objs = objs
        self.flag_stop = False
    def run(self):
        while not self.flag_stop:
            time.sleep(1)
            for obj in self.objs:
                objname = str(obj._values['objectName'])
                for meter in self.meters:
                    if meter.name == objname:
                        obj._values['outOfService'] = Boolean(not meter.is_connected)
                        obj._values['presentValue'] = Real(meter.dust_small*100)
                        
    def stop(self):
        self.flag_stop = True

def main():
    device_info = {
        'ip': '10.169.204.200',
        'netmask': 23,
        'port': 47809,
        'objectName': 'FHL-DAF-DUSTMETER',
        'objectIdentifier': 522020,
        'vendorIdentifier': 15,
        'location': 'FHL-DAF-CLEAN-ROOM',
        'vendorName': 'DESY-ATLAS',
        'modelName': 'DUST-METERS',
        'softwareVersion': 'bacpypes_v0.16.2_py27',
        'description': 'FHL-DAF clean room dustmeter server'
    }

    print device_info
    
    this_device = LocalDeviceObject(
        objectName=device_info['objectName'],
        objectIdentifier=device_info['objectIdentifier'],
        vendorIdentifier=device_info['vendorIdentifier']
    )
    
    this_device._values['location'] = CharacterString(device_info['location'])
    this_device._values['vendorName'] = CharacterString(device_info['vendorName'])
    this_device._values['modelName'] = CharacterString(device_info['modelName'])
    this_device._values['applicationSoftwareVersion'] = CharacterString(device_info['softwareVersion'])
    this_device._values['description'] = CharacterString(device_info['description'])
    
    this_addr = str(device_info['ip']+'/'+str(device_info['netmask'])+':'+str(device_info['port']))
    print 'bacnet server will listen at', this_addr
    this_application = BIPSimpleApplication(this_device, this_addr)
    this_application.add_capability(ReadWritePropertyMultipleServices)
    this_device.protocolServicesSupported = this_application.get_services_supported().value

    meter_info = [
        {'name': 'dustmeter_a19',
         'index': 1,
         'host': 'fhlrs232_a19.desy.de',
         'description': 'dustmeter on RS232-Ethernet bridge at somewhere',
        },
        {'name': 'dustmeter_a27',
         'index': 2,
         'host': 'fhlrs232_a27.desy.de',
         'description': 'dustmeter on RS232-Ethernet bridge at somewhere',
        },
        {'name': 'dustmeter_a40',
         'index': 3,
         'host': 'fhlrs232_a40.desy.de',
         'description': 'dustmeter on RS232-Ethernet bridge at somewhere',
        },
        {'name': 'dustmeter_a43',
         'index': 4,
         'host': 'fhlrs232_a43.desy.de',
         'description': 'dustmeter on RS232-Ethernet bridge at somewhere',
        },
        {'name': 'dustmeter_a49',
         'index': 5,
         'host': 'fhlrs232_a49.desy.de',
         'description': 'dustmeter on RS232-Ethernet bridge at somewhere',
        },
        {'name': 'dustmeter_a56',
         'index': 6,
         'host': 'fhlrs232_a56.desy.de',
         'description': 'dustmeter on RS232-Ethernet bridge at somewhere',
        },
    ]
    
    meters = []
    for info in meter_info:
        m = dustmeter.DustMeter(name = info['name'], host = info['host'])
        m.start()
        meters.append(m)
    
    objs = []
    for info in meter_info:
        ai_obj = AnalogInputObject(objectIdentifier=('analogInput', info['index']), \
                                   objectName=info['name'])
        ai_obj._values['description'] = CharacterString(info['description'])
        ai_obj._values['deviceType'] = CharacterString('Particles(>0.5um) PerCubicFoot')
        ai_obj._values['units'] = EngineeringUnits('noUnits')
        ai_obj._values['updateInterval'] = Unsigned(60)
        ai_obj._values['resolution'] = Real(100)
        this_application.add_object(ai_obj)
        objs.append(ai_obj)

    mythread = dataThread(meters, objs)
    mythread.start()
    
    run()
    
    mythread.stop()
    mythread.join()
    for m in meters:
        m.stop()
        m.join()
    print "end of join"

if __name__ == "__main__":
    main()
