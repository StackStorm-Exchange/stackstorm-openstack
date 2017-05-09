from keystoneclient.v3 import client as keystone
from zaqarclient.queues.v1 import client as zaqar

from st2reactor.sensor.base import PollingSensor


class MessageQueueSensor(PollingSensor):
    """
    * self.sensor_service
        - provides utilities like
            - get_logger() - returns logger instance specific to this sensor.
            - dispatch() for dispatching triggers into the system.
    * self._config
        - contains parsed configuration that was specified as
          config.yaml in the pack.
    """

    def setup(self):
        super(MessageQueueSensor, self).setup()
        self.logger = self.sensor_service.get_logger(name=self.__class__.__name__)

    def _get_keystone_auth_cred(self):
        return {
            'username': self._config['password']['OS_USERNAME'],
            'password': self._config['password']['OS_PASSWORD'],
            'auth_url': self._config['password']['OS_AUTH_URL'],
            'project_id': self._config['password']['OS_TENANT_ID']
        }

    def _get_zaqar_auth_config(self, auth_token):
        return {
            'auth_opts': {
                'options': {
                    'os_auth_token': auth_token,
                    'os_project_id': self._config['password']['OS_TENANT_ID'],
                    'os_auth_url': self._config['password']['OS_AUTH_URL']
                }
            }
        }

    def _get_claim_options(self):
        return {
            'ttl': self._config['messaging']['claim_ttl'],
            'grace': self._config['messaging']['claim_grace']
        }

    def _dispatch_message(self, queue_name, message):
        payload = {'queue': queue_name, 'message': message}
        self.sensor_service.dispatch(trigger='openstack.messaging', payload=payload)

    def poll(self):
        keystone_cred = self._get_keystone_auth_cred()
        keystone_cli = keystone.Client(**keystone_cred)

        messaging_endpoint = keystone_cli.service_catalog.url_for(
            service_type=self._config['messaging']['service_type'],
            endpoint_type='publicURL'
        )

        messaging_cli = zaqar.Client(
            messaging_endpoint,
            conf=self._get_zaqar_auth_config(keystone_cli.auth_token),
            version=2
        )

        claim_options = self._get_claim_options()
        claim_ttl = claim_options['ttl']
        claim_grace = claim_options['grace']

        for queue_name in self._config['messaging']['queues']:
            self.logger.debug('Claiming from queue "%s"...' % queue_name)
            queue = messaging_cli.queue(queue_name)
            for message in queue.claim(ttl=claim_ttl, grace=claim_grace):
                self._dispatch_message(queue_name, message.body)
                message.delete()

    def cleanup(self):
        # This is called when the st2 system goes down. You can perform cleanup operations like
        # closing the connections to external system here.
        pass

    def add_trigger(self, trigger):
        # This method is called when trigger is created
        pass

    def update_trigger(self, trigger):
        # This method is called when trigger is updated
        pass

    def remove_trigger(self, trigger):
        # This method is called when trigger is deleted
        pass
