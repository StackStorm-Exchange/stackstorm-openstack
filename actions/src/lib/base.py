import abc
import json
import os
import six
import subprocess
import sys

from st2common.runners.base_action import Action
from utils import process_kwargs


class OpenStackBaseAction(Action):

    # structure of openstack command.
    os_cli_cmd = 'openstack'

    def __init__(self, config):
        super(OpenStackBaseAction, self).__init__(config=config)
        self.openstackrc = self._get_config_section(config, 'openstackrc')
        self.token = self._get_config_section(config, 'token')
        self.password = self._get_config_section(config, 'password')
        self.parser = None

    def run(self, **kwargs):
        self.parser = self._get_parser(kwargs.pop('ep'))
        kwargs = process_kwargs(kwargs)
        cmd = [self.os_cli_cmd]
        cmd.extend(self.get_cmd(**kwargs))
        # Copy over current environment so that the pythonpath for openstack command is
        # still available.
        env = os.environ.copy()
        # If "cloud" was specified, use a clouds.yaml file for authentication.
        # Next, check for an openstackrc file specified in the pack configuration.
        # Finally, check for pack configured token or password.
        # The precedence order is cloud > openstackrc > token > password.
        if 'cloud' in kwargs and kwargs['cloud'] is not None:
            cmd.append('--os-cloud %s' % kwargs['cloud'])
        elif self.openstackrc:
            cmd[:0] = ['.', self.openstackrc, '&&']
        else:
            env.update(self.token or self.password)

        # If a project name or id was specified in the action, configure openstackclient
        # to run under that project. This will take precedence over prior authentication
        # settings.
        if 'project_name' in kwargs and kwargs['project_name'] is not None:
            cmd.append('--os-project-name %s' % kwargs['project_name'])
        elif 'project_id' in kwargs and kwargs['project_id'] is not None:
            cmd.append('--os-project-id %s' % kwargs['project_id'])

        cmd_str = ' '.join(cmd)
        self.logger.debug('Generated command "%s"', cmd_str)
        p = subprocess.Popen(cmd_str, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             env=env, shell=True)
        out, err = p.communicate()
        return self._format_output(out=out, err=err, exit=p.returncode)

    @abc.abstractmethod
    def get_cmd(self, **kwargs):
        pass

    def _get_config_section(self, config, section):
        cfg = config.get(section, {})
        if not isinstance(cfg, dict):
            return cfg
        return {k: v for k, v in six.iteritems(cfg) if v}

    def _get_parser(self, ep):
        # EntryPoint is needed only for eval to work. Locaizing the import
        # for readability and to avoid accidental deletion.
        from pkg_resources import EntryPoint  # NOQA
        entry_point = eval(ep)
        command_cls = entry_point.load(require=False)
        command = command_cls(None, None)
        return command.get_parser('autogen')

    def _format_output(self, out, err, exit):
        if exit == 0:
            try:
                return json.loads(out)
            except ValueError:
                return out
        else:
            # put out and err to output streams
            sys.stdout.write(out)
            sys.stderr.write(err)
            sys.exit(exit)
