import abc
import os
import shlex
import six
import subprocess

from st2actions.runners.pythonrunner import Action


class OpenStackBaseAction(Action):

    # structure of openstack command. Always ask for data as json for upstream consumption.
    base = 'openstack %s -f json'

    def __init__(self, config):
        super(OpenStackBaseAction, self).__init__(config=config)
        self.token = self._get_config_section(config, 'token')
        self.password = self._get_config_section(config, 'password')

    def run(self, **kwargs):
        cmd = self.base % self.get_cmd(**kwargs)
        self.logger.debug('Running cmd %s', cmd)
        # Copy over curretn environment so that the pythonpath for openstack command is
        # still available.
        env = os.environ.copy()
        env.update(self.token or self.password)
        p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             env=env)
        out, err = p.communicate()
        return {'out': out,
                'err': err,
                'exit': p.returncode}

    @abc.abstractmethod
    def get_cmd(self, **kwargs):
        pass

    def _get_config_section(self, config, section):
        cfg = config.get(section, {})
        return {k: v for k, v in six.iteritems(cfg) if v}
