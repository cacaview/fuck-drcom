# 更新日志

## [v1.1.0] - 2025-11-06

### 🎯 重大变更

#### 项目结构重组
- 将代码按功能分类到不同文件夹
- `common/` - 公共模块（配置、日志、登录）
- `server/` - 服务端程序
- `client/` - 命令行客户端
- `client_gui/` - GUI客户端
- `docs/` - 文档集中管理

#### 免责声明添加
- ⚠️ 在所有模块的 `__init__.py` 中添加免责声明
- ⚠️ 在所有主要文件顶部添加免责声明
- ⚠️ 在启动脚本中显示免责声明
- ⚠️ 在 README.md 顶部添加醒目的免责声明

**免责声明内容**：
> 此软件仅供学习用途使用，使用此软件则代表您愿意承担所造成的法律问题，
> 开发者不为此承担任何法律义务。

### ✨ 新增功能

#### 启动脚本
- 新增 `start_server.py` - 服务端启动脚本
- 新增 `start_client.py` - 客户端启动脚本
- 新增 `start_client_gui.py` - GUI启动脚本
- 所有启动脚本在运行时显示免责声明

#### 文档更新
- 新增 `项目说明.md` - 项目使用说明
- 新增 `docs/项目结构变更说明.md` - 详细的变更说明
- 更新 `README.md` - 包含免责声明和新的使用方法
- 所有文档移动到 `docs/` 目录

### 🔄 变更内容

#### 文件位置变更
- `config.py` → `common/config.py`
- `logger.py` → `common/logger.py`
- `drcom_login.py` → `common/drcom_login.py`
- `vpn_server.py` → `server/vpn_server.py`
- `vpn_client.py` → `client/vpn_client.py`
- `vpn_client_gui.py` → `client_gui/vpn_client_gui.py`
- 所有文档 → `docs/` 目录

#### 导入路径更新
```python
# 旧导入
from config import VPN_CONFIG
from logger import Logger
from drcom_login import DrcomLogin

# 新导入
from common.config import VPN_CONFIG
from common.logger import Logger
from common.drcom_login import DrcomLogin
```

#### 使用方法更新
```bash
# 旧方法
python vpn_server.py user pass 8888
python vpn_client.py user pass 172.21.77.34 8888

# 新方法（推荐）
python start_server.py user pass 8888
python start_client.py user pass 172.21.77.34 8888
python start_client_gui.py

# 或使用模块方式
python -m server.vpn_server user pass 8888
python -m client.vpn_client user pass 172.21.77.34 8888
python -m client_gui.vpn_client_gui
```

### 📚 文档改进

- ✅ README.md 添加免责声明章节
- ✅ 更新项目结构说明
- ✅ 更新安装和使用指南
- ✅ 创建详细的变更说明文档
- ✅ 所有文档集中到 docs/ 目录

### 🛡️ 法律合规

- ✅ 所有代码文件添加免责声明
- ✅ 启动时强制显示免责声明
- ✅ 文档中多处强调仅供学习使用
- ✅ 明确声明开发者不承担法律责任

### 🔧 技术改进

- ✅ 模块化设计，代码结构更清晰
- ✅ 统一的包管理（`__init__.py`）
- ✅ 便捷的启动脚本
- ✅ 更好的代码组织

### ⚠️ 破坏性变更

- 旧的直接运行方式已弃用（需使用新的启动脚本）
- 导入路径已变更（需更新自定义脚本）
- 配置文件位置已变更（自动兼容）

### 📦 依赖变更

无依赖变更，`requirements.txt` 保持不变。

---

## [v1.0.0] - 2025-11-06

### ✨ 初始发布

#### 核心功能
- ✅ Dr.COM自动登录
- ✅ VPN服务端实现
- ✅ VPN客户端（命令行版）
- ✅ VPN客户端（GUI版）
- ✅ 智能重试机制
- ✅ 详细日志系统
- ✅ 心跳保活机制

#### 文档
- ✅ README.md
- ✅ 快速开始.md
- ✅ 使用示例.md
- ✅ 开发说明.md
- ✅ 验证逻辑分析.md
- ✅ 项目总结.md

#### 特性
- ✅ 多平台支持（Windows/Linux/macOS）
- ✅ OpenWrt兼容
- ✅ GUI多平台支持（Flet）
- ✅ 完善的异常处理
- ✅ 自动重连机制

---

## 版本说明

### 版本号格式
遵循语义化版本规范：`主版本号.次版本号.修订号`

- **主版本号**：不兼容的API修改
- **次版本号**：向下兼容的功能性新增
- **修订号**：向下兼容的问题修正

### 变更类型

- **新增** - 新功能添加
- **变更** - 现有功能修改
- **弃用** - 即将移除的功能
- **移除** - 已删除的功能
- **修复** - Bug修复
- **安全** - 安全相关修复

---

**项目**: Dr.COM VPN 网络共享系统  
**许可**: MIT License  
**语言**: Python 3.7+

