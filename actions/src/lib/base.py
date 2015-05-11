import abc
import json
import os
import six
import subprocess
import sys

from st2actions.runners.pythonrunner import Action


class OpenStackBaseAction(Action):

    # structure of openstack command.
    os_cli_cmd = 'openstack'

    def __init__(self, config):
        super(OpenStackBaseAction, self).__init__(config=config)
        self.token = self._get_config_section(config, 'token')
        self.password = self._get_config_section(config, 'password')
        self.parser = None

    def run(self, **kwargs):
        self.parser = self._get_parser(kwargs.pop('ep'))
        cmd = [self.os_cli_cmd]
        cmd.extend(self.get_cmd(**kwargs))
        # Copy over curretn environment so that the pythonpath for openstack command is
        # still available.
        env = os.environ.copy()
        env.update(self.token or self.password)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             env=env)
        out, err = p.communicate()
        return self._format_output(out=out, err=err, exit=p.returncode)

    @abc.abstractmethod
    def get_cmd(self, **kwargs):
        pass

    def _get_config_section(self, config, section):
        cfg = config.get(section, {})
        return {k: v for k, v in six.iteritems(cfg) if v}

    def _get_parser(self, ep):
        # EntryPoint is needed only for eval to work. Locaizing the import
        # for readability and to avoid accidental deletion.
        from pkg_resources import EntryPoint
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
