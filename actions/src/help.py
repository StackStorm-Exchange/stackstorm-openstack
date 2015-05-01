from lib.base import OpenStackBaseAction


class TestAction(OpenStackBaseAction):

    def get_cmd(self, **kwargs):
        return '--help'
