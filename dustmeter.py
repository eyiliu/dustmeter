import socket
import select
import threading
import time

class DustMeter(threading.Thread):
    defaultProps= {
        'name': 'myDustMeter',
        'host': 'localhost',
        'port':  8888,
        'default_dust': 0,
        'reconnect': True
    }
    
    def __init__(self, **kwargs):
        threading.Thread.__init__(self)
        for attr, value in DustMeter.defaultProps.items():
            if attr not in kwargs:
                kwargs[attr] = value        
        self.name = kwargs['name']
        self.host = kwargs['host']
        self.port = kwargs['port']
        self.reconnect = kwargs['reconnect']
        self.dust_small = kwargs['default_dust']
        self.dust_large = kwargs['default_dust']
        self.is_connected = False
        self.ev = threading.Event()
    def run(self):
        while True:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if s.connect_ex((self.host, self.port)) == 0:
                self.is_connected = True
                print self.name, '#', self.host+':'+str(self.port), 'is connected!'
            else:
                self.is_connected = False
                print self.name, '#', self.host+':'+str(self.port), 'is unreachable!'
                if self.reconnect:
                    print self.name, '#', 'reconnect later'
                    time.sleep(30)
                    continue
                else:
                    print self.name, '#', 'no connection, stop'
                    self.dust_small = DustMeter.defaultProps['default_dust']
                    self.dust_large = DustMeter.defaultProps['default_dust']
                    s.close()
                    break
            inout = [s]
            idel_loop_count = 0
            while True:
                infds, outfds, errfds = select.select(inout, [], [], 0.01)
                if len(infds) != 0:
                    time.sleep(0.1)
                    buf = s.recv(64)
                    if len(buf) != 0:
                        idel_loop_count = 0;
                        [small_str, large_str] = buf.split(',')
                        self.dust_small=int(small_str)
                        self.dust_large=int(large_str)
                        print self.name, '#', 'receive data:', repr(buf)
                if self.ev.wait(30):
                    self.ev.clear()
                    print self.name, '#', 'close connection by user'
                    self.dust_small = DustMeter.defaultProps['default_dust']
                    self.dust_large = DustMeter.defaultProps['default_dust']
                    self.is_connected = False
                    s.close()
                    return
                else:
                    idel_loop_count += 1
                    if(idel_loop_count > 4):
                        print self.name, '#','no incoming data, closing connection'
                        self.dust_small = DustMeter.defaultProps['default_dust']
                        self.dust_large = DustMeter.defaultProps['default_dust']
                        self.is_connected = False
                        s.close()
                        break
        
    def stop(self):
        self.ev.set()
    
if __name__ == "__main__":

    d = DustMeter(name = 'mydustmeter_somewhere', host = 'fhlrs232_a27.desy.de')
    d.start()
    time.sleep(70)
    print 'wake up'
    d.stop()
    print 'stop 0'
    d.join()
    print 'join 0'
