from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, arp, lldp, icmp, ipv4
from ryu.app import simple_switch_13

class IADSApp(simple_switch_13.SimpleSwitch13):
    """步骤A：只添加变量定义"""
    
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    
    def __init__(self, *args, **kwargs):
        super(IADSApp, self).__init__(*args, **kwargs)
        
        # 添加更多变量（和调试版本一样）
        self.packet_count = 0
        self.arp_count = 0
        self.icmp_count = 0
        self.lldp_count = 0
        self.is_active = False
        self.datapath = None
        
        self.logger.info("IADS Step2A: Variables added")
    
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        # 保持和最小版本完全一样
        super(IADSApp, self).switch_features_handler(ev)
        datapath = ev.msg.datapath
        self.logger.info("IADS: Switch {} connected - monitoring enabled".format(datapath.id))
        self.logger.info("IADS: Ready to monitor LLDP packets")
    
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        # 保持和最小版本完全一样
        super(IADSApp, self)._packet_in_handler(ev)
        
        self.packet_count += 1
        
        msg = ev.msg
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        
        if eth and eth.ethertype == 0x88cc:  # LLDP
            self.lldp_count += 1
            self.logger.info("IADS: LLDP packet detected (total: {})".format(self.lldp_count))
