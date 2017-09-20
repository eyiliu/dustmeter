import socket
import select
import threading
import time

class DustMeter(threading.Thread):
    DustCount = dict()
    g_locker = threading.Lock()
    def __init__(self, host='localhost', port=8888):
        threading.Thread.__init__(self)
        threading.Thread.setName(self, host+':'+str(port))
        self.host = host
        self.port = port
        self.addr = host+':'+str(port)
        self.dust_small = -1
        self.dust_large = -1
        self.ev = threading.Event()
        DustMeter.g_locker.acquire()
        DustMeter.DustCount[self.host] = [self.dust_small, self.dust_large]
        DustMeter.g_locker.release()
    def __del__(self):
        self.__class__.g_locker.acquire()
        self.__class__.DustCount.pop(self.host, None)
        self.__class__.g_locker.release()
    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if s.connect_ex((self.host, self.port)) != 0:
            print 'the host/port is unreachable!', self.host, self.port
            return
        inout = [s]
        idel_loop_count = 0
        while 1:
            infds, outfds, errfds = select.select(inout, [], [], 0.01)
            if len(infds) != 0:
                time.sleep(0.1)
                buf = s.recv(64)
                if len(buf) != 0:
                    idel_loop_count = 0;
                    [small_str, large_str] = buf.split(',')
                    self.dust_small=int(small_str)
                    self.dust_large=int(large_str)
                    print '<', self.host, '>', 'receives data:', repr(buf)
                    DustMeter.g_locker.acquire()
                    DustMeter.DustCount[self.host] = [self.dust_small, self.dust_large]
                    # print repr(DustMeter.DustCount)
                    DustMeter.g_locker.release()
            if self.ev.wait(30):
                self.ev.clear()
                break;
            else:
                idel_loop_count += 1
                if(idel_loop_count > 4):
                    print 'no incoming data, stop connection'
                    break;
                
        s.close()
        self.dust_small = -1
        self.dust_large = -1
        DustMeter.g_locker.acquire()
        DustMeter.DustCount[self.host] = [-1, -1]
        DustMeter.g_locker.release()
    def stop(self):
        self.ev.set()
        
if __name__ == "__main__":
    HOST_0 = 'localhost'
    dustmeter_0 = DustMeter(HOST_0)
    dustmeter_0.start()

    HOST_1 = 'fhlrs232_a27.desy.de'
    dustmeter_1 = DustMeter(HOST_1)
    dustmeter_1.start()

    time.sleep(70)
    print 'wake'
    dustmeter_0.stop()
    print 'stop 0'
    dustmeter_0.join()
    print 'join 0'

    dustmeter_1.stop()
    print 'stop 1'
    dustmeter_1.join()
    print 'join 1'
