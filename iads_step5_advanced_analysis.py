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
import math
from collections import deque

class EntityState:
    """增强的实体状态类"""
    def __init__(self, entity_id, state_type='link'):
        self.entity_id = entity_id
        self.state_type = state_type
        self.last_update = time.time()
        self.uncertainty = 0.5
        self.stability = 0.5
        self.probe_count = 0
        self.last_probe_time = 0
        
        # 高级分析特性
        self.probe_history = deque(maxlen=50)  # 保存最近50次探测结果
        self.performance_metrics = {
            'response_time': deque(maxlen=20),
            'success_rate': deque(maxlen=10),
            'anomaly_score': 0.0
        }
        
    def update_state(self, probe_result=None):
        """更新实体状态"""
        self.last_update = time.time()
        self.probe_count += 1
        
        if probe_result is not None:
            # 记录探测历史
            self.probe_history.append({
                'success': probe_result['success'],
                'timestamp': probe_result['timestamp'],
                'response_time': probe_result.get('response_time', 0)
            })
            
            # 更新性能指标
            if probe_result.get('response_time'):
                self.performance_metrics['response_time'].append(probe_result['response_time'])
            
            # 计算成功率
            recent_probes = list(self.probe_history)[-10:]  # 最近10次
            if recent_probes:
                success_rate = sum(1 for p in recent_probes if p['success']) / len(recent_probes)
                self.performance_metrics['success_rate'].append(success_rate)
            
            # 更新不确定性和稳定性
            if probe_result['success']:
                self.uncertainty = max(0.05, self.uncertainty * 0.9)
                self.stability = min(1.0, self.stability * 1.05)
            else:
                self.uncertainty = min(0.95, self.uncertainty * 1.15)
                self.stability = max(0.05, self.stability * 0.85)
            
            # 计算异常分数
            self._calculate_anomaly_score()
        
    def _calculate_anomaly_score(self):
        """计算异常分数"""
        score = 0.0
        
        # 基于成功率的异常
        if self.performance_metrics['success_rate']:
            recent_success_rate = self.performance_metrics['success_rate'][-1]
            if recent_success_rate < 0.8:
                score += (0.8 - recent_success_rate) * 2
        
        # 基于响应时间的异常
        if len(self.performance_metrics['response_time']) > 5:
            times = list(self.performance_metrics['response_time'])
            avg_time = sum(times) / len(times)
            recent_time = times[-1]
            if recent_time > avg_time * 2:  # 响应时间翻倍
                score += 0.3
        
        # 基于稳定性的异常
        if self.stability < 0.3:
            score += (0.3 - self.stability) * 1.5
        
        self.performance_metrics['anomaly_score'] = min(1.0, score)
        
    def get_priority(self):
        """计算探测优先级（增强版）"""
        age = time.time() - self.last_update
        time_factor = 1 + age / 60
        
        # 综合考虑不确定性、异常分数和时间衰减
        priority = (self.uncertainty * 0.6 + 
                   self.performance_metrics['anomaly_score'] * 0.4) * time_factor
        
        return priority
    
    def is_anomalous(self, threshold=0.5):
        """判断实体是否异常"""
        return self.performance_metrics['anomaly_score'] > threshold

class IADSApp(simple_switch_13.SimpleSwitch13):
    """第5步：高级分析和异常检测"""
    
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    
    def __init__(self, *args, **kwargs):
        super(IADSApp, self).__init__(*args, **kwargs)
        
        # 基础监控
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
        
        # IADS核心组件
        self.entity_states = {}
        self.probe_queue = []
        self.probe_results = []
        
        # 高级分析组件
        self.anomaly_detector = {
            'detected_anomalies': [],
            'alert_threshold': 0.6,
            'last_analysis': time.time()
        }
        
        self.adaptive_scheduler = {
            'probe_interval': 10,  # 动态调整的探测间隔
            'load_factor': 0.5,
            'last_adjustment': time.time()
        }
        
        # 统计信息
        self.stats = {
            'total_probes': 0,
            'successful_probes': 0,
            'failed_probes': 0,
            'anomalies_detected': 0,
            'false_positives': 0,
            'start_time': time.time()
        }
        
        self.logger.info("IADS Step5: Advanced analysis and anomaly detection enabled")
    
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        super(IADSApp, self).switch_features_handler(ev)
        
        datapath = ev.msg.datapath
        self.main_datapath = datapath
        self.iads_monitoring_active = True
        
        self.logger.info("IADS: Switch {} connected, advanced analysis active".format(datapath.id))
        
        try:
            ofproto = datapath.ofproto
            parser = datapath.ofproto_parser
            
            match = parser.OFPMatch(eth_type=0x88cc)
            actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                              ofproto.OFPCML_NO_BUFFER)]
            self.add_flow(datapath, 100, match, actions)
            
            self.logger.info("IADS: LLDP flow installed successfully")
            
            # 启动完整的IADS系统
            hub.spawn_after(3, self._start_advanced_iads_system)
            
        except Exception as e:
            self.logger.error("IADS: Error: {}".format(e))
    
    @set_ev_cls(event.EventSwitchEnter)
    def _switch_enter_handler(self, ev):
        self.logger.info("IADS: Switch entered: {}".format(ev.switch))
        self._update_topology()
    
    @set_ev_cls(event.EventLinkAdd)
    def _link_add_handler(self, ev):
        self.logger.info("IADS: Link added: {}".format(ev.link))
        self._update_topology()
    
    def _update_topology(self):
        """更新拓扑信息和实体状态"""
        try:
            self.switches = get_all_switch(self)
            self.links = get_all_link(self)
            
            for link in self.links:
                entity_id = "link_{}_{}_{}_{}".format(
                    link.src.dpid, link.src.port_no,
                    link.dst.dpid, link.dst.port_no
                )
                
                self.topology_entities[entity_id] = {
                    'type': 'link',
                    'src_dpid': link.src.dpid,
                    'src_port': link.src.port_no,
                    'dst_dpid': link.dst.dpid,
                    'dst_port': link.dst.port_no,
                    'discovered_at': time.time()
                }
                
                if entity_id not in self.entity_states:
                    self.entity_states[entity_id] = EntityState(entity_id, 'link')
                    self.logger.info("IADS: New entity state created: {}".format(entity_id))
            
            self.logger.info("IADS: Topology updated - {} entities with enhanced monitoring".format(
                len(self.entity_states)))
                
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
                self._process_enhanced_probe_result(msg, True)
                
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
            self.logger.info("IADS: Advanced stats - Total: {}, ARP: {}, ICMP: {}, LLDP: {}".format(
                self.packet_count, self.arp_count, self.icmp_count, self.lldp_count))
    
    def _process_enhanced_probe_result(self, msg, success):
        """处理增强的探测结果"""
        try:
            in_port = msg.match['in_port']
            datapath_id = msg.datapath.id
            response_time = random.uniform(0.001, 0.050)  # 模拟响应时间
            
            for entity_id, entity_state in self.entity_states.items():
                if entity_state.state_type == 'link':
                    probe_result = {
                        'success': success,
                        'timestamp': time.time(),
                        'datapath_id': datapath_id,
                        'in_port': in_port,
                        'response_time': response_time
                    }
                    
                    entity_state.update_state(probe_result)
                    self.stats['total_probes'] += 1
                    
                    if success:
                        self.stats['successful_probes'] += 1
                    else:
                        self.stats['failed_probes'] += 1
                    
                    # 检查异常
                    if entity_state.is_anomalous(self.anomaly_detector['alert_threshold']):
                        self._handle_anomaly_detection(entity_id, entity_state)
                    
                    break
                    
        except Exception as e:
            self.logger.error("IADS: Error processing enhanced probe result: {}".format(e))
    
    def _handle_anomaly_detection(self, entity_id, entity_state):
        """处理异常检测"""
        anomaly_info = {
            'entity_id': entity_id,
            'timestamp': time.time(),
            'anomaly_score': entity_state.performance_metrics['anomaly_score'],
            'uncertainty': entity_state.uncertainty,
            'stability': entity_state.stability
        }
        
        self.anomaly_detector['detected_anomalies'].append(anomaly_info)
        self.stats['anomalies_detected'] += 1
        
        self.logger.warning("IADS: ANOMALY DETECTED - Entity: {}, Score: {:.3f}, Uncertainty: {:.3f}".format(
            entity_id, entity_state.performance_metrics['anomaly_score'], entity_state.uncertainty))
    
    def _start_advanced_iads_system(self):
        """启动高级IADS系统"""
        self.logger.info("IADS: Starting advanced monitoring, analysis and anomaly detection")
        hub.spawn(self._iads_main_loop)
        hub.spawn(self._advanced_probe_scheduler)
        hub.spawn(self._anomaly_analysis_engine)
    
    def _iads_main_loop(self):
        """IADS主循环"""
        while self.iads_monitoring_active:
            try:
                self._update_topology()
                
                if len(self.entity_states) > 0:
                    # 计算系统级统计
                    uncertainties = [s.uncertainty for s in self.entity_states.values()]
                    stabilities = [s.stability for s in self.entity_states.values()]
                    anomaly_scores = [s.performance_metrics['anomaly_score'] for s in self.entity_states.values()]
                    
                    avg_uncertainty = sum(uncertainties) / len(uncertainties)
                    avg_stability = sum(stabilities) / len(stabilities)
                    avg_anomaly_score = sum(anomaly_scores) / len(anomaly_scores)
                    max_anomaly_score = max(anomaly_scores)
                    
                    anomalous_entities = sum(1 for s in self.entity_states.values() 
                                           if s.is_anomalous(self.anomaly_detector['alert_threshold']))
                    
                    self.logger.info("IADS: System Analysis - {} entities, {} anomalous, avg uncertainty: {:.3f}, avg stability: {:.3f}, max anomaly: {:.3f}".format(
                        len(self.entity_states), anomalous_entities, avg_uncertainty, avg_stability, max_anomaly_score))
                
                hub.sleep(25)  # 25秒主循环
                
            except Exception as e:
                self.logger.error("IADS: Error in advanced main loop: {}".format(e))
                hub.sleep(25)
    
    def _advanced_probe_scheduler(self):
        """高级自适应探测调度器"""
        while self.iads_monitoring_active:
            try:
                if self.entity_states:
                    # 计算系统负载并调整探测间隔
                    avg_anomaly_score = sum(s.performance_metrics['anomaly_score'] 
                                          for s in self.entity_states.values()) / len(self.entity_states)
                    
                    # 自适应调整探测间隔
                    if avg_anomaly_score > 0.4:
                        self.adaptive_scheduler['probe_interval'] = max(5, self.adaptive_scheduler['probe_interval'] * 0.8)
                    else:
                        self.adaptive_scheduler['probe_interval'] = min(15, self.adaptive_scheduler['probe_interval'] * 1.1)
                    
                    # 选择高优先级实体
                    priorities = [(entity_id, state.get_priority()) 
                                 for entity_id, state in self.entity_states.items()]
                    priorities.sort(key=lambda x: x[1], reverse=True)
                    
                    # 动态选择探测数量
                    num_probes = min(5, max(1, int(len(priorities) * 0.3)))
                    top_entities = priorities[:num_probes]
                    
                    for entity_id, priority in top_entities:
                        self.logger.info("IADS: Advanced probe scheduled - Entity: {}, Priority: {:.3f}".format(
                            entity_id, priority))
                        self._simulate_advanced_probe(entity_id)
                
                hub.sleep(self.adaptive_scheduler['probe_interval'])
                
            except Exception as e:
                self.logger.error("IADS: Error in advanced probe scheduler: {}".format(e))
                hub.sleep(10)
    
    def _anomaly_analysis_engine(self):
        """异常分析引擎"""
        while self.iads_monitoring_active:
            try:
                current_time = time.time()
                
                # 定期清理旧的异常记录
                cutoff_time = current_time - 300  # 5分钟前
                self.anomaly_detector['detected_anomalies'] = [
                    a for a in self.anomaly_detector['detected_anomalies'] 
                    if a['timestamp'] > cutoff_time
                ]
                
                # 生成异常报告
                if len(self.anomaly_detector['detected_anomalies']) > 0:
                    recent_anomalies = len(self.anomaly_detector['detected_anomalies'])
                    self.logger.info("IADS: Anomaly Report - {} recent anomalies detected".format(recent_anomalies))
                    
                    # 分析异常模式
                    high_score_anomalies = [a for a in self.anomaly_detector['detected_anomalies'] 
                                          if a['anomaly_score'] > 0.8]
                    
                    if high_score_anomalies:
                        self.logger.warning("IADS: HIGH PRIORITY - {} severe anomalies detected!".format(
                            len(high_score_anomalies)))
                
                self.anomaly_detector['last_analysis'] = current_time
                hub.sleep(60)  # 每分钟分析一次
                
            except Exception as e:
                self.logger.error("IADS: Error in anomaly analysis engine: {}".format(e))
                hub.sleep(60)
    
    def _simulate_advanced_probe(self, entity_id):
        """模拟高级探测"""
        try:
            # 模拟更复杂的探测结果
            base_success_rate = 0.85
            
            # 根据实体当前状态调整成功率
            if entity_id in self.entity_states:
                entity_state = self.entity_states[entity_id]
                
                # 稳定的实体更容易探测成功
                adjusted_success_rate = base_success_rate * (0.5 + entity_state.stability * 0.5)
                
                success = random.random() < adjusted_success_rate
                response_time = random.uniform(0.001, 0.100)
                
                # 异常情况下响应时间更长
                if entity_state.performance_metrics['anomaly_score'] > 0.5:
                    response_time *= (1 + entity_state.performance_metrics['anomaly_score'])
                
                probe_result = {
                    'success': success,
                    'timestamp': time.time(),
                    'response_time': response_time,
                    'simulated': True,
                    'advanced': True
                }
                
                entity_state.update_state(probe_result)
                self.stats['total_probes'] += 1
                
                if success:
                    self.stats['successful_probes'] += 1
                else:
                    self.stats['failed_probes'] += 1
                
                self.logger.debug("IADS: Advanced probe completed - Entity: {}, Success: {}, Response: {:.3f}ms, Anomaly: {:.3f}".format(
                    entity_id, success, response_time * 1000, entity_state.performance_metrics['anomaly_score']))
        
        except Exception as e:
            self.logger.error("IADS: Error in advanced probe simulation: {}".format(e))
    
    def get_advanced_iads_status(self):
        """获取高级IADS状态"""
        uptime = time.time() - self.stats['start_time']
        
        entity_analysis = {}
        if self.entity_states:
            uncertainties = [s.uncertainty for s in self.entity_states.values()]
            stabilities = [s.stability for s in self.entity_states.values()]
            anomaly_scores = [s.performance_metrics['anomaly_score'] for s in self.entity_states.values()]
            
            entity_analysis = {
                'total_entities': len(self.entity_states),
                'avg_uncertainty': sum(uncertainties) / len(uncertainties),
                'max_uncertainty': max(uncertainties),
                'avg_stability': sum(stabilities) / len(stabilities),
                'min_stability': min(stabilities),
                'avg_anomaly_score': sum(anomaly_scores) / len(anomaly_scores),
                'max_anomaly_score': max(anomaly_scores),
                'anomalous_entities': sum(1 for s in self.entity_states.values() 
                                        if s.is_anomalous(self.anomaly_detector['alert_threshold']))
            }
        
        return {
            'monitoring_active': self.iads_monitoring_active,
            'uptime': uptime,
            'topology': {
                'switches': len(self.switches),
                'links': len(self.links),
                'entities': len(self.topology_entities)
            },
            'entity_analysis': entity_analysis,
            'anomaly_detection': {
                'total_anomalies': len(self.anomaly_detector['detected_anomalies']),
                'alert_threshold': self.anomaly_detector['alert_threshold'],
                'recent_anomalies': len([a for a in self.anomaly_detector['detected_anomalies'] 
                                       if time.time() - a['timestamp'] < 300])
            },
            'adaptive_scheduling': self.adaptive_scheduler.copy(),
            'probe_stats': self.stats.copy(),
            'packet_stats': {
                'total': self.packet_count,
                'arp': self.arp_count,
                'icmp': self.icmp_count,
                'lldp': self.lldp_count
            }
        }
