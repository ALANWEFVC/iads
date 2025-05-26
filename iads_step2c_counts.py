from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, arp, lldp, icmp, ipv4
from ryu.app import simple_switch_13

class IADSApp(simple_switch_13.SimpleSwitch13):
    """步骤C：只添加计数变量"""
    
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    
    def __init__(self, *args, **kwargs):
        super(IADSApp, self).__init__(*args, **kwargs)
        
        # 成功的变量
        self.packet_count = 0
        self.lldp_count = 0
        
        # 添加的变量
        self.arp_count = 0
        self.icmp_count = 0
        
        self.logger.info("IADS Step2C: Count variables added")
    
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        super(IADSApp, self).switch_features_handler(ev)
        datapath = ev.msg.datapath
        self.logger.info("IADS: Switch {} connected".format(datapath.id))
    
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        super(IADSApp, self)._packet_in_handler(ev)
        self.packet_count += 1
        if self.packet_count % 20 == 0:
            self.logger.info("IADS: Processed {} packets".format(self.packet_count))
