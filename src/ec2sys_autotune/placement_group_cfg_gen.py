'''

EC2 placement groups allow instances to interact with low network latency.
Care should be taken to not use this configuration on WAN to avoid
bloating buffer on the internet. There is more memory buffer for each
socket now to achieve maximum network bandwidth on LAN.
'''

import os
import sys
from syslog import syslog
from ec2sys_autotune.ec2_instance_cfg_gen import Ec2InstanceCfgGen
from ec2_instance_high_networking_performance import *

# Exception
from ec2sys_autotune.ec2_instance_exception import Ec2AutotuneError


class PlacementGroupCfgGen(Ec2InstanceCfgGen):
    def tune(self):
        # Call super class as well to inherit base class network settings
        super(PlacementGroupCfgGen, self).start_cfg_logging()
        super(PlacementGroupCfgGen, self)._tune()
        try:
            networking_performance = self.get_instance_data(
                                         "Networking Performance")

            if (networking_performance in HIGH_NETWORK_PERFORMANCE):
                __min = 4
                if (networking_performance == "100 Gigabit"):
                    __def = 149
                    __max = 1196
                    __budget = 400
                elif (networking_performance == "50 Gigabit"):
                    __def = 149
                    __max = 598
                    __budget = 400
                elif (networking_performance == "25 Gigabit"):
                    __def = 149
                    __max = 299
                    __budget = 400
                elif (networking_performance == "20 Gigabit"):
                    __def = 60
                    __max = 240
                    __budget = 450
                else:
                    # networking_performance == "10 Gigabit"
                    __def = 60
                    __max = 120
                    __budget = 450

                '''
                netdev_budget
                Maximum number of packets taken from all interfaces in
                one polling cycle (NAPI poll).
                '''
                self.set_sysctl_config("net.core.netdev_budget", __budget)

                self.set_sysctl_config("net.core.rmem_max",
                                       1024 * 1024 * __max)
                self.set_sysctl_config("net.core.wmem_max",
                                       1024 * 1024 * __max)
                self.set_sysctl_config("net.ipv4.tcp_rmem",
                                       [1024 * __min,
                                        1024 * 1024 * __def,
                                        1024 * 1024 * __max])
                self.set_sysctl_config("net.ipv4.tcp_wmem",
                                       [1024 * __min,
                                        1024 * 1024 * __def,
                                        1024 * 1024 * __max])
        except Ec2AutotuneError, e:
            syslog(e.msg)
            syslog("Failed to generate configuration specific to " +
                   "EC2 placement gorup")
        super(PlacementGroupCfgGen, self).stop_cfg_logging()
        return
