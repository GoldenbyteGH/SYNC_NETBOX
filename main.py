#!/usr/bin/python3


"""

keep Update ip from dhcp leases in my domain

"""
import socket,configparser
from requests import patch
from netbox import NetBox

class Device:
    def __init__(self,name,domain,SM='/24'):
        self.name=name+domain
        self.subnet=SM
        self.domain = domain
        self.IP='0.0.0.0'
        self.VID='0'
    def getIP(self):
        try:
            self.IP = socket.gethostbyname(self.name)  # Resolve DNS
            self.VID = self.IP[7:9]                    # Get VLAN from  3rd octect
        except:
            self.IP=None


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
    ##############################################################################################################################################################
    for item in netbox_device.virtualization.get_virtual_machines():                # sync GATEWAY Status
        if 'Pfsense' in item['name']:

            pfsenseX = Device(item['name'], domain=config['NETBOX_SRV']['domain'])
            pfsenseX.getIP()
            if pfsenseX.IP != None:
                GW_ONLINE = {
                    'status': 'active'
                }
                patch(url=netbox_srv + '/api/virtualization/virtual-machines/' + str(item['id']) + '/',headers=netbox_srv_header,json=GW_ONLINE, verify=False)
            else:
                GW_OFFLINE = {
                    'status': 'offline'
                }
                res=patch(url=netbox_srv + '/api/virtualization/virtual-machines/' + str(item['id']) + '/',headers=netbox_srv_header, json=GW_OFFLINE, verify=False)
    ##############################################################################################################################################################

    for item in netbox_device.ipam.get_ip_addresses():
        if item['assigned_object_id']!= None and item['status']['value'] == 'dhcp' :
            try:
                v_device = Device(item['assigned_object']['virtual_machine']['name'],domain=config['NETBOX_SRV']['domain'])
                v_device.getIP()
                print('virtual',item['address'],v_device.name,'<=====>',v_device.IP)
                if item['address'][:-3] != v_device.IP and v_device.IP != None:
                    if item['address'][7:9] == v_device.VID:                # check VLAN on interface before PATCH IP
                        payload = {
                            'address': v_device.IP+v_device.subnet
                        }
                        patch(url=netbox_srv+'/api/ipam/ip-addresses/'+str(item['id'])+'/',headers=netbox_srv_header,json=payload,verify=False)
            except:
                f_device = Device(item['assigned_object']['device']['name'],domain=config['NETBOX_SRV']['domain'])
                f_device.getIP()
                print('physical',item['address'],f_device.name,'<=====>',f_device.IP)
                if item['address'][:-3] != f_device.IP and f_device.IP != None:
                    if item['address'][7:9] == f_device.VID:             # check VLAN on interface before PATCH IP
                        payload = {
                            'address': f_device.IP+f_device.subnet
                        }
                        patch(url=netbox_srv+'/api/ipam/ip-addresses/'+str(item['id'])+'/',headers=netbox_srv_header,json=payload,verify=False)
