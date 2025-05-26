from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, arp, lldp, icmp, ipv4
from ryu.lib import hub
from ryu.app import simple_switch_13

class IADSApp(simple_switch_13.SimpleSwitch13):
    """步骤P：修复is_active冲突"""
    
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    
    def __init__(self, *args, **kwargs):
        super(IADSApp, self).__init__(*args, **kwargs)
        
        # 所有成功的变量
        self.packet_count = 0
        self.lldp_count = 0
        self.arp_count = 0
        self.icmp_count = 0
        self.main_datapath = None
        
        # 修复冲突的变量名
        self.iads_monitoring_active = False  # 改名避免冲突
        
        self.logger.info("IADS Step2P: Fixed variable name conflict")
    
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        super(IADSApp, self).switch_features_handler(ev)
        
        datapath = ev.msg.datapath
        self.main_datapath = datapath
        self.iads_monitoring_active = True  # 使用新的变量名
        
        self.logger.info("IADS: Switch {} connected, monitoring_active={}".format(
            datapath.id, self.iads_monitoring_active))
        
        # 现在尝试添加LLDP流表项
        try:
            ofproto = datapath.ofproto
            parser = datapath.ofproto_parser
            
            match = parser.OFPMatch(eth_type=0x88cc)
            actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                              ofproto.OFPCML_NO_BUFFER)]
            self.add_flow(datapath, 100, match, actions)
            
            self.logger.info("IADS: LLDP flow installed successfully")
            
            # 启动监控
            hub.spawn_after(3, self._start_iads_monitoring)
            
        except Exception as e:
            self.logger.error("IADS: Error: {}".format(e))
    
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        super(IADSApp, self)._packet_in_handler(ev)
        
        self.packet_count += 1
        
        msg = ev.msg
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        
        if eth:
            if eth.ethertype == 0x88cc:  # LLDP
                self.lldp_count += 1
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
        
        if self.packet_count % 30 == 0:
            self.logger.info("IADS: Stats - Total: {}, ARP: {}, ICMP: {}, LLDP: {}".format(
                self.packet_count, self.arp_count, self.icmp_count, self.lldp_count))
    
    def _start_iads_monitoring(self):
        """启动IADS监控"""
        self.logger.info("IADS: Starting monitoring system")
        hub.spawn(self._iads_monitoring_loop)
    
    def _iads_monitoring_loop(self):
        """IADS监控循环"""
        while self.iads_monitoring_active:
            try:
                self.logger.info("IADS: Monitoring round - network analysis")
                
                if self.main_datapath:
                    self.logger.debug("IADS: Active monitoring on datapath {}".format(
                        self.main_datapath.id))
                
                hub.sleep(10)
                
            except Exception as e:
                self.logger.error("IADS: Error in monitoring loop: {}".format(e))
                hub.sleep(10)
