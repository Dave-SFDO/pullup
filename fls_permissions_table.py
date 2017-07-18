import xml.etree.ElementTree as ET
from beautifultable import BeautifulTable
import os
import util_functions as uf
import classes


files = []
files_dict = {}  # used in detail mode as perm shorthand
files_num_dict = {}  # used for reverse dict (number to name)
count = 1
for filename in os.listdir('permissionsets'):
    if filename.endswith('.permissionset'):
        files.append(filename)
        files_dict[filename] = count
        files_num_dict[count] = filename
        count += 1

# Print all profiles for user selection
profiles = uf.create_profile_list()
print('\n\nAvailable profiles:')
for profile in profiles:
    print profile
selected_profile = raw_input('Enter the profile name to calculate permissions for: ')

# Print all permission sets for user selection
perm_table = BeautifulTable()
perm_table.auto_calculate_width()
perm_table.column_headers = ['Name', 'Number']
for filename in files:
    perm_table.append_row([files_num_dict[files_dict[filename]], files_dict[filename]])
print('\nAvailable Permission Sets')
print perm_table

user_input_set = set()
user_input = ''
while user_input != 'x':
    user_input = raw_input('Add permission set number (x to stop): ')
    if user_input != 'x':
        # needs to check entry for valid int
        user_input_set.add(int(user_input))

object_to_get = raw_input('Enter object name: ')

tree = ET.parse('objects/' + object_to_get + '.object')
root = tree.getroot()

fields = []
# get fields from object xml
for child in root:
    if child.tag == '{http://soap.sforce.com/2006/04/metadata}fields':
        # assign temp variables based on the grand child tag
        for grand_child in child:
            if grand_child.tag == '{http://soap.sforce.com/2006/04/metadata}fullName':
                fields.append(grand_child.text)

final_fls_list = {}
for f in fields:
    new_field = Field(f, [], [])
    final_fls_list[new_field.name] = new_field

# digest files and roll up perms into the final_perm_list
print('\n')
print('FLS Table for:')
print('\n')
for perm_file in files:
    if files_dict[perm_file] in user_input_set:
        print perm_file + ' - ' + str(files_dict[perm_file])
        tree = ET.parse('permissionsets/' + perm_file)
        root = tree.getroot()

        for child in root:
            if child.tag == "{http://soap.sforce.com/2006/04/metadata}fieldPermissions":
                # temp variables to store grandchild text
                temp_name = ''
                temp_readable = ''
                temp_editable = ''

                # assign temp variables based on the grand child tag
                for grand_child in child:
                    if "field" in grand_child.tag:
                        temp_name = grand_child.text
                    elif "allowRead" in grand_child.tag:
                        temp_allow_read = grand_child.text
                    elif "allowCreate" in grand_child.tag:
                        temp_allow_create = grand_child.text

                # add current perm set value to final perm list if true
                if temp_name.startswith(object_to_get, 0, len(object_to_get) + 1):
                    if temp_readable == 'true':
                        final_fls_list[temp_name[0:len(object_to_get)]].readable.append(files_dict[perm_file])
                    if temp_editable == 'true':
                        final_fls_list[temp_name[0:len(object_to_get)]].editable.append(files_dict[perm_file])

# print final table
table = BeautifulTable()
table._max_table_width = 100
table.auto_calculate_width()
table.column_headers = ['Name', 'readable', 'editable']
for fls in final_fls_list:
    table.append_row([fls.name, fls.readable, fls.editable])
print table
