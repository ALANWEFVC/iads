#!/bin/bash

echo "修复 iads_main.py 中的变量冲突..."

# 备份
cp iads_main.py iads_main_original_backup.py

# 修复 is_active 冲突
sed -i 's/self\.is_active/self.iads_monitoring_active/g' iads_main.py

# 修复可能的其他冲突
sed -i 's/self\.datapath\([^s]\)/self.main_datapath\1/g' iads_main.py
sed -i 's/self\.datapath$/self.main_datapath/g' iads_main.py

# 检查语法
python3 -m py_compile iads_main.py

echo "修复完成！"
echo "修改的内容："
grep -n "iads_monitoring_active\|main_datapath" iads_main.py

echo ""
echo "现在可以测试: ryu-manager --verbose iads_main.py"
