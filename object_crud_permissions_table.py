import xml.etree.ElementTree as et
from beautifultable import BeautifulTable
import os
import classes
import util_functions as uf


# get list of permission set files that need to be digested and create dictionaries with numbers for user input
files = []
files_dict = {}  # used in detail mode as perm shorthand (name to number)
files_num_dict = {}  # used in detail mode for reverse dict (number to name)
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

# get list of objects that exist and build a list of SObjects to store perm rollup
object_list = uf.create_object_list()
final_perm_list = {}
for o in object_list:
    new_object = classes.SObject(o, [], [], [], [], [], [])
    final_perm_list[new_object.name] = new_object

print('\nObject Level Permissions Table for:\n')
print selected_profile + ' - ' + 'P'

# calculate profile permissions
final_perm_list = uf.calculate_profile_permissions(final_perm_list, selected_profile)

# digest permission set files and roll up perms into the final_perm_list
for perm_file in files:
    if files_dict[perm_file] in user_input_set:
        print perm_file + ' - ' + str(files_dict[perm_file])
        tree = et.parse('permissionsets/' + perm_file)
        root = tree.getroot()

        for child in root:
            if child.tag == "{http://soap.sforce.com/2006/04/metadata}objectPermissions":
                # temp variables to store grandchild text
                temp_name = ''
                temp_allow_read = ''
                temp_allow_create = ''
                temp_allow_edit = ''
                temp_allow_delete = ''
                temp_view_all_records = ''
                temp_modify_all_records = ''

                # assign temp variables based on the grand child tag
                for grand_child in child:
                    if "object" in grand_child.tag:
                        temp_name = grand_child.text
                    elif "allowRead" in grand_child.tag:
                        temp_allow_read = grand_child.text
                    elif "allowCreate" in grand_child.tag:
                        temp_allow_create = grand_child.text
                    elif "allowEdit" in grand_child.tag:
                        temp_allow_edit = grand_child.text
                    elif "allowDelete" in grand_child.tag:
                        temp_allow_delete = grand_child.text
                    elif "viewAllRecords" in grand_child.tag:
                        temp_view_all_records = grand_child.text
                    elif "modifyAllRecords" in grand_child.tag:
                        temp_modify_all_records = grand_child.text

                # add current perm set value to final perm list if true
                if temp_allow_read == 'true':
                    final_perm_list[temp_name].allow_read.append(files_dict[perm_file])
                if temp_allow_create == 'true':
                    final_perm_list[temp_name].allow_create.append(files_dict[perm_file])
                if temp_allow_edit == 'true':
                    final_perm_list[temp_name].allow_edit.append(files_dict[perm_file])
                if temp_allow_delete == 'true':
                    final_perm_list[temp_name].allow_delete.append(files_dict[perm_file])
                if temp_view_all_records == 'true':
                    final_perm_list[temp_name].view_all_records.append(files_dict[perm_file])
                if temp_modify_all_records == 'true':
                    final_perm_list[temp_name].modify_all_records.append(files_dict[perm_file])

# print final table
table = BeautifulTable()
table._max_table_width = 150
table.auto_calculate_width()
table.column_headers = ["Name", "allowRead", "allowCreate", "allowEdit", "allowDelete", "viewAllRecords",
                        "modifyAllRecords"]
for o in object_list:
    table.append_row([final_perm_list[o].name, final_perm_list[o].allow_read, final_perm_list[o].allow_create,
                      final_perm_list[o].allow_edit, final_perm_list[o].allow_delete,
                      final_perm_list[o].view_all_records, final_perm_list[o].modify_all_records])
print table

# mode = raw_input("Enter 1 for cumulative mode, 2 for detail mode: ")
# if mode == '1':
#     # digest files and roll up perms into the final_perm_list
#     for perm_file in files:
#         if perm_file == 'Modify_All_Data.permissionset':
#             break
#         tree = et.parse('permissionsets/' + perm_file)
#         root = tree.getroot()
#
#         for child in root:
#             if child.tag == "{http://soap.sforce.com/2006/04/metadata}objectPermissions":
#                 # temp variables to store grandchild text
#                 temp_name = ''
#                 temp_allow_read = ''
#                 temp_allow_create = ''
#                 temp_allow_edit = ''
#                 temp_allow_delete = ''
#                 temp_view_all_records = ''
#                 temp_modify_all_records = ''
#
#                 # assign temp variables based on the grand child tag
#                 for grand_child in child:
#                     if "object" in grand_child.tag:
#                         temp_name = grand_child.text
#                     elif "allowRead" in grand_child.tag:
#                         temp_allow_read = grand_child.text
#                     elif "allowCreate" in grand_child.tag:
#                         temp_allow_create = grand_child.text
#                     elif "allowEdit" in grand_child.tag:
#                         temp_allow_edit = grand_child.text
#                     elif "allowDelete" in grand_child.tag:
#                         temp_allow_delete = grand_child.text
#                     elif "viewAllRecords" in grand_child.tag:
#                         temp_view_all_records = grand_child.text
#                     elif "modifyAllRecords" in grand_child.tag:
#                         temp_modify_all_records = grand_child.text
#
#                 # if the final perm list object for each respective variable is false, set it to what is currently
#                 # being read
#                 if temp_allow_read == 'true':
#                     final_perm_list[temp_name].allow_read = 'true'
#                 if temp_allow_create == 'true':
#                     final_perm_list[temp_name].allow_create = 'true'
#                 if temp_allow_edit == 'true':
#                     final_perm_list[temp_name].allow_edit = 'true'
#                 if temp_allow_delete == 'true':
#                     final_perm_list[temp_name].allow_delete = 'true'
#                 if temp_view_all_records == 'true':
#                     final_perm_list[temp_name].view_all_records = 'true'
#                 if temp_modify_all_records == 'true':
#                     final_perm_list[temp_name].modify_all_records = 'true'

