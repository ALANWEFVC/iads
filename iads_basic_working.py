from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, arp
from ryu.app import simple_switch_13

class IADSApp(simple_switch_13.SimpleSwitch13):
    """基础工作版本"""
    
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    
    def __init__(self, *args, **kwargs):
        super(IADSApp, self).__init__(*args, **kwargs)
        self.logger.info("IADS Basic Working Version initialized")
    
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        super(IADSApp, self).switch_features_handler(ev)
        datapath = ev.msg.datapath
        self.logger.info("IADS: Switch {} connected successfully".format(datapath.id))
    
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        super(IADSApp, self)._packet_in_handler(ev)
        # 基本版本只做转发，不添加额外处理
