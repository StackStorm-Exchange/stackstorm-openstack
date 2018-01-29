import argparse

from osc_lib.cli import parseractions

DASH_PARAMETERS = [
    "rxtx_factor",
    "container_format",
    "copy_from",
    "disk_format",
    "min_disk",
    "min_ram",
    "page_size",
    "public_key",
    "key_pairs",
    "no_share",
    "or_show",
    "fixed_ips",
    "floating_ips",
    "injected_file_size",
    "public_key",
    "injected_files",
    "min_disk",
    "min_ram",
    "injected_path_size",
    "secgroup_rules",
    "volume_type",
    "all_projects",
    "dst_port",
    "src_group",
    "src_ip",
    "availability_zone",
    "block_device_mapping",
    "config_drive",
    "key_name",
    "security_group",
    "user_data",
    "all_projects",
    "instance_name",
    "reservation_id",
    "block_migration",
    "disk_overcommit",
    "no_disk_overcommit",
    "password_prompt",
    "shared_migration",
    "root_password",
    "address_type",
    "password_prompt",
    "availability_zone",
    "snapshot_id",
    "all_projects",
    "end_marker",
    "protocol_port",
    "lb_algorithm",
    "provider_network_type",
    "provider_physical_network",
    "provider_segmentation_id"
]

NEUTRON_PARAMETER = [
    'net-list',
    'net-external-list',
    'net-show',
    'net-create',
    'net-delete',
    'net-update',
    'subnet-list',
    'subnet-show',
    'subnet-create',
    'subnet-delete',
    'subnet-update',
    'subnetpool-list',
    'subnetpool-show',
    'subnetpool-create',
    'subnetpool-delete',
    'subnetpool-update',
    'port-list',
    'port-show',
    'port-create',
    'port-delete',
    'port-update',
    'purge',
    'quota-list',
    'quota-show',
    'quota-default-show',
    'quota-delete',
    'quota-update',
    'ext-list',
    'ext-show',
    'router-list',
    'router-port-list',
    'router-show',
    'router-create',
    'router-delete',
    'router-update',
    'router-interface-add',
    'router-interface-delete',
    'router-gateway-set',
    'router-gateway-clear',
    'floatingip-list',
    'floatingip-show',
    'floatingip-create',
    'floatingip-delete',
    'floatingip-associate',
    'floatingip-disassociate',
    'security-group-list',
    'security-group-show',
    'security-group-create',
    'security-group-delete',
    'security-group-update',
    'security-group-rule-list',
    'security-group-rule-show',
    'security-group-rule-create',
    'security-group-rule-delete',
    'agent-list',
    'agent-show',
    'agent-delete',
    'agent-update',
    'dhcp-agent-network-add',
    'dhcp-agent-network-remove',
    'net-list-on-dhcp-agent',
    'dhcp-agent-list-hosting-net',
    'l3-agent-router-add',
    'l3-agent-router-remove',
    'router-list-on-l3-agent',
    'l3-agent-list-hosting-router',
    'lb-pool-list-on-agent',
    'lb-agent-hosting-pool',
    'lbaas-loadbalancer-list-on-agent',
    'lbaas-agent-hosting-loadbalancer',
    'service-provider-list',
    'rbac-create',
    'rbac-update',
    'rbac-list',
    'rbac-show',
    'rbac-delete',
    'address-scope-list',
    'address-scope-show',
    'address-scope-create',
    'address-scope-delete',
    'address-scope-update',
    'availability-zone-list',
    'auto-allocated-topology-show',
    'auto-allocated-topology-delete',
    'net-ip-availability-list',
    'net-ip-availability-show',
    'tag-add',
    'tag-replace',
    'tag-remove',
    'qos-policy-list',
    'qos-policy-show',
    'qos-policy-create',
    'qos-policy-update',
    'qos-policy-delete',
    'qos-bandwidth-limit-rule-create',
    'qos-bandwidth-limit-rule-show',
    'qos-bandwidth-limit-rule-list',
    'qos-bandwidth-limit-rule-update',
    'qos-bandwidth-limit-rule-delete',
    'qos-dscp-marking-rule-create',
    'qos-dscp-marking-rule-show',
    'qos-dscp-marking-rule-list',
    'qos-dscp-marking-rule-update',
    'qos-dscp-marking-rule-delete',
    'qos-minimum-bandwidth-rule-create',
    'qos-minimum-bandwidth-rule-show',
    'qos-minimum-bandwidth-rule-list',
    'qos-minimum-bandwidth-rule-update',
    'qos-minimum-bandwidth-rule-delete',
    'qos-available-rule-types',
    'flavor-list',
    'flavor-show',
    'flavor-create',
    'flavor-delete',
    'flavor-update',
    'flavor-associate',
    'flavor-disassociate',
    'flavor-profile-list',
    'flavor-profile-show',
    'flavor-profile-create',
    'flavor-profile-delete',
    'flavor-profile-update',
    'meter-label-create',
    'meter-label-list',
    'meter-label-show',
    'meter-label-delete',
    'meter-label-rule-create',
    'meter-label-rule-list',
    'meter-label-rule-show',
    'meter-label-rule-delete',
    'firewall-rule-list',
    'firewall-rule-show',
    'firewall-rule-create',
    'firewall-rule-update',
    'firewall-rule-delete',
    'firewall-policy-list',
    'firewall-policy-show',
    'firewall-policy-create',
    'firewall-policy-update',
    'firewall-policy-delete',
    'firewall-policy-insert-rule',
    'firewall-policy-remove-rule',
    'firewall-list',
    'firewall-show',
    'firewall-create',
    'firewall-update',
    'firewall-delete',
    'bgp-dragent-speaker-add',
    'bgp-dragent-speaker-remove',
    'bgp-speaker-list-on-dragent',
    'bgp-dragent-list-hosting-speaker',
    'bgp-speaker-list',
    'bgp-speaker-advertiseroute-list',
    'bgp-speaker-show',
    'bgp-speaker-create',
    'bgp-speaker-update',
    'bgp-speaker-delete',
    'bgp-speaker-peer-add',
    'bgp-speaker-peer-remove',
    'bgp-speaker-network-add',
    'bgp-speaker-network-remove',
    'bgp-peer-list',
    'bgp-peer-show',
    'bgp-peer-create',
    'bgp-peer-update',
    'bgp-peer-delete',
    'lbaas-loadbalancer-list',
    'lbaas-loadbalancer-show',
    'lbaas-loadbalancer-create',
    'lbaas-loadbalancer-update',
    'lbaas-loadbalancer-delete',
    'lbaas-loadbalancer-stats',
    'lbaas-loadbalancer-status',
    'lbaas-listener-list',
    'lbaas-listener-show',
    'lbaas-listener-create',
    'lbaas-listener-update',
    'lbaas-listener-delete',
    'lbaas-l7policy-list',
    'lbaas-l7policy-show',
    'lbaas-l7policy-create',
    'lbaas-l7policy-update',
    'lbaas-l7policy-delete',
    'lbaas-l7rule-list',
    'lbaas-l7rule-show',
    'lbaas-l7rule-create',
    'lbaas-l7rule-update',
    'lbaas-l7rule-delete',
    'lbaas-pool-list',
    'lbaas-pool-show',
    'lbaas-pool-create',
    'lbaas-pool-update',
    'lbaas-pool-delete',
    'lbaas-healthmonitor-list',
    'lbaas-healthmonitor-show',
    'lbaas-healthmonitor-create',
    'lbaas-healthmonitor-update',
    'lbaas-healthmonitor-delete',
    'lbaas-member-list',
    'lbaas-member-show',
    'lbaas-member-create',
    'lbaas-member-update',
    'lbaas-member-delete',
    'lb-vip-list',
    'lb-vip-show',
    'lb-vip-create',
    'lb-vip-update',
    'lb-vip-delete',
    'lb-pool-list',
    'lb-pool-show',
    'lb-pool-create',
    'lb-pool-update',
    'lb-pool-delete',
    'lb-pool-stats',
    'lb-member-list',
    'lb-member-show',
    'lb-member-create',
    'lb-member-update',
    'lb-member-delete',
    'lb-healthmonitor-list',
    'lb-healthmonitor-show',
    'lb-healthmonitor-create',
    'lb-healthmonitor-update',
    'lb-healthmonitor-delete',
    'lb-healthmonitor-associate',
    'lb-healthmonitor-disassociate',
    'ipsec-site-connection-list',
    'ipsec-site-connection-show',
    'ipsec-site-connection-create',
    'ipsec-site-connection-update',
    'ipsec-site-connection-delete',
    'vpn-endpoint-group-list',
    'vpn-endpoint-group-show',
    'vpn-endpoint-group-create',
    'vpn-endpoint-group-update',
    'vpn-endpoint-group-delete',
    'vpn-service-list',
    'vpn-service-show',
    'vpn-service-create',
    'vpn-service-update',
    'vpn-service-delete',
    'vpn-ipsecpolicy-list',
    'vpn-ipsecpolicy-show',
    'vpn-ipsecpolicy-create',
    'vpn-ipsecpolicy-update',
    'vpn-ipsecpolicy-delete',
    'vpn-ikepolicy-list',
    'vpn-ikepolicy-show',
    'vpn-ikepolicy-create',
    'vpn-ikepolicy-update',
    'vpn-ikepolicy-delete',
]


def process_kwargs(kwargs):
    for key in DASH_PARAMETERS:
        if key in kwargs:
            if key == 'provider_network_type':
                kwargs['provider:network_type'] = kwargs.pop(key)
            elif key == 'provider_physical_network':
                kwargs['provider:physical_network'] = kwargs.pop(key)
            elif key == 'provider_segmentation_id':
                kwargs['provider:segmentation_id'] = kwargs.pop(key)
            else:
                kwargs[key.replace('_', '-')] = kwargs.pop(key)
    return kwargs


class ArgparseUtils(object):

    TYPE_LOOKUP = {
        int: 'integer',
        float: 'number',
        bool: 'boolean',
        'integer': int,
        'number': float,
        'boolean': bool,
        'array': list,
        'string': str
    }

    @staticmethod
    def is_positional(action):
        # If no option string is specified then is a positional
        return len(action.option_strings) == 0

    @staticmethod
    def get_type(action):
        if action.type in ArgparseUtils.TYPE_LOOKUP:
            return ArgparseUtils.TYPE_LOOKUP[action.type]
        # In all these cases the value that will be stored is known so
        # so we only pick whether to append or not.
        if isinstance(action, argparse._StoreTrueAction) or \
           isinstance(action, argparse._StoreFalseAction) or \
           isinstance(action, argparse._AppendConstAction):
            return 'boolean'
        # _AppendAction and KeyValueAction are treated as array for st2 but
        # are different i.e. specified multiple times
        if isinstance(action, argparse._AppendAction) or \
           isinstance(action, parseractions.KeyValueAction):
            return 'array'
        return 'string'

    @staticmethod
    def is_repeated_action(action):
        '''
        _AppendAction and KeyValueAction are repeated on the CLI
        e.g. --property a=1 --property b=1
        '''
        return isinstance(action, argparse._AppendAction) or \
            isinstance(action, parseractions.KeyValueAction)

    @staticmethod
    def get_default(action, type_=None):
        if type_ is None:
            type_ = ArgparseUtils.get_type(action)
        # special handling for the formatter action. default value of table
        # is no good in this case.
        if action.dest == 'formatter' and 'json' in action.choices:
            return 'json'
        if action.default is not None:
            if isinstance(action, parseractions.RangeAction):
                # assumption is action.default is a tuple - (0, 0)
                return '%s:%s' % action.default
            # Do best to cast to the right type. This way oddly written
            # defaults which mismatch the type of specified property do not
            # lead to inconsistencies in default for st2.
            # e.g. openstackclient.compute.v2.server:CreateServer.config-drive
            if isinstance(type_, str) and type_ in ArgparseUtils.TYPE_LOOKUP:
                return ArgparseUtils.TYPE_LOOKUP[type_](action.default)
            else:
                action.default
        # For _AppendConstAction do not append by default.
        if isinstance(action, argparse._StoreTrueAction) or \
           isinstance(action, argparse._AppendConstAction):
            return False
        if isinstance(action, argparse._StoreFalseAction):
            return True

    @staticmethod
    def get_name(action):
        # param name is from the options string of fully expanded
        usable_options = [x for x in action.option_strings if x.startswith('--')]
        return usable_options[0][len('--'):] if usable_options else action.dest

    @staticmethod
    def is_boolean_included(action, value):
        """
        Looking at whether the action is StoreTrueAction, StoreFalseAction or AppendConstAction
        and at the actual value to decide if the boolean action should be included.
        """
        if isinstance(action, argparse._StoreTrueAction) or \
           isinstance(action, argparse._AppendConstAction):
            return value
        if isinstance(action, argparse._StoreFalseAction):
            return not value
        return value
