from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, arp, lldp, icmp, ipv4
from ryu.lib import hub
from ryu.app import simple_switch_13

class IADSApp(simple_switch_13.SimpleSwitch13):
    """第2步：添加LLDP流表项和探测功能"""
    
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    
    def __init__(self, *args, **kwargs):
        super(IADSApp, self).__init__(*args, **kwargs)
        
        # IADS监控相关
        self.packet_count = 0
        self.arp_count = 0
        self.icmp_count = 0
        self.lldp_count = 0
        
        # IADS探测相关
        self.is_active = False
        self.datapath = None
        
        self.logger.info("IADS Step2: LLDP and Probing initialized")
    
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        super(IADSApp, self).switch_features_handler(ev)
        
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        self.datapath = datapath  # 保存datapath用于探测
        
        self.logger.info("IADS: Switch {} basic flows installed".format(datapath.id))
        
        # 添加LLDP流表项（高优先级）
        try:
            match = parser.OFPMatch(eth_type=0x88cc)
            actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                              ofproto.OFPCML_NO_BUFFER)]
            self.add_flow(datapath, 100, match, actions)
            
            self.logger.info("IADS: LLDP flow installed for switch {}".format(datapath.id))
            
            # 启动探测线程
            hub.spawn_after(5, self._start_probing)
            
        except Exception as e:
            self.logger.error("IADS: Error installing LLDP flow: {}".format(e))
    
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
            if eth.ethertype == 0x88cc:  # LLDP
                self.lldp_count += 1
                lldp_pkt = pkt.get_protocol(lldp.lldp)
                if lldp_pkt:
                    self.logger.info("IADS: LLDP packet received (total: {})".format(self.lldp_count))
                    
            elif eth.ethertype == 0x0806:  # ARP
                self.arp_count += 1
                if self.arp_count % 5 == 0:
                    self.logger.info("IADS: ARP count: {}".format(self.arp_count))
                    
            elif eth.ethertype == 0x0800:  # IPv4
                ip_pkt = pkt.get_protocol(ipv4.ipv4)
                if ip_pkt and ip_pkt.proto == 1:  # ICMP
                    icmp_pkt = pkt.get_protocol(icmp.icmp)
                    if icmp_pkt:
                        self.icmp_count += 1
                        self.logger.info("IADS: ICMP packet detected (total: {})".format(self.icmp_count))
        
        # 每50个包记录一次统计
        if self.packet_count % 50 == 0:
            self.logger.info("IADS: Stats - Total: {}, ARP: {}, ICMP: {}, LLDP: {}".format(
                self.packet_count, self.arp_count, self.icmp_count, self.lldp_count))
    
    def _start_probing(self):
        """启动IADS探测"""
        self.logger.info("IADS: Starting probing thread")
        self.is_active = True
        hub.spawn(self._probe_loop)
    
    def _probe_loop(self):
        """IADS探测循环"""
        while self.is_active:
            try:
                self.logger.info("IADS: Probe round - monitoring network state")
                
                # 简单的探测逻辑
                if self.datapath:
                    # 这里可以发送LLDP包或其他探测包
                    self.logger.debug("IADS: Active probing on datapath {}".format(self.datapath.id))
                
                # 等待10秒
                hub.sleep(10)
                
            except Exception as e:
                self.logger.error("IADS: Error in probe loop: {}".format(e))
                hub.sleep(10)
    
    def stop(self):
        """停止IADS"""
        self.logger.info("IADS: Stopping application")
        self.is_active = False
