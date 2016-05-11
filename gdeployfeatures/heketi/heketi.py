#!/usr/bin/python
"""
Add functions corresponding to each of the actions in the json file.
The function should be named as follows <feature name>_<action_name>
"""
from gdeploylib import defaults, Global, Helpers
import re

helpers = Helpers()

def heketi_heketi_init(section_dict):
    yamls = []
    get_server_name(section_dict)
    section_dict['port'] = Global.port
    section_dict['server'] = Global.server
    yamls.append(defaults.HKT_CONFIG_COPY)
    section_dict['service'] = 'heketi'
    section_dict['state'] = 'started'
    section_dict['enabled'] = 'yes'
    yamls.append(defaults.CHKCONFIG)
    yamls.append(defaults.SERVICE_MGMT)

    section_dict, ymls = heketi_load_topology(section_dict)
    if ymls:
        yamls.append(ymls)
    return section_dict, yamls


def heketi_load_topology(section_dict):
    if not Global.server or Global.port:
        section_dict = get_server_name(section_dict)
    if Global.server and Global.port:
        section_dict["servername"] = "http://{0}:{1}".format(Global.server,
                Global.port)

    filename = section_dict.get('topologyfile')
    if filename:
        section_dict['filename'] = filename
    else:
        hostnames = helpers.get_section_dict(section_dict, "hostnames")
        zone = helpers.listify(section_dict.get("zone"))
        devices = helpers.listify(section_dict.get("devices"))
        if not (hostnames or zone or devices):
            return section_dict, None
        section_dict = get_hostnames(section_dict, hostnames,
                devices)

    if not section_dict.get("topologyfile"):
        section_dict["topologyfile"] = ''
    return section_dict, defaults.HKT_LOAD_TOPO

def get_devices(devs):
    devnames = devs.split(';')
    if devs and devnames:
        return helpers.correct_brick_format(devnames)
    else:
        return ''

def get_hostnames(section_dict, hostnames, devices):
    global helpers
    if hostnames and not devices:
        devices = [''] * len(hostnames)
    if not hostnames and devices:
        hostnames = [''] * len(devices)
    if len(hostnames) != len(devices):
        print "Error: Entity number mismatch"
        helpers.cleanup_and_quit()
    data = []
    for hosts, devs in zip(hostnames, devices):
        hdict = {}
        h = helpers.listify(hosts)
        manage = ''
        storage = ''
        for each in h:
            mgroup = re.match('manage=(.*)', each)
            if mgroup:
                manage = mgroup.group(1)
            sgroup = re.match('storage=(.*)', each)
            if sgroup:
                storage = sgroup.group(1)
            zgroup = re.match('zone=(.*)', each)
            if zgroup:
                zone = zgroup.group(1)
            else:
                zone = 1
        hdict["manage"] = h[0] if not manage else manage
        hdict["storage"] = h[-1] if not storage else storage
        hdict["devices"] = get_devices(devs)
        hdict["zone"] = zone
        data.append(hdict)
    section_dict['hdict'] = data
    return section_dict


def get_server_name(section_dict):
    global helpers
    server = section_dict.get('server')
    if not server:
        section_dict['servername'] = ''
    else:
        server_group = re.match('(.*):(.*)', server)
        if not server_group:
            port = section_dict.get('port')
        else:
            server = server_group.group(1)
            port = server_group.group(2)
        Global.server = server
        Global.port = port
    return section_dict

def heketi_add_node(section_dict):
    section_dict, yml = heketi_load_topology(section_dict)
    return section_dict, defaults.HKT_ADD_NODE

def heketi_add_device(section_dict):
    section_dict, yml = heketi_load_topology(section_dict)
    return section_dict, defaults.HKT_ADD_DEVICE

def heketi_create_volume(section_dict):
    section_dict, yml = heketi_load_topology(section_dict)
    return section_dict, defaults.HKT_CREATE_VOLUME
