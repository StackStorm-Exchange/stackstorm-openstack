import abc
import subprocess
import shlex


class OpenStackBaseAction(object):

    base = 'openstack %s'

    def __init__(self, config):
        super(OpenStackBaseAction. self).__init__(config=config)

    def run(self, **kwargs):
        cmd = self.base % self.get_cmd(**kwargs)
        p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        return {'out': out,
                'err': err,
                'exit': p.returncode}

    @abc.abstractmethod
    def get_cmd(self, **kwargs):
        pass
