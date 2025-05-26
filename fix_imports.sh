#!/bin/bash

echo "开始修复IADS相对导入问题..."

# 备份原始文件
echo "备份原始文件..."
find . -name "*.py" -exec cp {} {}.backup \;

# 修复 modules/ 目录下的相对导入
echo "修复 modules/ 目录..."

# 修复 from ..config import *
find ./modules -name "*.py" -exec sed -i 's/from \.\.config import \*/from config import */g' {} \;

# 修复 from ..utils.xxx import xxx
sed -i 's/from \.\.utils\.distributions import/from utils.distributions import/g' ./modules/uq.py
sed -i 's/from \.\.utils\.distributions import/from utils.distributions import/g' ./modules/esm.py

# 修复 modules/__init__.py 中的相对导入
sed -i 's/from \.esm import/from modules.esm import/g' ./modules/__init__.py
sed -i 's/from \.uq import/from modules.uq import/g' ./modules/__init__.py
sed -i 's/from \.aps import/from modules.aps import/g' ./modules/__init__.py
sed -i 's/from \.pe import/from modules.pe import/g' ./modules/__init__.py
sed -i 's/from \.rfu import/from modules.rfu import/g' ./modules/__init__.py
sed -i 's/from \.em import/from modules.em import/g' ./modules/__init__.py

# 修复 utils/__init__.py 中的相对导入
echo "修复 utils/ 目录..."
sed -i 's/from \.distributions import/from utils.distributions import/g' ./utils/__init__.py
sed -i 's/from \.network_utils import/from utils.network_utils import/g' ./utils/__init__.py
sed -i 's/from \.logger import/from utils.logger import/g' ./utils/__init__.py

echo "修复完成！"

# 显示修改的文件
echo "已修改的文件:"
find . -name "*.py" -newer fix_imports.sh
