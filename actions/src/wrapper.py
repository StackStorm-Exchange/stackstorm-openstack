import six

from lib.base import OpenStackBaseAction


class WrapperAction(OpenStackBaseAction):

    def get_cmd(self, base, verb, **kwargs):
        _args = [base, verb]
        _args.extend(['--%s %s' % (k, v) for k,v in six.iteritems(kwargs)])
        return ' '.join(map(str, _args))
