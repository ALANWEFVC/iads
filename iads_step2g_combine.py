from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, arp, lldp, icmp, ipv4
from ryu.lib import hub
from ryu.app import simple_switch_13

class IADSApp(simple_switch_13.SimpleSwitch13):
    """步骤G：组合所有变量 + add_flow，但不使用hub功能"""
    
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    
    def __init__(self, *args, **kwargs):
        super(IADSApp, self).__init__(*args, **kwargs)
        
        # 组合所有成功的变量
        self.packet_count = 0
        self.lldp_count = 0
        self.arp_count = 0
        self.icmp_count = 0
        self.is_active = False
        self.main_datapath = None
        
        self.logger.info("IADS Step2G: All variables + add_flow (no hub usage)")
    
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        self.logger.info("IADS: switch_features_handler START")
        
        super(IADSApp, self).switch_features_handler(ev)
        
        datapath = ev.msg.datapath
        self.main_datapath = datapath
        
        self.logger.info("IADS: Switch {} parent handler completed".format(datapath.id))
        
        # 添加LLDP流表项（复制成功的代码）
        try:
            self.logger.info("IADS: Adding LLDP flow")
            
            ofproto = datapath.ofproto
            parser = datapath.ofproto_parser
            
            match = parser.OFPMatch(eth_type=0x88cc)
            actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                              ofproto.OFPCML_NO_BUFFER)]
            self.add_flow(datapath, 100, match, actions)
            
            self.logger.info("IADS: LLDP flow installed successfully")
            
            # 不使用hub.spawn_after，只记录
            self.logger.info("IADS: Ready for monitoring (hub not used)")
            
        except Exception as e:
            self.logger.error("IADS: Error: {}".format(e))
        
        self.logger.info("IADS: switch_features_handler END")
    
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
                
            elif eth.ethertype == 0x0800:  # IPv4
                ip_pkt = pkt.get_protocol(ipv4.ipv4)
                if ip_pkt and ip_pkt.proto == 1:  # ICMP
                    icmp_pkt = pkt.get_protocol(icmp.icmp)
                    if icmp_pkt:
                        self.icmp_count += 1
                        self.logger.info("IADS: ICMP packet detected (total: {})".format(self.icmp_count))
        
        if self.packet_count % 30 == 0:
            self.logger.info("IADS: Stats - Total: {}, ICMP: {}, LLDP: {}".format(
                self.packet_count, self.icmp_count, self.lldp_count))
