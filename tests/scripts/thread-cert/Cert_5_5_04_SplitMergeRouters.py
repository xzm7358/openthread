#!/usr/bin/env python
#
#  Copyright (c) 2016, The OpenThread Authors.
#  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are met:
#  1. Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#  2. Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#  3. Neither the name of the copyright holder nor the
#     names of its contributors may be used to endorse or promote products
#     derived from this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#  ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
#  LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#  CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
#  SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
#  INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
#  CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
#  ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
#  POSSIBILITY OF SUCH DAMAGE.
#

import time
import unittest

import config
import node

LEADER = 1
ROUTER1 = 2
ROUTER2 = 3
ROUTER3 = 4
ROUTER4 = 5

class Cert_5_5_4_SplitMergeRouters(unittest.TestCase):
    def setUp(self):
        self.simulator = config.create_default_simulator()

        self.nodes = {}
        for i in range(1,6):
            self.nodes[i] = node.Node(i, simulator=self.simulator)

        self.nodes[LEADER].set_panid(0xface)
        self.nodes[LEADER].set_mode('rsdn')
        self._setUpLeader()

        self.nodes[ROUTER1].set_panid(0xface)
        self.nodes[ROUTER1].set_mode('rsdn')
        self.nodes[ROUTER1].add_whitelist(self.nodes[LEADER].get_addr64())
        self.nodes[ROUTER1].add_whitelist(self.nodes[ROUTER3].get_addr64())
        self.nodes[ROUTER1].enable_whitelist()
        self.nodes[ROUTER1].set_router_selection_jitter(1)

        self.nodes[ROUTER2].set_panid(0xface)
        self.nodes[ROUTER2].set_mode('rsdn')
        self.nodes[ROUTER2].add_whitelist(self.nodes[LEADER].get_addr64())
        self.nodes[ROUTER2].add_whitelist(self.nodes[ROUTER4].get_addr64())
        self.nodes[ROUTER2].enable_whitelist()
        self.nodes[ROUTER2].set_router_selection_jitter(1)

        self.nodes[ROUTER3].set_panid(0xface)
        self.nodes[ROUTER3].set_mode('rsdn')
        self.nodes[ROUTER3].add_whitelist(self.nodes[ROUTER1].get_addr64())
        self.nodes[ROUTER3].enable_whitelist()
        self.nodes[ROUTER3].set_router_selection_jitter(1)

        self.nodes[ROUTER4].set_panid(0xface)
        self.nodes[ROUTER4].set_mode('rsdn')
        self.nodes[ROUTER4].add_whitelist(self.nodes[ROUTER2].get_addr64())
        self.nodes[ROUTER4].enable_whitelist()
        self.nodes[ROUTER4].set_router_selection_jitter(1)

    def _setUpLeader(self):
        self.nodes[LEADER].add_whitelist(self.nodes[ROUTER1].get_addr64())
        self.nodes[LEADER].add_whitelist(self.nodes[ROUTER2].get_addr64())
        self.nodes[LEADER].enable_whitelist()
        self.nodes[LEADER].set_router_selection_jitter(1)        

    def tearDown(self):
        for node in list(self.nodes.values()):
            node.stop()
        del self.nodes
        del self.simulator

    def test(self):
        self.nodes[LEADER].start()
        self.simulator.go(5)
        self.assertEqual(self.nodes[LEADER].get_state(), 'leader')

        self.nodes[ROUTER1].start()
        self.simulator.go(5)
        self.assertEqual(self.nodes[ROUTER1].get_state(), 'router')

        self.nodes[ROUTER2].start()
        self.simulator.go(5)
        self.assertEqual(self.nodes[ROUTER2].get_state(), 'router')

        self.nodes[ROUTER3].start()
        self.simulator.go(5)
        self.assertEqual(self.nodes[ROUTER3].get_state(), 'router')

        self.nodes[ROUTER4].start()
        self.simulator.go(5)
        self.assertEqual(self.nodes[ROUTER4].get_state(), 'router')

        self.nodes[LEADER].reset()
        self._setUpLeader()
        self.simulator.go(150)

        self.nodes[LEADER].start()
        self.simulator.go(50)

        self.assertEqual(self.nodes[LEADER].get_state(), 'router')

        addrs = self.nodes[ROUTER4].get_addrs()
        for addr in addrs:
            if addr[0:4] != 'fe80':
                self.assertTrue(self.nodes[ROUTER3].ping(addr))

if __name__ == '__main__':
    unittest.main()
