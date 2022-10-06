
import socket,configparser
from requests import patch
from netbox import NetBox

class Device:
    def __init__(self,name,domain,SM='/24'):
        self.name=name+domain
        self.IP='0.0.0.0'
        self.subnet=SM
        self.type=None
        self.domain = domain
    def getIP(self):
        try:
            return socket.gethostbyname(self.name)          #Resolve DNS
        except:
            return None
    def getSM(self):
        return self.subnet


if __name__ == '__main__':
    ####################################################
    # config Netbox AuthInfo
    ####################################################
    config = configparser.ConfigParser()
    config.read('config.ini')
    netbox_srv=config['NETBOX_SRV']['url']
    netbox_srv_header={
        'Accept':'application/json',
        'Authorization':config['NETBOX_SRV']['token'],
    }
    ##################################################

    netbox_device = NetBox(host=netbox_srv[8:], use_ssl=False, auth_token=netbox_srv_header['Authorization'][6:])
    name_fdevices = netbox_device.dcim.get_devices()
    name_vdevices = netbox_device.virtualization.get_virtual_machines()

    for item in netbox_device.ipam.get_ip_addresses():
        if item['assigned_object_id']!= None and item['status']['value'] == 'dhcp' :
            try:
                v_device = Device(item['assigned_object']['virtual_machine']['name'],domain=config['NETBOX_SRV']['domain'])
                print('virtual',item['address'],v_device.name,'<=====>',v_device.getIP())
                if item['address'][:-3] != v_device.getIP() and v_device.getIP() != None:
                    payload = {
                        'address': v_device.getIP()+v_device.getSM()
                    }
                    patch(url=netbox_srv+'/api/ipam/ip-addresses/'+str(item['id'])+'/',headers=netbox_srv_header,json=payload,verify=False)
            except:
                f_device = Device(item['assigned_object']['device']['name'])
                print('physical',item['address'],f_device.name,'<=====>',f_device.getIP())
                if item['address'][:-3] != f_device.getIP() and f_device.getIP() != None:
                    payload = {
                        'address': f_device.getIP()+f_device.getSM()
                    }
                    patch(url=netbox_srv+'/api/ipam/ip-addresses/'+str(item['id'])+'/',headers=netbox_srv_header,json=payload,verify=False)



