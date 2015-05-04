import six

from lib.base import OpenStackBaseAction

SKIP = ['id', 'name']


class WrapperAction(OpenStackBaseAction):

    def get_cmd(self, positional, **kwargs):
        _args = [positional]
        _args.extend(['--%s %s' % (k, v) for k,v in six.iteritems(kwargs) if k not in SKIP])
        return ' '.join(map(str, _args))
