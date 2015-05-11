import argparse

from openstackclient.common import parseractions


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
        # In all these cases the value that will be stored is know so
        # so we only pick where to append or not.
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
        if isinstance(action, argparse._StoreTrueAction):
            return False
        # For _AppendConstAction so not append by default.
        if isinstance(action, argparse._StoreFalseAction) or \
           isinstance(action, argparse._AppendConstAction):
            return True

    @staticmethod
    def get_name(action):
        # param name is from the options string of fully expanded
        usable_options = [x for x in action.option_strings if x.startswith('--')]
        return usable_options[0][len('--'):] if usable_options else action.dest
