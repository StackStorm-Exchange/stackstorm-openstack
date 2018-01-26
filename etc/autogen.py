#! /usr/bin/env python2.7

import argparse
import logging
import os
import sys

from openstackclient import shell
import six
import yaml

# HACK until setup.py is worked out to add actions/src to PYTHONPATH
sys.path.append(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '../actions/src'))

from lib.utils import ArgparseUtils


LOG = logging.getLogger(__name__)

# CHANGEME
BASE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'test')

SCRIPT_RELATIVE_PATH = 'src/wrapper.py'

ALL = '*'


class CommandProcessor(object):

    SKIP_GROUP_NAMES = [
        'output formatters',
        # https://github.com/openstack/cliff/blob/master/cliff/display.py#L53

        'table formatter',
        # https://github.com/openstack/cliff/blob/master/cliff/formatters/table.py#L22

        'shell formatter',
        # https://github.com/openstack/cliff/blob/master/cliff/formatters/shell.py#L14

        'CSV Formatter'
        # https://github.com/openstack/cliff/blob/master/cliff/formatters/commaseparated.py#L20
    ]

    def __init__(self, command, entry_point):
        self._command_text = command
        self._command_name = command.replace(' ', '.')
        self._entry_point = entry_point
        self._command_cls = entry_point.load()
        self._skip_groups = []

    def _get_parameter(self, default=None, description='', type_='string', required=False,
                       immutable=False):
        parameter = {
            'type': type_
        }
        # include properties only if they have meaningful values.
        if required:
            parameter['required'] = required
        if immutable:
            parameter['immutable'] = immutable
        if description:
            parameter['description'] = description
        if default is not None:
            parameter['default'] = default
        return parameter

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

    def _setup_skip_groups(self, parser):
        # Add groups to skip group.
        self._skip_groups.extend(
            [g for g in parser._action_groups if g.title in self.SKIP_GROUP_NAMES])
        self._skip_groups.extend(
            [g for g in parser._mutually_exclusive_groups if g.title in self.SKIP_GROUP_NAMES])

    def _test_skip_action(self, action, parser):
        # hack for formatter
        if action.dest == 'formatter' and 'json' in action.choices:
            return False
        # This check is leading to some really mruky issues. Lots of formatting
        # options which might be usef are lost for example. For now helps with
        # simplicity of creating a usable pack.
        for skip_group in self._skip_groups:
            # It is important to use _group_actions to limit to action within a group.
            if action in skip_group._group_actions:
                LOG.debug('\n%s in %s', action, skip_group.title)
                return True
        return False

    def _parse_parameter(self, action, parser):
        if self._test_skip_action(action, parser):
            return None, None

        name = ArgparseUtils.get_name(action)

        # All positionals outside of a mutually exclusive group are required.
        required = self._is_required(action, parser)

        # type is string if not specified otherwise
        type_ = ArgparseUtils.get_type(action)

        # for a few actions default is defined by type(action)
        default = ArgparseUtils.get_default(action, type_=type_)

        # Make sure choices are included in the description. Often action.help
        # may not list choices. It is perhaps better if this type were an enum?
        description = str(action.help) if not action.choices else \
            '%s (choices: %s)' % (action.help, ', '.join(map(str, action.choices)))

        return name, self._get_parameter(default=default, description=description,
                                         type_=type_, required=required)

    def _parse_parameters(self, parser):
        parameters = {}

        # skip groups should be put in place before
        self._setup_skip_groups(parser)

        for action in parser._actions:
            # value implies that argparse will ignore.
            if action.dest is argparse.SUPPRESS or action.default is argparse.SUPPRESS:
                continue
            name, meta = self._parse_parameter(action, parser)
            if not name and not meta:
                LOG.debug('\033[91mskipping:\033[0m %s', action)
                continue

            # include some extra debug info. Useful if with a single action.
            LOG.debug('\033[92m\033[4m\033[1m%s\033[0m', name)
            LOG.debug('%s\n%s', action, meta)

            name = name.replace("-", "_")
            parameters[name] = meta

        parameters['ep'] = self._get_parameter(default=repr(self._entry_point), immutable=True)
        parameters['base'] = self._get_parameter(default=self._command_text, immutable=True)

        # Add a cloud parameter to the action
        cloud_param = {
            'type': 'string',
            'description': 'A specific cloud to query'
        }
        parameters['cloud'] = cloud_param

        # Add project parameters to the action
        project_name_param = {
            'type': 'string',
            'description': 'Run the action under a different project, identified by name'
        }
        parameters['project_name'] = project_name_param

        project_id_param = {
            'type': 'string',
            'description': 'Run the action under a different project, identified by id'
        }
        parameters['project_id'] = project_id_param

        return parameters

    def __call__(self):
        try:
            command = self._command_cls(None, None)
            parser = command.get_parser('autogen')
            parameters = self._parse_parameters(parser)
            LOG.debug('No of parameters %s', len(parameters))
            return {
                'name': self._command_name,
                'runner_type': 'python-script',
                'entry_point': SCRIPT_RELATIVE_PATH,
                'enabled': True,
                'description': self._command_cls.__doc__,
                'parameters': parameters
            }
        except Exception as err:
            print("Unable to generate %s: %s") % (self._command_name, err)
            pass


class MetaDataWriter(object):

    def __init__(self, base_path=BASE_PATH, script_relative_path=SCRIPT_RELATIVE_PATH):
        self._base_path = base_path
        self._script_relative_path = script_relative_path

    def write(self, command):
        metadata_file_path = os.path.join(self._base_path, '%s.%s' % (command['name'], 'yaml'))
        with open(metadata_file_path, 'w') as out:
            out.write(yaml.safe_dump(command, explicit_start=True,
                                     default_flow_style=False, indent=4))
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
        if writeable_command is not None:
            path = writer.write(writeable_command)
            LOG.info('%s : %s ', writeable_command['name'], path)


def _setup_logging(debug=False):
    level = logging.DEBUG if debug else logging.INFO
    LOG.setLevel(level)

    # log to console
    ch = logging.StreamHandler()
    ch.setLevel(level)

    formatter = logging.Formatter('%(message)s')
    ch.setFormatter(formatter)

    LOG.addHandler(ch)


def _get_parsed_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ns', '-n', dest='namespace', default=ALL)
    parser.add_argument('--path', '-p', dest='base_path', default=BASE_PATH)
    parser.add_argument('--debug', '-d', dest='debug', action='store_true')
    return parser.parse_args()


def main():
    args = _get_parsed_args()
    _setup_logging(args.debug)
    app = _setup_shell_app()
    commands = _get_commands(app)
    _process_commands(commands, namespace=args.namespace, base_write_path=args.base_path)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        pass
    except:
        LOG.exception('autogen stalled.')
