#!/usr/bin/env python3

import hvac
import json
import argparse
import sys
import os

class VaultInventory(object):

    vault_addr = os.environ['VAULT_ADDR']
    vault_token = os.environ['VAULT_TOKEN']
    secret_infra_mount_point = 'secret'
    secret_infra_path = 'infra/vbox'
    inventory_list_all = {}
    hostvars_dist = {}
    hostgroups = {}

    def __init__(self):
        self.hvacclient = hvac.Client(
            url=self.vault_addr, token=self.vault_token)

    def build_inventory_object(self):
        inv_meta_object = {'hostvars': self.hostvars_dist}
        self.inventory_list_all = {'_meta': inv_meta_object}
        self.inventory_list_all['all'] = {'children': ['ungrouped']}
        self.inventory_list_all['ungrouped'] = {'hosts': self.list_hosts}
        return self.inventory_list_all

    def build_hostvars_set(self):
        for host in self.list_hosts:
            self.hostvars_dist[host] = self.retrieve_hostvars(host)

    def retrieve_hostvars(self, host):
        try:
            hostsecrets = self.hvacclient.secrets.kv.v2.read_secret_version(
                mount_point=self.secret_infra_mount_point,
                path=self.secret_infra_path+'/'+host)['data']['data']
            return hostsecrets
        except:
            return {}

    def retrieve_host_list(self):
        self.list_hosts = self.hvacclient.secrets.kv.v2.list_secrets(
            mount_point=self.secret_infra_mount_point,
            path=self.secret_infra_path)['data']['keys']

    @staticmethod
    def args_parse():
        parser = argparse.ArgumentParser()
        # parser.add_mutually_exclusive_group(required=True)
        parser.add_argument('--list', action='store_true')
        parser.add_argument('--host', action='store')
        return parser.parse_args()


def main():
    inv = VaultInventory()
    userargs = VaultInventory.args_parse()
    if userargs.list:
        inv.retrieve_host_list()
        inv.build_hostvars_set()
        finalobject = inv.build_inventory_object()
        json.dump(finalobject, sys.stdout)
    else:
        singlehost = inv.retrieve_hostvars(userargs.host)
        json.dump(singlehost, sys.stdout)


if __name__ == '__main__':
    main()
