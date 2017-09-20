#!/usr/bin/env python

"""
This sample application shows how to extend the basic functionality of a device
to support the ReadPropertyMultiple service.
ReadPropertyMultipleServer.py v0.16.2
"""

import dustmeter

import random
import netifaces
import time

from bacpypes.debugging import bacpypes_debugging, ModuleLogger
from bacpypes.consolelogging import ConfigArgumentParser

from bacpypes.core import run

from bacpypes.primitivedata import Real
from bacpypes.object import AnalogValueObject, Property, register_object_type
from bacpypes.errors import ExecutionError

from bacpypes.app import BIPSimpleApplication
from bacpypes.service.device import LocalDeviceObject
from bacpypes.service.object import ReadWritePropertyMultipleServices

# some debugging
_debug = 0
_log = ModuleLogger(globals())

#
#   ReadPropertyMultipleApplication
#

@bacpypes_debugging
class ReadPropertyMultipleApplication(BIPSimpleApplication, ReadWritePropertyMultipleServices):
    pass

#
#   DustValueProperty
#

@bacpypes_debugging
class DustValueProperty(Property):
    
    def __init__(self, identifier):
        if _debug: DustValueProperty._debug("__init__ %r", identifier)
        Property.__init__(self, identifier, Real, default=None, optional=True, mutable=False)
    def ReadProperty(self, obj, arrayIndex=None):
        if _debug: DustValueProperty._debug("ReadProperty %r arrayIndex=%r", obj, arrayIndex)
        index = arrayIndex
        if index is None:
            index = 0
        if index>1:
            index = 1
        value = 0
        if obj.objectName in dustmeter.DustMeter.DustCount:
            value = dustmeter.DustMeter.DustCount[obj.objectName][index]
        if _debug: DustValueProperty._debug("    - value: %r", value)
        return value

    def WriteProperty(self, obj, value, arrayIndex=None, priority=None, direct=False):
        if _debug: DustValueProperty._debug("WriteProperty %r %r arrayIndex=%r priority=%r direct=%r", obj, value, arrayIndex, priority, direct)
        raise ExecutionError(errorClass='property', errorCode='writeAccessDenied')

#
#   Dust Value Object Type
#

@bacpypes_debugging
class DustAnalogValueObject(AnalogValueObject):
    def __init__(self, **kwargs):
        if _debug: DustAnalogValueObject._debug("__init__ %r", kwargs)
        AnalogValueObject.__init__(self, **kwargs)
        pv = DustValueProperty('presentValue')
        self.add_property(pv)

register_object_type(DustAnalogValueObject)

#
#   __main__
#

def main():
    meterhosts = list()
    meters = list()
    # meterhosts.append('fhlrs232_a19.desy.de')
    meterhosts.append('fhlrs232_a27.desy.de')
    meterhosts.append('fhlrs232_a40.desy.de')
    # meterhosts.append('fhlrs232_a43.desy.de')
    # meterhosts.append('fhlrs232_a49.desy.de')
    # meterhosts.append('fhlrs232_a56.desy.de')
    for h in meterhosts:
        m = dustmeter.DustMeter(h)
        m.start()
        meters.append(m)
        
    ifaces=netifaces.interfaces()
    print ifaces
    iface='wlo1'
    local_ip     = netifaces.ifaddresses(iface)[netifaces.AF_INET][0]['addr']
    local_mask   = netifaces.ifaddresses(iface)[netifaces.AF_INET][0]['netmask']
    local_prefix = sum([bin(int(x)).count('1') for x in local_mask.split('.')])
    local_addr = str(local_ip+'/'+str(local_prefix))
    print iface
    print local_addr

    
    if _debug: _log.debug("initialization")

    this_device = LocalDeviceObject(
        objectName='catkins',
        objectIdentifier=600,
        maxApduLengthAccepted=1024,
        segmentationSupported='segmentedBoth',
        vendorIdentifier=15,
        )

    this_application = ReadPropertyMultipleApplication(this_device, local_addr)

    meter_count = 1
    for h in meterhosts:
        dav = DustAnalogValueObject(objectIdentifier=('analogValue', meter_count), objectName=h)
        _log.debug("    - dav: %r", dav)
        this_application.add_object(dav)
        meter_count += 1
    _log.debug("    - object list: %r", this_device.objectList)

    services_supported = this_application.get_services_supported()
    if _debug: _log.debug("    - services_supported: %r", services_supported)

    this_device.protocolServicesSupported = services_supported.value

    _log.debug("running")

    run()
    for m in meters:
        m.stop()
        m.join()
    print "end of join"

if __name__ == "__main__":
    main()
