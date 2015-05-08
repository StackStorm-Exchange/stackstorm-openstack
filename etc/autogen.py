#! /usr/bin/env python2.7

import argparse
import openstackclient.shell as shell
import os
import six
import sys
import traceback
import yaml


DEBUG = False
# CHANGEME
BASE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'test')

SCRIPT_RELATIVE_PATH = 'src/wrapper.py'

ALL = '*'


class CommandProcessor(object):

    TYPE_LOOKUP = {
        int: 'integer',
        float: 'number',
        bool: 'boolean'
    }

    def __init__(self, command, entry_point):
        self._command_text = command
        self._command_name = command.replace(' ', '.')
        self._entry_point = entry_point
        self._command_cls = entry_point.load()

    def _get_parameter(self, default=None, description=None, type_='string', required=False,
                       immutable=False):
        return {
            'default': default,
            'description': description,
            'type': type_,
            'required': required,
            'immutable': immutable
        } if default is not None else {
            'description': description,
            'type': type_,
            'required': required,
            'immutable': immutable
        }

    def _is_required(self, action, parser):
        if type(action.required) is bool:
            return action.required
        # if is optional then is not required
        if action.option_strings:
            return False
        # positional actions in mutually_exclusive_groups cannot be required.
        for mex_group in parser._mutually_exclusive_groups:
            if action in mex_group._group_actions:
                return False
        return True

    def _get_type(self, action):
        if action.type in self.TYPE_LOOKUP:
            return self.TYPE_LOOKUP[action.type]
        # In all these cases the value that will be stored is know so
        # so we only pick where to append or not.
        if isinstance(action, argparse._StoreTrueAction) or \
           isinstance(action, argparse._StoreFalseAction) or \
           isinstance(action, argparse._AppendConstAction):
            return 'boolean'
        if isinstance(action, argparse._AppendAction):
            return 'array'
        return 'string'

    def _get_default(self, action):
        if action.default is not None:
            return action.default
        if isinstance(action, argparse._StoreTrueAction):
            return False
        # For _AppendConstAction so not append by default.
        if isinstance(action, argparse._StoreFalseAction) or \
           isinstance(action, argparse._AppendConstAction):
            return True

    def _parse_parameter(self, action, parser):
        # param name is from the options string of fully expanded
        usable_options = [x for x in action.option_strings if x.startswith('--')]
        name = usable_options[0][len('--'):] if usable_options else action.dest

        # All positionals outside of a mutually exclusive group are required.
        required = self._is_required(action, parser)

        # type is string if not specified otherwise
        type_ = self._get_type(action)

        # for a few actions default is defined by type(action)
        default = self._get_default(action)

        return name, self._get_parameter(default=default, description=action.help,
                                         type_=type_, required=required)

    def _parse_parameters(self, parser):
        parameters = {}

        for action in parser._actions:
            # value implies that argparse will ignore.
            if action.dest is argparse.SUPPRESS or action.default is argparse.SUPPRESS:
                continue
            name, meta = self._parse_parameter(action, parser)
            # include soe extra debug info. Useful if with a single action.
            if DEBUG:
                print '\033[92m\033[4m\033[1m%s\033[0m' % name
                print action, '\n', meta, '\n'
            parameters[name] = meta

        parameters['ep'] = self._get_parameter(default=repr(self._entry_point), immutable=True)
        parameters['base'] = self._get_parameter(default=self._command_text, immutable=True)
        return parameters

    def __call__(self):
        command = self._command_cls(None, None)
        parser = command.get_parser('autogen')
        parameters = self._parse_parameters(parser)
        return {
            'name': self._command_name,
            'runner_type': 'run-python',
            'entry_point': SCRIPT_RELATIVE_PATH,
            'enabled': True,
            'description': self._command_cls.__doc__,
            'parameters': parameters
        }


class MetaDataWriter(object):

    def __init__(self, base_path=BASE_PATH, script_relative_path=SCRIPT_RELATIVE_PATH):
        self._base_path = base_path
        self._script_relative_path = script_relative_path

    def write(self, command):
        metadata_file_path = os.path.join(self._base_path, '%s.%s' % (command['name'], 'yaml'))
        with open(metadata_file_path, 'w') as out:
            out.write(yaml.dump(command, explicit_start=True, default_flow_style=False, indent=4))
        return metadata_file_path


def _setup_shell_app():
    # create app and run help command. This bootstrap the application.
    app = shell.OpenStackShell()
    try:
        # reduce noise - 1
        org_print_message = argparse.ArgumentParser._print_message

        def devnull(obj, message, file):
            pass

        argparse.ArgumentParser._print_message = devnull

        # reduce noise - 2
        stdout = sys.stdout
        stderr = sys.stderr
        app_stdout = app.stdout
        app_stderr = app.stderr

        dev_null = open(os.devnull, 'w')
        sys.stdout = dev_null
        sys.stderr = dev_null
        app.stdout = dev_null
        app.stderr = dev_null

        app.run(['--help'])
    except SystemExit:
        pass
    finally:
        # reassign original stdout and stderr
        sys.stdout = stdout
        sys.stderr = stderr
        app.stdout = app_stdout
        app.stderr = app_stderr
        argparse.ArgumentParser._print_message = org_print_message
    return app


def _get_commands(app):
    return app.command_manager.commands


def _is_command_in_namespace(command, namespace):
    if namespace == ALL:
        return True
    return command.startswith(namespace)


def _process_commands(commands, namespace=ALL, base_write_path=BASE_PATH):
    writer = MetaDataWriter(base_path=base_write_path)
    for command, ep in six.iteritems(commands):
        if not _is_command_in_namespace(command, namespace):
            continue
        writeable_command = CommandProcessor(command, ep)()
        path = writer.write(writeable_command)
        print('%s : %s ' % (writeable_command['name'], path))


def _get_parsed_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ns', '-n', dest='namespace', default=ALL)
    parser.add_argument('--path', '-p', dest='base_path', default=BASE_PATH)
    parser.add_argument('--debug', '-d', dest='debug', action='store_true')
    return parser.parse_args()


def main():
    args = _get_parsed_args()
    # Well evil but whatever.
    global DEBUG
    DEBUG = args.debug
    app = _setup_shell_app()
    commands = _get_commands(app)
    _process_commands(commands, namespace=args.namespace, base_write_path=args.base_path)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        pass
    except:
        print('autogen stalled.')
        traceback.print_exc()
