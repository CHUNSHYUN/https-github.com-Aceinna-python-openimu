import time
import socket
from ..constants import (BAUDRATE_LIST, INTERFACES)
from ..utils.print import (print_red, print_yellow)
from ..wrapper import SocketConnWrapper
from ..communicator import Communicator
from .netbios import netbios_query

greeting = 'i am pc'

def get_network_interfaces():
    host = socket.gethostname()
    _, _, ip_addr_list = socket.gethostbyname_ex(host)
    return ip_addr_list


class LAN(Communicator):
    '''LAN'''
    _find_client_retries = 0

    def __init__(self, options=None):
        super().__init__()
        self.type = INTERFACES.ETH
        self.host = None
        self.port = 2203  # TODO: predefined or configured?

        self.sock = None
        self.device_conn = None
        self.filter_device_type = None
        self.filter_device_type_assigned = False

        if options and options.device_type != 'auto':
            self.filter_device_type = options.device_type
            self.filter_device_type_assigned = True

    def find_device(self, callback, retries=0, not_found_handler=None):
        self.device = None

        # get avaliable network interface
        ip_address_list = get_network_interfaces()

        # find client by hostname
        can_find, ip_address = self.find_client_by_hostname('OPENRTK', ip_address_list)

        if not can_find:
            print_red(
                '[Error] We detected the device for a long time, please make sure the device is connected with LAN port')
            return

        conn = None
        can_use_address_list=[]

        if ip_address:
            can_use_address_list = [ip_address]
        else:
            can_use_address_list = ip_address_list
        
        for ip_address in can_use_address_list:
            # establish TCP Server
            socket_host = self.establish_host(ip_address)
            # wait for client
            try:
                conn, _ = socket_host.accept()
                self.sock = conn
                self.host = ip_address
                break
            except:
                conn = None
                if socket_host:
                    socket_host.close()
                print_yellow(
                    '[Warn] Socket host accept error on {0}'.format(ip_address))

        if not conn:
            print_red(
                '[Error] Cannot establish communication with device through LAN')
            return

        self.device_conn = SocketConnWrapper(conn)

        conn.send(greeting.encode())

        # confirm device
        self.confirm_device(self.device_conn)

        if self.device:
            callback(self.device)

    def establish_host(self, host_ip):
        socket_host = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_host.settimeout(20)
        try:
            socket_host.bind((host_ip, self.port))
            socket_host.listen(5)
            return socket_host
        except socket.error:
            socket_host = None
            raise
        except socket.timeout as e:
            print(e)
        except Exception as e:
            socket_host = None

        return socket_host

    def open(self):
        '''
        open
        '''

    def close(self):
        '''
        close
        '''
        self._find_client_retries = 0
        if self.sock:
            self.sock.close()
            self.sock = None

    def can_write(self):
        return self.device_conn != None

    def write(self, data, is_flush=False):
        '''
        write
        '''
        try:
            if self.device_conn:
                return self.device_conn.write(data)
        except socket.error:
            print("socket error,do reconnect.")
            raise
        except Exception as e:
            raise

    def read(self, size=100):
        '''
        read
        '''
        try:
            if self.device_conn is None:
                raise Exception('Device is not connected.')
            data = self.device_conn.read(size)

            if not data:
                raise socket.error('Device is connected.')
            else:
                return data
        except socket.error as e:
            print("socket error,do reconnect.")
            raise
        except Exception as e:
            raise
        except:
            raise

    def find_client_by_hostname(self, name, ip_address_list):
        is_find = False
        ip_address = None

        # 1st round, directly find by host name
        try:
            socket.gethostbyname(name)
            is_find = True
        except:
            is_find = False

        if is_find:
            return True, None

        # 2nd round find from netbios
        try:
            nbns = netbios_query(name, ip_address_list)
            ip_address = nbns.query()
            is_find = True
        except Exception as e:
            is_find = False

        return is_find,ip_address

    def reset_buffer(self):
        '''
        reset buffer
        '''
        pass
