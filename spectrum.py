#!/usr/bin/env python

import json

raw = open('test.json', 'r')
raw = json.load(raw)
raw = raw['ns1.model-response-list']['ns1.model-responses']['ns1.model']
# print(type(raw))

filterList = [
    ('0x12c04', 'model'),
    ('0x12d83', 'secureDomainName'),
    ('0x12d7f', 'ipAddress'),
    ('0x12y6q', 'osVersion')
]
spectrumlist = []
def createData():
    for model in raw:
        spectrumvars = {}
        for attributes, varlist in model.items():
            if isinstance(varlist, list):
                # print(varlist)
                # [{'$': 'ciscorouter', '@id': '0x12c04'}, {'$': 'nykserver01', '@id': '0x12d83'},{'@error': 'NoSuchAttribute', '@id': '0x12d7f'}]
                # [{'@error': 'NoSuchAttribute', '@id': '0x12c04'}, {'$': 'sgdserver01', '@id': '0x12d83'},{'$': '10.2.2.2', '@id': '0x12d7f'}]
                # [{'$': 'f5networks', '@id': '0x12c04'}, {'$': 'ldnserver01', '@id': '0x12d83'},{'$': '10.3.3.3', '@id': '0x12d7f'}]
                # [{'$': 'netscreen', '@id': '0x12c04'}, {'$': '', '@id': '0x12d83'}, {'$': '10.4.4.4', '@id': '0x12d7f'}]
                # [{'@error': 'NoSuchAttribute', '@id': '0x12c04'}, {'$': 'nykserver01', '@id': '0x12d83'},{'$': '10.5.5.5', '@id': '0x12d7f'}]
                for vars in varlist:
                    for filterTuple in filterList:
                        id, colName = filterTuple
                        if vars['@id'] == id:
                            if '@error' in vars.keys():
                                spectrumvars.update({colName: vars['@error']})
                            else:
                                spectrumvars.update({colName: vars['$']})
                spectrumlist.append(spectrumvars)
    return spectrumlist

curateddata = createData()

# print(createData())


# spectrumlist = []
# for model in raw:
#     spectrumvars = {}
#     for attributes, varlist in model.items():
#         if isinstance(varlist, list):
#             # print(value)
#             for vars in varlist:
#                 if vars['@id'] == '0x12c04':
#                     if '@error' in vars.keys():
#                         spectrumvars.update({'model': vars['@error']})
#                     else:
#                         spectrumvars.update({'model': vars['$']})
#                 elif vars['@id'] == '0x12d83':
#                     if '@error' in vars.keys():
#                         spectrumvars.update({'secureDomainName': vars['@error']})
#                     else:
#                         spectrumvars.update({'secureDomainName': vars['$']})
#                 elif vars['@id'] == '0x12d7f':
#                     if '@error' in row.keys():
#                         spectrumvars.update({'ipAddress': vars['@error']})
#                     else:
#                         spectrumvars.update({'ipAddress': vars['$']})
#                 else:
#                     print('Problem encountered in row : ' + vars)
#             spectrumlist.append(spectrumvars)
# for item in spectrumlist:
#     print(item.values())
#
import psycopg2
from psycopg2.extras import execute_values
#
# # INSERT INTO spdw (ipaddress, hostname, operational_state)
# # VALUES ('10.1.1.1', 'host01', 'operational');
# # ('20.1.1.1', 'host02', 'ceased'),
# # ('30.1.1.1', 'host03', 'maintenance'),
# # ('40.1.1.1', 'host04', 'operational');
#
columns = curateddata[0].keys()
# print(','.join(columns))
# query = "INSERT INTO public.spectrum ({}) VALUES %s".format(','.join(columns))
# query = "INSERT INTO public.spectrum ({}) VALUES %s ON CONFLICT (ipaddress) DO NOTHING".format(','.join(columns))
query = "INSERT INTO public.spectrum ({}) VALUES %s ON CONFLICT (ipaddress) DO NOTHING".format(','.join(columns))
# print(spectrumlist.values())
values = [[value for value in item.values()] for item in curateddata]
print(values)

conn = psycopg2.connect(
                host = '192.168.0.91',
                database = 'spectrum',
                user = 'postgres',
                password = 'Labrat@123'
)
cursor = conn.cursor()
delete = [{'query': 'TRUNCATE public.spectrum;'},
          {'query': 'DELETE FROM public.spectrum;'}
          ]

for item in delete:
    cursor.execute(item['query'])
execute_values(cursor, query, values)
conn.commit()
conn.close()
#
#
