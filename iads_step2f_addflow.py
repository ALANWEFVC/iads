from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, arp, lldp, icmp, ipv4
from ryu.app import simple_switch_13

class IADSApp(simple_switch_13.SimpleSwitch13):
    """步骤F：测试add_flow调用"""
    
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    
    def __init__(self, *args, **kwargs):
        super(IADSApp, self).__init__(*args, **kwargs)
        
        self.packet_count = 0
        self.lldp_count = 0
        
        self.logger.info("IADS Step2F: Testing add_flow")
    
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        self.logger.info("IADS: switch_features_handler START")
        
        super(IADSApp, self).switch_features_handler(ev)
        
        datapath = ev.msg.datapath
        self.logger.info("IADS: Switch {} parent handler completed".format(datapath.id))
        
        # 测试add_flow调用
        try:
            self.logger.info("IADS: About to test add_flow")
            
            ofproto = datapath.ofproto
            parser = datapath.ofproto_parser
            
            # 尝试添加一个简单的流表项
            match = parser.OFPMatch(eth_type=0x88cc)
            actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                              ofproto.OFPCML_NO_BUFFER)]
            self.add_flow(datapath, 100, match, actions)
            
            self.logger.info("IADS: add_flow completed successfully")
            
        except Exception as e:
            self.logger.error("IADS: add_flow failed: {}".format(e))
            import traceback
            self.logger.error("IADS: Traceback: {}".format(traceback.format_exc()))
        
        self.logger.info("IADS: switch_features_handler END")
    
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        super(IADSApp, self)._packet_in_handler(ev)
        self.packet_count += 1
        if self.packet_count % 20 == 0:
            self.logger.info("IADS: Processed {} packets".format(self.packet_count))
