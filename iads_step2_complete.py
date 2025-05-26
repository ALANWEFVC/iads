from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, arp, lldp, icmp, ipv4
from ryu.lib import hub
from ryu.app import simple_switch_13

class IADSApp(simple_switch_13.SimpleSwitch13):
    """第2步完整版本 - 结合C和D的成功元素"""
    
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    
    def __init__(self, *args, **kwargs):
        super(IADSApp, self).__init__(*args, **kwargs)
        
        # 来自步骤C的成功变量
        self.packet_count = 0
        self.lldp_count = 0
        self.arp_count = 0
        self.icmp_count = 0
        
        # 来自步骤D的成功变量（避免冲突的命名）
        self.is_active = False
        self.main_datapath = None  # 避免与父类冲突
        
        self.logger.info("IADS Step2 Complete: All variables initialized safely")
    
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        super(IADSApp, self).switch_features_handler(ev)
        
        datapath = ev.msg.datapath
        self.main_datapath = datapath  # 使用安全的变量名
        
        self.logger.info("IADS: Switch {} connected - ready for LLDP flows".format(datapath.id))
        
        # 现在尝试添加LLDP流表项
        try:
            ofproto = datapath.ofproto
            parser = datapath.ofproto_parser
            
            # 添加LLDP流表项（高优先级）
            match = parser.OFPMatch(eth_type=0x88cc)
            actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                              ofproto.OFPCML_NO_BUFFER)]
            self.add_flow(datapath, 100, match, actions)
            
            self.logger.info("IADS: LLDP flow successfully installed for switch {}".format(datapath.id))
            
            # 启动监控
            hub.spawn_after(3, self._start_iads_monitoring)
            
        except Exception as e:
            self.logger.error("IADS: Error installing LLDP flow: {}".format(e))
            import traceback
            self.logger.error("IADS: Traceback: {}".format(traceback.format_exc()))
    
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        # 先调用父类处理器（确保基本转发）
        super(IADSApp, self)._packet_in_handler(ev)
        
        # 然后添加IADS监控
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
        
        # 每30个包记录一次统计
        if self.packet_count % 30 == 0:
            self.logger.info("IADS: Packet stats - Total: {}, ARP: {}, ICMP: {}, LLDP: {}".format(
                self.packet_count, self.arp_count, self.icmp_count, self.lldp_count))
    
    def _start_iads_monitoring(self):
        """启动IADS监控线程"""
        self.logger.info("IADS: Starting monitoring and probing system")
        self.is_active = True
        hub.spawn(self._iads_loop)
    
    def _iads_loop(self):
        """IADS主循环"""
        while self.is_active:
            try:
                self.logger.info("IADS: Monitoring round - analyzing network state")
                
                if self.main_datapath:
                    self.logger.debug("IADS: Active monitoring on datapath {}".format(self.main_datapath.id))
                
                # 10秒一轮监控
                hub.sleep(10)
                
            except Exception as e:
                self.logger.error("IADS: Error in monitoring loop: {}".format(e))
                hub.sleep(10)
    
    def stop(self):
        """停止IADS系统"""
        self.logger.info("IADS: Stopping monitoring system")
        self.is_active = False
