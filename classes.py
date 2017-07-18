class SObject(object):
    # object used to store an object and it's related permissions
    def __init__(self, name, allow_read, allow_create, allow_edit, allow_delete, view_all_records, modify_all_records):
        self.name = name
        self.allow_read = allow_read
        self.allow_create = allow_create
        self.allow_edit = allow_edit
        self.allow_delete = allow_delete
        self.view_all_records = view_all_records
        self.modify_all_records = modify_all_records


class Field(object):
    # object used to store a field and it's related attributes
    def __init__(self, name, readable, editable):
        self.name = name
        self.readable = readable
        self.editable = editable
