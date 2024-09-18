
from zhinst.toolkit import Session

import time as t
import numpy as np 
import sys 
this = sys.modules[__name__]
this.samplingrate = 5400
def connect(int_time):
    """Connect to any available device 

    Returns:
        device: The access port of a give device 
        Session: The scope of the devices which holds data etc
    """
    session = Session("localhost",hf2=True)
    avbdev = session.devices.visible()
    print(avbdev[0])
    device = session.connect_device(avbdev[0])
    device.demods[0].enable(1)
    TOTAL_DURATION = int_time
    this.samplingrate = device.demods[0].rate()
    return device,session
def daqdata(device,session,inttime):
    """_summary_

    Args:
        device (_type_): _description_
        session (_type_): _description_
        daq_module (_type_): _description_
        inttime (_type_): _description_

    Returns:
        _type_: _description_
    """
    a = session.poll(.0001)
    poll_results = session.poll(inttime)
    x= poll_results[device.demods[0].sample]['x']
    y= poll_results[device.demods[0].sample]['y']
    r= np.sqrt(x**2+y**2)
    #print('poll end')
    return r
