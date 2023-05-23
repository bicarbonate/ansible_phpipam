#!/usr/bin/python
# -*- coding: utf-8 -*-
#

import os
import sys
import argparse
import json
import pymysql as mdb

IPAM_DBHOST = os.getenv('IPAM_DBHOST')
IPAM_DBPASS = os.getenv('IPAM_DBPASS')
IPAM_DBUSER = os.getenv('IPAM_DBUSER')
inventory = {}
queries = ["SELECT INET_NTOA(ip_addr) AS ip_address, hostname, custom_role  FROM ipaddresses WHERE custom_managed='Yes' AND subnetId IN (SELECT id FROM subnets WHERE custom_Ownership LIKE 'IT Department');",           ]

def getdbdata(query):
    con = None
    mylist = []
    if DEBUG:
        print(query)

    try:
        con = mdb.connect(user=IPAM_DBUSER, passwd=IPAM_DBPASS, host=IPAM_DBHOST, port=3306, database='phpipam')
        cursor = con.cursor()
        cursor.execute(query)
        desc = cursor.description

        column_names = [col[0] for col in desc]

        rows = cursor.fetchall()
        for row in rows:
            mylist.append(dict(zip(column_names, row)))

    except Exception as ex:
        print(ex)
        print("Check db communication.")

    finally:
        if con:
            con.close()

    return mylist


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action='store_true', default=False, help="show debug output")
    parser.add_argument('--list', action='store_true', help="used by ansible")
    parser.add_argument('--groups', action='store_true', help="list groupnames this script generates")
    parser.add_argument('--host', action='store', help="unused")
    myargs = parser.parse_args()

    global DEBUG
    DEBUG = myargs.debug

    # Create the groups dict which we will populate
    inventory = {}
    inventory['_meta'] = {}
    inventory['_meta']['hostvars'] = {}
    # loop through the queries and populate the groups dict with data found
    for query in queries:
        result = getdbdata(query.format(** vars(myargs)))
        for item in result:
            if DEBUG:
                if 'custom_role' not in item:
                    continue
            if not inventory.get(item['custom_role']):
                inventory[item['custom_role']] = {}
                inventory[item['custom_role']]['hosts'] = []
                if 'vars' in inventory[item['custom_role']]:
                    del inventory[item['custom_role']]['vars']

            if item['hostname'] is None:
                item['hostname'] = item['ip_address']

            inventory[item['custom_role']]['hosts'].append(item['hostname'])
            inventory['_meta']['hostvars'][item['hostname']] = {"ansible_host": item['ip_address']}

            if 'all' not in inventory:
                inventory['all'] = {}
                inventory['all']['children'] = []

            inventory['all']['children'].append(item['custom_role'])

    if myargs.list:
        #output_file = '/tmp/inventory.json'
        #with open(output_file, 'w') as outfile:
        #            json.dump(inventory, outfile, indent=4)
        print(json.dumps(inventory, indent=4))

    # We return '_meta', skipped implementing --host option.

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
