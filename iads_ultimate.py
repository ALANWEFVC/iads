# iads_ultimate.py
"""IADS终极集成版本 - 完整算法 + 稳定网络"""

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, lldp, icmp, arp, ipv4
from ryu.lib import hub
from ryu.topology import event
from ryu.topology.api import get_all_switch, get_all_link
from ryu.app import simple_switch_13

import time
import json
import numpy as np
from datetime import datetime

# 导入原始IADS模块和配置
try:
    from config import *
    from modules.esm import EntityStateManager
    from modules.uq import UncertaintyQuantifier
    from modules.aps import ActiveProbingScheduler
    from modules.pe import ProbeExecutor
    from modules.rfu import ResultFusionUnit
    from modules.em import EventManager
    
    ORIGINAL_IADS_AVAILABLE = True
    print("✅ 原始IADS模块导入成功！")
except ImportError as e:
    print(f"❌ 原始IADS模块导入失败: {e}")
    ORIGINAL_IADS_AVAILABLE = False


class IADSUltimateApp(simple_switch_13.SimpleSwitch13):
    """IADS终极版本 - 集成原始算法的完整系统"""

    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(IADSUltimateApp, self).__init__(*args, **kwargs)

        self.logger.info("🚀 IADS Ultimate System Starting...")
        self.logger.info("   Integrated Adaptive Detection System")
        self.logger.info("   Enterprise SDN Intelligence + Original Algorithms")

        if not ORIGINAL_IADS_AVAILABLE:
            self.logger.error("❌ 原始IADS模块不可用，系统将退出")
            raise ImportError("Original IADS modules required")

        # 初始化原始IADS核心模块
        self.logger.info("📦 Initializing Original IADS Core Modules...")
        
        try:
            self.esm = EntityStateManager()
            self.logger.info("   ✅ ESM (Entity State Manager) initialized")
            
            self.uq = UncertaintyQuantifier(self.esm)
            self.logger.info("   ✅ UQ (Uncertainty Quantifier) initialized")
            
            self.em = EventManager(self.esm)
            self.logger.info("   ✅ EM (Event Manager) initialized")
            
            self.aps = ActiveProbingScheduler(self.esm, self.uq, self.em)
            self.logger.info("   ✅ APS (Active Probing Scheduler) initialized")
            
            self.pe = ProbeExecutor(self)
            self.logger.info("   ✅ PE (Probe Executor) initialized")
            
            self.rfu = ResultFusionUnit(self.esm, self.aps)
            self.logger.info("   ✅ RFU (Result Fusion Unit) initialized")
            
        except Exception as e:
            self.logger.error(f"❌ IADS模块初始化失败: {e}")
            raise

        # 数据路径管理（使用安全的变量名避免冲突）
        self.iads_datapaths = {}

        # 拓扑信息
        self.switches = []
        self.links = []

        # 控制标志（使用安全的变量名）
        self.iads_monitoring_active = False  # 避免与SimpleSwitch13冲突
        self.initialization_done = False

        # 启动探测线程（延迟启动避免初始化冲突）
        self.probe_thread = None

        # 统计信息
        self.stats = {
            'start_time': time.time(),
            'total_rounds': 0,
            'initialization_progress': 0
        }

        # 基础网络监控
        self.packet_count = 0
        self.lldp_count = 0
        self.arp_count = 0
        self.icmp_count = 0

        self.logger.info("🎯 IADS Ultimate System initialized successfully!")

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        """交换机连接处理 - 集成L2转发和IADS初始化"""
        # 1. 先调用父类确保L2转发正常
        super(IADSUltimateApp, self).switch_features_handler(ev)
        
        datapath = ev.msg.datapath
        self.logger.info(f"🔗 IADS: Switch {datapath.id} connected with L2 forwarding")
        
        # 2. 添加IADS专用流表项
        try:
            ofproto = datapath.ofproto
            parser = datapath.ofproto_parser
            
            # LLDP包发送到控制器（用于IADS探测）
            match = parser.OFPMatch(eth_type=0x88cc)
            actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                              ofproto.OFPCML_NO_BUFFER)]
            self.add_flow(datapath, 100, match, actions)
            
            self.logger.info(f"📡 IADS: LLDP monitoring flow installed for switch {datapath.id}")
            
            # 3. 启动IADS系统（延迟启动确保稳定）
            if not self.probe_thread:
                hub.spawn_after(5, self._start_iads_system)
                
        except Exception as e:
            self.logger.error(f"❌ Error setting up IADS for switch {datapath.id}: {e}")

    def _start_iads_system(self):
        """启动完整的IADS系统"""
        self.logger.info("🧠 Starting Complete IADS Intelligence System...")
        self.iads_monitoring_active = True
        
        # 启动原始IADS的探测循环
        self.probe_thread = hub.spawn(self._original_iads_probe_loop)
        
        self.logger.info("✅ IADS Ultimate System fully operational!")

    @set_ev_cls(ofp_event.EventOFPStateChange, [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        """处理数据路径状态变化"""
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if datapath.id not in self.iads_datapaths:
                self.logger.info(f"📍 IADS: Datapath {datapath.id} registered")
                self.iads_datapaths[datapath.id] = datapath

                # 设置PE的数据路径（原始IADS功能）
                if len(self.iads_datapaths) == 1:  # 第一个数据路径
                    try:
                        self.pe.set_datapath(datapath)
                        self.logger.info("🎯 IADS: PE datapath configured")
                    except Exception as e:
                        self.logger.error(f"❌ Error setting PE datapath: {e}")

        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.iads_datapaths:
                self.logger.info(f"📍 IADS: Datapath {datapath.id} unregistered")
                del self.iads_datapaths[datapath.id]

    @set_ev_cls(event.EventSwitchEnter)
    def _switch_enter_handler(self, ev):
        """处理交换机加入"""
        self.logger.info(f"🔄 IADS: Switch entered: {ev.switch}")
        self._update_topology()

    @set_ev_cls(event.EventLinkAdd)
    def _link_add_handler(self, ev):
        """处理链路添加"""
        self.logger.info(f"🔗 IADS: Link added: {ev.link}")
        self._update_topology()

    def _update_topology(self):
        """更新拓扑信息 - 使用原始IADS算法"""
        try:
            # 获取所有交换机和链路
            self.switches = get_all_switch(self)
            self.links = get_all_link(self)

            # 使用原始ESM更新实体
            for link in self.links:
                # 创建链路ID（与原始格式保持一致）
                entity_id = f"{link.src.dpid}-{link.src.port_no}:{link.dst.dpid}-{link.dst.port_no}"
                
                # 使用原始ESM添加实体
                self.esm.add_entity(entity_id)

                # 使用原始EM标记核心链路
                self.em.add_core_entity(entity_id)

            # 使用原始UQ更新任务池
            self.uq.update_entity_list()

            self.logger.info(f"📊 IADS: Topology updated - {len(self.switches)} switches, "
                           f"{len(self.links)} links, {len(self.esm.entities)} entities")

        except Exception as e:
            self.logger.error(f"❌ Error updating IADS topology: {e}")

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        """数据包处理 - L2转发 + IADS监控"""
        
        # 1. 首先调用父类确保L2转发正常
        super(IADSUltimateApp, self)._packet_in_handler(ev)

        # 2. 然后进行IADS相关的监控和探测
        msg = ev.msg
        datapath = msg.datapath
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)

        if not eth:
            return

        self.packet_count += 1
        dpid = datapath.id

        # 处理IADS相关的数据包（使用原始算法）
        try:
            if eth.ethertype == ethernet.ether.ETH_TYPE_LLDP:
                # 使用原始PE处理LLDP探测包
                lldp_pkt = pkt.get_protocol(lldp.lldp)
                if lldp_pkt:
                    self.lldp_count += 1
                    self.pe.handle_lldp_packet(dpid, in_port, lldp_pkt)
                    self.logger.debug(f"🔍 IADS: LLDP packet processed (total: {self.lldp_count})")

            elif eth.ethertype == ethernet.ether.ETH_TYPE_IP:
                # 使用原始PE处理ICMP探测回复
                ip_pkt = pkt.get_protocol(ipv4.ipv4)
                if ip_pkt:
                    icmp_pkt = pkt.get_protocol(icmp.icmp)
                    if icmp_pkt and icmp_pkt.type == icmp.ICMP_ECHO_REPLY:
                        self.icmp_count += 1
                        self.pe.handle_icmp_reply(dpid, in_port, icmp_pkt, ip_pkt)
                        self.logger.debug(f"🎯 IADS: ICMP reply processed (total: {self.icmp_count})")

            elif eth.ethertype == ethernet.ether.ETH_TYPE_ARP:
                # ARP包计数（L2转发已由父类处理）
                self.arp_count += 1
                if self.arp_count % 10 == 0:
                    self.logger.debug(f"📡 IADS: ARP packets processed: {self.arp_count}")

        except Exception as e:
            self.logger.error(f"❌ Error in IADS packet processing: {e}")

        # 定期统计报告
        if self.packet_count % 100 == 0:
            self.logger.info(f"📊 IADS: Packet stats - Total: {self.packet_count}, "
                           f"LLDP: {self.lldp_count}, ICMP: {self.icmp_count}, ARP: {self.arp_count}")

    def _original_iads_probe_loop(self):
        """原始IADS探测循环 - 完整算法实现"""
        self.logger.info("🔄 Original IADS probe loop started")

        # 等待拓扑发现和稳定
        hub.sleep(10)

        # 执行原始IADS初始化（全网探测）
        if not self.initialization_done:
            self._perform_original_initialization()

        # 进入原始IADS常规探测循环
        while self.iads_monitoring_active:
            try:
                # 使用原始IADS算法执行一轮探测
                self._perform_original_probe_round()

                # 使用原始配置的探测间隔
                interval = SYSTEM_CONFIG.get('probe_interval_default', 5.0)
                hub.sleep(interval)

            except Exception as e:
                self.logger.error(f"❌ Error in original IADS probe loop: {e}")
                hub.sleep(10)

    def _perform_original_initialization(self):
        """执行原始IADS初始化（全网探测）"""
        self.logger.info("🔍 Starting Original IADS Initialization...")

        try:
            # 使用原始UQ获取所有任务
            all_tasks = self.uq.get_task_pool_with_eig()
            total_tasks = len(all_tasks)

            if total_tasks == 0:
                self.logger.warning("⚠️ No tasks available for IADS initialization")
                return

            self.logger.info(f"📊 IADS: Found {total_tasks} tasks for initialization")

            # 使用原始配置的批次大小
            batch_size = SYSTEM_CONFIG['top_k']
            num_batches = (total_tasks + batch_size - 1) // batch_size

            for batch_idx in range(num_batches):
                start_idx = batch_idx * batch_size
                end_idx = min(start_idx + batch_size, total_tasks)

                # 获取当前批次的任务
                batch_tasks = [
                    {'task': task, 'priority': eig}
                    for task, eig in all_tasks[start_idx:end_idx]
                ]

                self.logger.info(f"🎯 IADS: Initialization batch {batch_idx + 1}/{num_batches}")

                # 使用原始RFU缓存探测前状态
                self.rfu.cache_states_before_probe(batch_tasks)

                # 使用原始PE执行探测
                results = self.pe.execute_batch(batch_tasks)

                # 使用原始RFU处理结果
                if results:
                    self.rfu.process_results(results)

                # 更新进度
                self.stats['initialization_progress'] = (batch_idx + 1) / num_batches

                hub.sleep(1)

            self.initialization_done = True
            self.logger.info("✅ Original IADS initialization completed successfully!")

        except Exception as e:
            self.logger.error(f"❌ Error in original IADS initialization: {e}")

    def _perform_original_probe_round(self):
        """执行原始IADS探测轮次"""
        self.stats['total_rounds'] += 1

        try:
            # 1. 使用原始EM检测事件
            self.em.check_and_detect_events()

            # 2. 使用原始APS选择探测任务
            selection_result = self.aps.select_tasks()
            selected_tasks = selection_result['tasks']

            if not selected_tasks:
                self.logger.debug("🔍 IADS: No tasks selected by APS")
                return

            self.logger.info(f"🎯 IADS Round {self.stats['total_rounds']}: "
                           f"APS selected {len(selected_tasks)} tasks, "
                           f"strategy: {selection_result['strategy']}")

            # 3. 使用原始RFU缓存探测前状态
            self.rfu.cache_states_before_probe(selected_tasks)

            # 4. 使用原始PE执行探测
            probe_results = self.pe.execute_batch(selected_tasks)

            # 5. 使用原始RFU处理结果
            if probe_results:
                process_result = self.rfu.process_results(probe_results)
                self.logger.info(f"📊 IADS: RFU processed {process_result['updated_states']} states, "
                               f"reward: {process_result['reward']:.4f}")

        except Exception as e:
            self.logger.error(f"❌ Error in original IADS probe round: {e}")

    def get_original_iads_status(self):
        """获取原始IADS系统状态"""
        uptime = time.time() - self.stats['start_time']

        try:
            return {
                'system': {
                    'uptime': uptime,
                    'monitoring_active': self.iads_monitoring_active,
                    'initialization_done': self.initialization_done,
                    'total_rounds': self.stats['total_rounds'],
                },
                'topology': {
                    'switches': len(self.switches),
                    'links': len(self.links),
                    'entities': len(self.esm.entities) if hasattr(self.esm, 'entities') else 0
                },
                'original_modules': {
                    'esm': self.esm.get_statistics() if hasattr(self.esm, 'get_statistics') else 'active',
                    'uq': self.uq.get_statistics() if hasattr(self.uq, 'get_statistics') else 'active',
                    'aps': self.aps.get_statistics() if hasattr(self.aps, 'get_statistics') else 'active',
                    'pe': self.pe.get_statistics() if hasattr(self.pe, 'get_statistics') else 'active',
                    'rfu': self.rfu.get_statistics() if hasattr(self.rfu, 'get_statistics') else 'active',
                    'em': self.em.get_statistics() if hasattr(self.em, 'get_statistics') else 'active'
                },
                'packet_stats': {
                    'total': self.packet_count,
                    'lldp': self.lldp_count,
                    'icmp': self.icmp_count,
                    'arp': self.arp_count
                }
            }
        except Exception as e:
            self.logger.error(f"Error getting IADS status: {e}")
            return {'error': str(e)}

    def get_detailed_report(self):
        """获取原始IADS详细报告"""
        try:
            return {
                'timestamp': datetime.now().isoformat(),
                'status': self.get_original_iads_status(),
                'recent_events': self.em.get_recent_events() if hasattr(self.em, 'get_recent_events') else [],
                'anomaly_summary': self.em.get_anomaly_summary() if hasattr(self.em, 'get_anomaly_summary') else {},
                'update_summary': self.rfu.get_update_summary() if hasattr(self.rfu, 'get_update_summary') else {},
                'top_uncertain_entities': self._get_top_uncertain_entities(),
                'top_unstable_entities': self._get_top_unstable_entities()
            }
        except Exception as e:
            self.logger.error(f"Error getting detailed report: {e}")
            return {'error': str(e)}

    def _get_top_uncertain_entities(self, limit=10):
        """获取不确定性最高的实体（原始算法）"""
        try:
            entity_uncertainties = {}

            if hasattr(self.esm, 'state_table'):
                for (entity_id, metric), state in self.esm.state_table.items():
                    if entity_id not in entity_uncertainties:
                        entity_uncertainties[entity_id] = []
                    if hasattr(state, 'get_uncertainty'):
                        entity_uncertainties[entity_id].append(state.get_uncertainty())

                # 计算平均不确定性
                avg_uncertainties = [
                    (entity_id, np.mean(uncertainties))
                    for entity_id, uncertainties in entity_uncertainties.items()
                    if uncertainties
                ]

                # 排序
                avg_uncertainties.sort(key=lambda x: x[1], reverse=True)
                return avg_uncertainties[:limit]
            
            return []
        except Exception as e:
            self.logger.error(f"Error getting uncertain entities: {e}")
            return []

    def _get_top_unstable_entities(self, limit=10):
        """获取最不稳定的实体（原始算法）"""
        try:
            entity_stabilities = {}

            if hasattr(self.esm, 'state_table'):
                for (entity_id, metric), state in self.esm.state_table.items():
                    if entity_id not in entity_stabilities:
                        entity_stabilities[entity_id] = []
                    if hasattr(state, 'get_stability'):
                        entity_stabilities[entity_id].append(state.get_stability())

                # 计算平均稳定性
                avg_stabilities = [
                    (entity_id, np.mean(stabilities))
                    for entity_id, stabilities in entity_stabilities.items()
                    if stabilities
                ]

                # 排序（稳定性越高表示越不稳定）
                avg_stabilities.sort(key=lambda x: x[1], reverse=True)
                return avg_stabilities[:limit]
            
            return []
        except Exception as e:
            self.logger.error(f"Error getting unstable entities: {e}")
            return []

    def stop(self):
        """停止IADS应用"""
        self.logger.info("🛑 Stopping IADS Ultimate System")
        self.iads_monitoring_active = False
        if self.probe_thread:
            hub.kill(self.probe_thread)
        self.logger.info("✅ IADS Ultimate System stopped")
