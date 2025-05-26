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
import time
import random

class EntityState:
    """简化的实体状态类"""
    def __init__(self, entity_id, state_type='link'):
        self.entity_id = entity_id
        self.state_type = state_type
        self.last_update = time.time()
        self.uncertainty = 0.5  # 初始不确定性
        self.stability = 0.5    # 初始稳定性
        self.probe_count = 0
        self.last_probe_time = 0
        
    def update_state(self, probe_result=None):
        """更新实体状态"""
        self.last_update = time.time()
        self.probe_count += 1
        
        if probe_result is not None:
            # 根据探测结果更新不确定性
            if probe_result['success']:
                self.uncertainty = max(0.1, self.uncertainty * 0.9)  # 降低不确定性
                self.stability = min(1.0, self.stability * 1.1)      # 提高稳定性
            else:
                self.uncertainty = min(1.0, self.uncertainty * 1.1)  # 增加不确定性
                self.stability = max(0.1, self.stability * 0.9)      # 降低稳定性
        
    def get_priority(self):
        """计算探测优先级"""
        age = time.time() - self.last_update
        return self.uncertainty * (1 + age / 60)  # 不确定性 * 时间衰减因子

class IADSApp(simple_switch_13.SimpleSwitch13):
    """第4步：添加实体状态管理"""
    
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
        self.topology_entities = {}
        
        # IADS实体状态管理
        self.entity_states = {}     # 实体状态表 {entity_id: EntityState}
        self.probe_queue = []       # 探测队列
        self.probe_results = []     # 探测结果历史
        
        # 统计信息
        self.stats = {
            'total_probes': 0,
            'successful_probes': 0,
            'failed_probes': 0,
            'start_time': time.time()
        }
        
        self.logger.info("IADS Step4: Entity state management enabled")
    
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        super(IADSApp, self).switch_features_handler(ev)
        
        datapath = ev.msg.datapath
        self.main_datapath = datapath
        self.iads_monitoring_active = True
        
        self.logger.info("IADS: Switch {} connected, state management active".format(datapath.id))
        
        # 添加LLDP流表项
        try:
            ofproto = datapath.ofproto
            parser = datapath.ofproto_parser
            
            match = parser.OFPMatch(eth_type=0x88cc)
            actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                              ofproto.OFPCML_NO_BUFFER)]
            self.add_flow(datapath, 100, match, actions)
            
            self.logger.info("IADS: LLDP flow installed successfully")
            
            # 启动IADS系统
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
        """更新拓扑信息和实体状态"""
        try:
            # 获取拓扑信息
            self.switches = get_all_switch(self)
            self.links = get_all_link(self)
            
            # 更新实体信息和状态
            for link in self.links:
                entity_id = "link_{}_{}_{}_{}".format(
                    link.src.dpid, link.src.port_no,
                    link.dst.dpid, link.dst.port_no
                )
                
                # 更新拓扑实体
                self.topology_entities[entity_id] = {
                    'type': 'link',
                    'src_dpid': link.src.dpid,
                    'src_port': link.src.port_no,
                    'dst_dpid': link.dst.dpid,
                    'dst_port': link.dst.port_no,
                    'discovered_at': time.time()
                }
                
                # 创建或更新实体状态
                if entity_id not in self.entity_states:
                    self.entity_states[entity_id] = EntityState(entity_id, 'link')
                    self.logger.info("IADS: New entity state created: {}".format(entity_id))
            
            self.logger.info("IADS: Topology updated - {} switches, {} links, {} entities, {} states".format(
                len(self.switches), len(self.links), len(self.topology_entities), len(self.entity_states)))
                
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
                # LLDP包可以作为链路状态的探测结果
                self._process_lldp_probe_result(msg, True)
                
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
    
    def _process_lldp_probe_result(self, msg, success):
        """处理LLDP探测结果"""
        try:
            in_port = msg.match['in_port']
            datapath_id = msg.datapath.id
            
            # 寻找相关的链路实体
            for entity_id, entity_state in self.entity_states.items():
                if entity_state.state_type == 'link':
                    # 简化：假设LLDP包对应某个链路实体
                    probe_result = {
                        'success': success,
                        'timestamp': time.time(),
                        'datapath_id': datapath_id,
                        'in_port': in_port
                    }
                    
                    entity_state.update_state(probe_result)
                    self.stats['total_probes'] += 1
                    
                    if success:
                        self.stats['successful_probes'] += 1
                    else:
                        self.stats['failed_probes'] += 1
                    
                    self.logger.debug("IADS: Updated state for entity {} - uncertainty: {:.3f}, stability: {:.3f}".format(
                        entity_id, entity_state.uncertainty, entity_state.stability))
                    break
                    
        except Exception as e:
            self.logger.error("IADS: Error processing probe result: {}".format(e))
    
    def _start_iads_system(self):
        """启动IADS系统"""
        self.logger.info("IADS: Starting monitoring, topology discovery and state management")
        hub.spawn(self._iads_main_loop)
        hub.spawn(self._iads_probe_scheduler)
    
    def _iads_main_loop(self):
        """IADS主循环"""
        while self.iads_monitoring_active:
            try:
                # 定期更新拓扑
                self._update_topology()
                
                # 统计报告
                if len(self.entity_states) > 0:
                    avg_uncertainty = sum(s.uncertainty for s in self.entity_states.values()) / len(self.entity_states)
                    avg_stability = sum(s.stability for s in self.entity_states.values()) / len(self.entity_states)
                    
                    self.logger.info("IADS: System status - {} entities, avg uncertainty: {:.3f}, avg stability: {:.3f}".format(
                        len(self.entity_states), avg_uncertainty, avg_stability))
                
                hub.sleep(20)  # 20秒主循环
                
            except Exception as e:
                self.logger.error("IADS: Error in main loop: {}".format(e))
                hub.sleep(20)
    
    def _iads_probe_scheduler(self):
        """IADS探测调度器"""
        while self.iads_monitoring_active:
            try:
                # 选择高优先级实体进行探测
                if self.entity_states:
                    # 计算所有实体的优先级
                    priorities = [(entity_id, state.get_priority()) 
                                 for entity_id, state in self.entity_states.items()]
                    
                    # 按优先级排序
                    priorities.sort(key=lambda x: x[1], reverse=True)
                    
                    # 选择前几个进行探测
                    top_entities = priorities[:min(3, len(priorities))]
                    
                    for entity_id, priority in top_entities:
                        self.logger.info("IADS: Scheduling probe for entity {} (priority: {:.3f})".format(
                            entity_id, priority))
                        
                        # 模拟探测（实际实现中会发送真实的探测包）
                        self._simulate_probe(entity_id)
                
                hub.sleep(10)  # 10秒调度一次
                
            except Exception as e:
                self.logger.error("IADS: Error in probe scheduler: {}".format(e))
                hub.sleep(10)
    
    def _simulate_probe(self, entity_id):
        """模拟探测（实际实现中会发送真实探测包）"""
        try:
            # 模拟探测结果（90%成功率）
            success = random.random() < 0.9
            
            probe_result = {
                'success': success,
                'timestamp': time.time(),
                'simulated': True
            }
            
            if entity_id in self.entity_states:
                self.entity_states[entity_id].update_state(probe_result)
                self.stats['total_probes'] += 1
                
                if success:
                    self.stats['successful_probes'] += 1
                else:
                    self.stats['failed_probes'] += 1
                
                self.logger.debug("IADS: Simulated probe for {} - result: {}, new uncertainty: {:.3f}".format(
                    entity_id, success, self.entity_states[entity_id].uncertainty))
        
        except Exception as e:
            self.logger.error("IADS: Error in probe simulation: {}".format(e))
    
    def get_iads_status(self):
        """获取IADS状态"""
        uptime = time.time() - self.stats['start_time']
        
        return {
            'monitoring_active': self.iads_monitoring_active,
            'uptime': uptime,
            'topology': {
                'switches': len(self.switches),
                'links': len(self.links),
                'entities': len(self.topology_entities)
            },
            'entity_management': {
                'total_entities': len(self.entity_states),
                'avg_uncertainty': sum(s.uncertainty for s in self.entity_states.values()) / len(self.entity_states) if self.entity_states else 0,
                'avg_stability': sum(s.stability for s in self.entity_states.values()) / len(self.entity_states) if self.entity_states else 0
            },
            'probe_stats': self.stats.copy(),
            'packet_stats': {
                'total': self.packet_count,
                'arp': self.arp_count,
                'icmp': self.icmp_count,
                'lldp': self.lldp_count
            }
        }
