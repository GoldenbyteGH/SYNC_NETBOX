
import socket
from netbox import NetBox


class Device:
    def __init__(self,name,domain='.goldenbyte.it',SM='/24'):
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

    netbox_device = NetBox(host='netbox.goldenbyte.it', use_ssl=False, auth_token='2987124c7bfb33f28ddc7872599acddf13bf3d6c')
    name_fdevices = netbox_device.dcim.get_devices()
    name_vdevices = netbox_device.virtualization.get_virtual_machines()

    for item in netbox_device.ipam.get_ip_addresses():
        if item['assigned_object_id']!= None and item['status']['value'] == 'dhcp' :
            try:
                v_device = Device(item['assigned_object']['virtual_machine']['name'])
                print('virtual',item['address'],v_device.name,'<=====>',v_device.getIP())
                if item['address'][:-3] != v_device.getIP():
                    print(v_device.getIP()+v_device.getSM())
                    exit()
                    netbox_device.ipam.update_ip(item['address'],{'address':v_device.getIP()+v_device.getSM()})
            except:
                f_device = Device(item['assigned_object']['device']['name'])
                print('physical',item['address'],f_device.name,'<=====>',f_device.getIP())
                if item['address'][:-3] != f_device.getIP():
                    netbox_device.ipam.update_ip(item['address'],{'address':f_device.getIP()+f_device.getSM()})


