from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, arp, lldp, icmp, ipv4
from ryu.lib import hub
from ryu.topology import event
from ryu.topology.api import get_all_switch, get_all_link
from ryu.app import simple_switch_13

class IADSApp(simple_switch_13.SimpleSwitch13):
    """第3步：添加拓扑发现功能"""
    
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    
    def __init__(self, *args, **kwargs):
        super(IADSApp, self).__init__(*args, **kwargs)
        
        # 监控计数
        self.packet_count = 0
        self.lldp_count = 0
        self.arp_count = 0
        self.icmp_count = 0
        
        # 状态管理
        self.iads_monitoring_active = False
        self.main_datapath = None
        
        # 拓扑信息
        self.switches = []
        self.links = []
        self.topology_entities = {}  # 存储网络实体信息
        
        self.logger.info("IADS Step3: Topology discovery enabled")
    
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        super(IADSApp, self).switch_features_handler(ev)
        
        datapath = ev.msg.datapath
        self.main_datapath = datapath
        self.iads_monitoring_active = True
        
        self.logger.info("IADS: Switch {} connected, monitoring_active={}".format(
            datapath.id, self.iads_monitoring_active))
        
        # 添加LLDP流表项
        try:
            ofproto = datapath.ofproto
            parser = datapath.ofproto_parser
            
            match = parser.OFPMatch(eth_type=0x88cc)
            actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                              ofproto.OFPCML_NO_BUFFER)]
            self.add_flow(datapath, 100, match, actions)
            
            self.logger.info("IADS: LLDP flow installed successfully")
            
            # 启动监控
            hub.spawn_after(3, self._start_iads_system)
            
        except Exception as e:
            self.logger.error("IADS: Error: {}".format(e))
    
    @set_ev_cls(event.EventSwitchEnter)
    def _switch_enter_handler(self, ev):
        """处理交换机加入事件"""
        self.logger.info("IADS: Switch entered: {}".format(ev.switch))
        self._update_topology()
    
    @set_ev_cls(event.EventLinkAdd)
    def _link_add_handler(self, ev):
        """处理链路添加事件"""
        self.logger.info("IADS: Link added: {}".format(ev.link))
        self._update_topology()
    
    def _update_topology(self):
        """更新拓扑信息"""
        try:
            # 获取所有交换机
            self.switches = get_all_switch(self)
            
            # 获取所有链路
            self.links = get_all_link(self)
            
            # 更新实体信息
            for link in self.links:
                # 创建链路实体ID
                entity_id = "link_{}_{}_{}_{}".format(
                    link.src.dpid, link.src.port_no,
                    link.dst.dpid, link.dst.port_no
                )
                
                # 存储实体信息
                self.topology_entities[entity_id] = {
                    'type': 'link',
                    'src_dpid': link.src.dpid,
                    'src_port': link.src.port_no,
                    'dst_dpid': link.dst.dpid,
                    'dst_port': link.dst.port_no,
                    'discovered_at': hub.time()
                }
            
            self.logger.info("IADS: Topology updated - {} switches, {} links, {} entities".format(
                len(self.switches), len(self.links), len(self.topology_entities)))
                
        except Exception as e:
            self.logger.error("IADS: Error updating topology: {}".format(e))
    
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
                # LLDP包会触发拓扑发现
                
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
        
        if self.packet_count % 50 == 0:
            self.logger.info("IADS: Stats - Total: {}, ARP: {}, ICMP: {}, LLDP: {}".format(
                self.packet_count, self.arp_count, self.icmp_count, self.lldp_count))
    
    def _start_iads_system(self):
        """启动IADS系统"""
        self.logger.info("IADS: Starting monitoring and topology discovery system")
        hub.spawn(self._iads_main_loop)
    
    def _iads_main_loop(self):
        """IADS主循环"""
        while self.iads_monitoring_active:
            try:
                self.logger.info("IADS: Monitoring round - topology: {} switches, {} links, {} entities".format(
                    len(self.switches), len(self.links), len(self.topology_entities)))
                
                # 每轮监控输出当前状态
                if self.main_datapath:
                    self.logger.debug("IADS: Active monitoring on datapath {}".format(
                        self.main_datapath.id))
                
                # 定期强制更新拓扑
                self._update_topology()
                
                hub.sleep(15)  # 15秒一轮
                
            except Exception as e:
                self.logger.error("IADS: Error in main loop: {}".format(e))
                hub.sleep(15)
    
    def get_iads_status(self):
        """获取IADS状态"""
        return {
            'monitoring_active': self.iads_monitoring_active,
            'switches': len(self.switches),
            'links': len(self.links),
            'entities': len(self.topology_entities),
            'packet_stats': {
                'total': self.packet_count,
                'arp': self.arp_count,
                'icmp': self.icmp_count,
                'lldp': self.lldp_count
            }
        }
