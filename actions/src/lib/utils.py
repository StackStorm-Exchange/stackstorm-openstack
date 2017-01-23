import argparse

from osc_lib.cli import parseractions

DASH_PARAMETERS = [
    "rxtx_factor",
    "container_format",
    "copy_from",
    "disk_format",
    "min_disk",
    "min_ram",
    "page_size",
    "public_key",
    "key_pairs",
    "no_share",
    "or_show",
    "fixed_ips",
    "floating_ips",
    "injected_file_size",
    "public_key",
    "injected_files",
    "min_disk",
    "min_ram",
    "injected_path_size",
    "secgroup_rules",
    "volume_type",
    "all_projects",
    "dst_port",
    "src_group",
    "src_ip",
    "availability_zone",
    "block_device_mapping",
    "config_drive",
    "key_name",
    "security_group",
    "user_data",
    "all_projects",
    "instance_name",
    "reservation_id",
    "block_migration",
    "disk_overcommit",
    "no_disk_overcommit",
    "password_prompt",
    "shared_migration",
    "root_password",
    "address_type",
    "password_prompt",
    "availability_zone",
    "snapshot_id",
    "all_projects",
    "end_marker",
]


def process_kwargs(kwargs):
    for key in DASH_PARAMETERS:
        if key in kwargs:
            kwargs[key.replace('_', '-')] = kwargs.pop(key)
    return kwargs


class ArgparseUtils(object):

    TYPE_LOOKUP = {
        int: 'integer',
        float: 'number',
        bool: 'boolean',
        'integer': int,
        'number': float,
        'boolean': bool,
        'array': list,
        'string': str
    }

    @staticmethod
    def is_positional(action):
        # If no option string is specified then is a positional
        return len(action.option_strings) == 0

    @staticmethod
    def get_type(action):
        if action.type in ArgparseUtils.TYPE_LOOKUP:
            return ArgparseUtils.TYPE_LOOKUP[action.type]
        # In all these cases the value that will be stored is known so
        # so we only pick whether to append or not.
        if isinstance(action, argparse._StoreTrueAction) or \
           isinstance(action, argparse._StoreFalseAction) or \
           isinstance(action, argparse._AppendConstAction):
            return 'boolean'
        # _AppendAction and KeyValueAction are treated as array for st2 but
        # are different i.e. specified multiple times
        if isinstance(action, argparse._AppendAction) or \
           isinstance(action, parseractions.KeyValueAction):
            return 'array'
        return 'string'

    @staticmethod
    def is_repeated_action(action):
        '''
        _AppendAction and KeyValueAction are repeated on the CLI
        e.g. --property a=1 --property b=1
        '''
        return isinstance(action, argparse._AppendAction) or \
            isinstance(action, parseractions.KeyValueAction)

    @staticmethod
    def get_default(action, type_=None):
        if type_ is None:
            type_ = ArgparseUtils.get_type(action)
        # special handling for the formatter action. default value of table
        # is no good in this case.
        if action.dest == 'formatter' and 'json' in action.choices:
            return 'json'
        if action.default is not None:
            if isinstance(action, parseractions.RangeAction):
                # assumption is action.default is a tuple - (0, 0)
                return '%s:%s' % action.default
            # Do best to cast to the right type. This way oddly written
            # defaults which mismatch the type of specified property do not
            # lead to inconsistencies in default for st2.
            # e.g. openstackclient.compute.v2.server:CreateServer.config-drive
            if isinstance(type_, str) and type_ in ArgparseUtils.TYPE_LOOKUP:
                return ArgparseUtils.TYPE_LOOKUP[type_](action.default)
            else:
                action.default
        # For _AppendConstAction do not append by default.
        if isinstance(action, argparse._StoreTrueAction) or \
           isinstance(action, argparse._AppendConstAction):
            return False
        if isinstance(action, argparse._StoreFalseAction):
            return True

    @staticmethod
    def get_name(action):
        # param name is from the options string of fully expanded
        usable_options = [x for x in action.option_strings if x.startswith('--')]
        return usable_options[0][len('--'):] if usable_options else action.dest

    @staticmethod
    def is_boolean_included(action, value):
        """
        Looking at whether the action is StoreTrueAction, StoreFalseAction or AppendConstAction
        and at the actual value to decide if the boolean action should be included.
        """
        if isinstance(action, argparse._StoreTrueAction) or \
           isinstance(action, argparse._AppendConstAction):
            return value
        if isinstance(action, argparse._StoreFalseAction):
            return not value
        return value
