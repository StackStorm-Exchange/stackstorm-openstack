import six

from lib.base import OpenStackBaseAction
from lib.utils import ArgparseUtils


class WrapperAction(OpenStackBaseAction):

    def get_cmd(self, **kwargs):
        # base is a required property.
        cmd = kwargs['base'].split()
        # Iterate over _actions to preserve original order
        for action in self.parser._actions:
            name = ArgparseUtils.get_name(action)
            if name in kwargs:
                action_cli_text = self.get_action_cli_text(action, name, kwargs[name])
                if action_cli_text:
                    cmd.extend(action_cli_text)
        return cmd

    def get_action_cli_text(self, action, name, value):
        # positional args are always required and only expect value.
        if ArgparseUtils.is_positional(action):
            return [value]
        default = ArgparseUtils.get_default(action)
        # for format since it is doubly hacked we keep making exceptions.
        if name != 'format' and str(default) == str(value):
            return []
        # expand the array into a repetition.
        if ArgparseUtils.is_repeated_action(action):
            cli_text = []
            for v in value:
                cli_text.append(action.option_strings[0])
                cli_text.append(v)
            return cli_text
        # Special handling for boolean
        if ArgparseUtils.get_type(action) == 'boolean':
            include_action = ArgparseUtils.is_boolean_included(action, value)
            # For booleans we only include the option_string.
            # e.g. --wait instead of --wait=True.
            return [action.option_strings[0]] if include_action else None
        # will end up being of the form "option_string value"
        return [
            action.option_strings[0],
            six.moves.shlex_quote(
                str(value)
            )
        ]
