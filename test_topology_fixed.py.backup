#!/usr/bin/env python3
# test_topology.py - Mininet测试拓扑

"""
创建一个用于测试IADS框架的Mininet拓扑
拓扑结构：
    h1 --- s1 --- s2 --- h2
            |      |
            +--s3--+
               |
               h3
"""

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink
import time
import random
import threading


class IADSTestTopology:
    """IADS测试拓扑"""

    def __init__(self):
        self.net = None
        self.hosts = []
        self.switches = []
        self.links = []

    def create_topology(self):
        """创建测试拓扑"""
        info('*** Creating network\n')

        # 创建网络，使用RemoteController连接到Ryu
        self.net = Mininet(
            controller=RemoteController,
            switch=OVSSwitch,
            link=TCLink,  # 使用TCLink以支持带宽、延迟等参数
            autoSetMacs=True
        )

        info('*** Adding controller\n')
        c0 = self.net.addController(
            'c0',
            controller=RemoteController,
            ip='127.0.0.1',
            port=6633
        )

        info('*** Adding switches\n')
        # 添加交换机
        s1 = self.net.addSwitch('s1', dpid='0000000000000001')
        s2 = self.net.addSwitch('s2', dpid='0000000000000002')
        s3 = self.net.addSwitch('s3', dpid='0000000000000003')
        self.switches = [s1, s2, s3]

        info('*** Adding hosts\n')
        # 添加主机
        h1 = self.net.addHost('h1', ip='10.0.0.1/24')
        h2 = self.net.addHost('h2', ip='10.0.0.2/24')
        h3 = self.net.addHost('h3', ip='10.0.0.3/24')
        self.hosts = [h1, h2, h3]

        info('*** Creating links\n')
        # 创建链路，设置不同的参数以测试IADS
        # h1-s1: 正常链路
        self.net.addLink(h1, s1, bw=100, delay='1ms', loss=0)

        # s1-s2: 核心链路，带宽较高
        self.net.addLink(s1, s2, bw=1000, delay='2ms', loss=0)

        # s2-h2: 正常链路
        self.net.addLink(s2, h2, bw=100, delay='1ms', loss=0)

        # s1-s3: 不稳定链路，较高延迟和丢包
        self.net.addLink(s1, s3, bw=100, delay='5ms', loss=1)

        # s3-s2: 备份链路
        self.net.addLink(s3, s2, bw=500, delay='3ms', loss=0)

        # s3-h3: 较差的链路
        self.net.addLink(s3, h3, bw=50, delay='10ms', loss=2)

    def start(self):
        """启动网络"""
        info('*** Starting network\n')
        self.net.start()

        # 等待交换机连接到控制器
        info('*** Waiting for switches to connect\n')
        time.sleep(5)

        info('*** Testing connectivity\n')
        # 先执行pingAll确保基本连通性
        self.net.pingAll()

    def run_dynamic_scenarios(self):
        """运行动态场景以测试IADS的自适应能力"""
        info('\n*** Starting dynamic test scenarios\n')

        def scenario_thread():
            scenarios = [
                self._scenario_link_flapping,
                self._scenario_congestion,
                self._scenario_host_failure,
                self._scenario_varying_traffic
            ]

            for scenario in scenarios:
                time.sleep(30)  # 每30秒运行一个场景
                scenario()

        # 在后台线程运行场景
        t = threading.Thread(target=scenario_thread)
        t.daemon = True
        t.start()

    def _scenario_link_flapping(self):
        """场景1：链路抖动"""
        info('\n*** Scenario 1: Link flapping\n')
        s1, s3 = self.switches[0], self.switches[2]

        for i in range(5):
            # 断开链路
            info('  - Bringing down link s1-s3 (iteration {})\n'.format(i + 1))
            self.net.configLinkStatus(s1, s3, 'down')
            time.sleep(3)

            # 恢复链路
            info('  - Bringing up link s1-s3 (iteration {})\n'.format(i + 1))
            self.net.configLinkStatus(s1, s3, 'up')
            time.sleep(3)

    def _scenario_congestion(self):
        """场景2：网络拥塞"""
        info('\n*** Scenario 2: Network congestion\n')
        h1, h2 = self.hosts[0], self.hosts[1]

        # 使用iperf产生大流量
        info('  - Starting high bandwidth flow from h1 to h2\n')
        h2.cmd('iperf -s &')
        h1.cmd('iperf -c 10.0.0.2 -t 20 -b 900M &')

        time.sleep(20)
        # 清理
        h1.cmd('killall -9 iperf')
        h2.cmd('killall -9 iperf')

    def _scenario_host_failure(self):
        """场景3：主机故障"""
        info('\n*** Scenario 3: Host failure simulation\n')
        h3 = self.hosts[2]

        # 模拟主机故障（禁用网络接口）
        info('  - Simulating h3 failure\n')
        h3.cmd('ifconfig h3-eth0 down')
        time.sleep(10)

        # 恢复主机
        info('  - Recovering h3\n')
        h3.cmd('ifconfig h3-eth0 up')
        h3.cmd('ifconfig h3-eth0 10.0.0.3 netmask 255.255.255.0')

    def _scenario_varying_traffic(self):
        """场景4：变化的流量模式"""
        info('\n*** Scenario 4: Varying traffic patterns\n')

        # 产生不同类型的流量
        patterns = [
            ('h1', 'h2', '10M', '5'),  # 低带宽
            ('h2', 'h3', '50M', '5'),  # 中等带宽
            ('h1', 'h3', '80M', '5'),  # 高带宽
        ]

        for src_name, dst_name, bw, duration in patterns:
            src = self.net.get(src_name)
            dst = self.net.get(dst_name)
            dst_ip = dst.IP()

            info('  - Traffic from {} to {} at {}\n'.format(src_name, dst_name, bw))
            dst.cmd(f'iperf -s -p 5001 &')
            src.cmd(f'iperf -c {dst_ip} -p 5001 -t {duration} -b {bw} &')
            time.sleep(int(duration) + 2)

            # 清理
            src.cmd('killall -9 iperf 2>/dev/null')
            dst.cmd('killall -9 iperf 2>/dev/null')

    def cli(self):
        """启动CLI"""
        info('*** Running CLI\n')
        CLI(self.net)

    def stop(self):
        """停止网络"""
        info('*** Stopping network\n')
        self.net.stop()


def main():
    """主函数"""
    setLogLevel('info')

    # 创建测试拓扑
    topo = IADSTestTopology()

    try:
        # 创建和启动拓扑
        topo.create_topology()
        topo.start()

        # 运行动态场景
        topo.run_dynamic_scenarios()

        # 进入CLI
        topo.cli()

    finally:
        # 清理
        topo.stop()


if __name__ == '__main__':
    main()