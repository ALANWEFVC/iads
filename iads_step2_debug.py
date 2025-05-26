from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, arp, lldp, icmp, ipv4
from ryu.lib import hub
from ryu.app import simple_switch_13

class IADSApp(simple_switch_13.SimpleSwitch13):
    """第2步调试版本"""
    
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
        
        self.logger.info("IADS Step2 Debug: initialized")
    
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        self.logger.info("IADS DEBUG: switch_features_handler called - START")
        
        try:
            self.logger.info("IADS DEBUG: About to call super()")
            super(IADSApp, self).switch_features_handler(ev)
            self.logger.info("IADS DEBUG: super() call completed")
            
            datapath = ev.msg.datapath
            self.datapath = datapath
            
            self.logger.info("IADS DEBUG: Switch {} basic flows installed".format(datapath.id))
            
            # 先不添加LLDP流表项，只记录
            self.logger.info("IADS DEBUG: Would add LLDP flow here")
            self.logger.info("IADS DEBUG: switch_features_handler completed successfully")
            
        except Exception as e:
            self.logger.error("IADS DEBUG: Exception in switch_features_handler: {}".format(e))
            import traceback
            self.logger.error("IADS DEBUG: Traceback: {}".format(traceback.format_exc()))
    
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        # 只调用父类，不添加任何额外处理
        super(IADSApp, self)._packet_in_handler(ev)
        
        # 简单计数
        self.packet_count += 1
        if self.packet_count % 20 == 0:
            self.logger.info("IADS DEBUG: Processed {} packets".format(self.packet_count))
