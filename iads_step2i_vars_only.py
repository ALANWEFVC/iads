from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, arp, lldp, icmp, ipv4
from ryu.lib import hub
from ryu.app import simple_switch_13

class IADSApp(simple_switch_13.SimpleSwitch13):
    """步骤I：只测试所有变量组合，不调用add_flow"""
    
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    
    def __init__(self, *args, **kwargs):
        super(IADSApp, self).__init__(*args, **kwargs)
        
        # 所有变量（从步骤C和D复制）
        self.packet_count = 0
        self.lldp_count = 0
        self.arp_count = 0
        self.icmp_count = 0
        self.is_active = False
        self.main_datapath = None
        
        self.logger.info("IADS Step2I: All variables, no add_flow")
    
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        self.logger.info("IADS: switch_features_handler START")
        
        super(IADSApp, self).switch_features_handler(ev)
        
        datapath = ev.msg.datapath
        self.main_datapath = datapath  # 设置变量
        
        self.logger.info("IADS: Switch {} connected, datapath saved".format(datapath.id))
        
        # 不调用add_flow，只设置状态
        self.is_active = True
        
        self.logger.info("IADS: switch_features_handler END")
    
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        super(IADSApp, self)._packet_in_handler(ev)
        
        self.packet_count += 1
        if self.packet_count % 20 == 0:
            self.logger.info("IADS: Processed {} packets, active={}".format(
                self.packet_count, self.is_active))
