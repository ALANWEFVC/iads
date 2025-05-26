#!/bin/bash
# run.sh - IADS启动脚本

# 设置颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting IADS Ultimate Framework${NC}"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python3 is not installed${NC}"
    exit 1
fi

# 检查Ryu是否安装
if ! command -v ryu-manager &> /dev/null; then
    echo -e "${RED}Error: Ryu is not installed${NC}"
    echo "Please install Ryu: pip install ryu"
    exit 1
fi

# 创建日志目录
mkdir -p logs

# 清理旧的日志
echo -e "${YELLOW}Cleaning old logs...${NC}"
find logs -name "*.log" -mtime +7 -delete

# 设置Python路径
export PYTHONPATH=$PYTHONPATH:$(pwd)

# 启动参数 - 修改为使用iads_ultimate
RYU_APP="iads_ultimate.py"  # 改为新文件名
OBSERVE_LINKS="--observe-links"
OFPROTO="--ofp-tcp-listen-port 6633"
VERBOSE="--verbose"
LOG_FILE="--log-file logs/iads_ultimate.log"  # 修改日志文件名

# 检查是否需要REST API
if [ "$1" == "--with-rest" ]; then
    echo -e "${GREEN}Starting IADS Ultimate with REST API support${NC}"
    REST_API="ryu.app.ofctl_rest"
    ryu-manager $RYU_APP $REST_API $OBSERVE_LINKS $OFPROTO $VERBOSE $LOG_FILE
else
    echo -e "${GREEN}Starting IADS Ultimate without REST API${NC}"
    ryu-manager $RYU_APP $OBSERVE_LINKS $OFPROTO $VERBOSE $LOG_FILE
fi
