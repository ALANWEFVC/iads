from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, arp, lldp, icmp, ipv4
from ryu.app import simple_switch_13

class IADSApp(simple_switch_13.SimpleSwitch13):
    """第1步：添加IADS监控结构（修复版）"""
    
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    
    def __init__(self, *args, **kwargs):
        super(IADSApp, self).__init__(*args, **kwargs)
        
        # IADS监控相关
        self.packet_count = 0
        self.arp_count = 0
        self.icmp_count = 0
        
        self.logger.info("IADS Step1: Monitoring structure initialized (fixed)")
    
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        super(IADSApp, self).switch_features_handler(ev)
        datapath = ev.msg.datapath
        self.logger.info("IADS: Switch {} connected - monitoring enabled".format(datapath.id))
    
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        # 1. 先调用父类处理器（确保转发正常）
        super(IADSApp, self)._packet_in_handler(ev)
        
        # 2. 添加IADS监控
        self.packet_count += 1
        
        msg = ev.msg
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        
        if eth:
            if eth.ethertype == 0x0806:  # ARP
                self.arp_count += 1
                if self.arp_count % 5 == 0:  # 每5个ARP包记录一次
                    self.logger.info("IADS: ARP count: {}".format(self.arp_count))
                    
            elif eth.ethertype == 0x0800:  # IPv4
                ip_pkt = pkt.get_protocol(ipv4.ipv4)  # 修复了导入问题
                if ip_pkt and ip_pkt.proto == 1:  # ICMP
                    icmp_pkt = pkt.get_protocol(icmp.icmp)
                    if icmp_pkt:
                        self.icmp_count += 1
                        self.logger.info("IADS: ICMP packet detected (total: {})".format(self.icmp_count))
        
        # 每100个包记录一次统计
        if self.packet_count % 100 == 0:
            self.logger.info("IADS: Packet stats - Total: {}, ARP: {}, ICMP: {}".format(
                self.packet_count, self.arp_count, self.icmp_count))
