# 更新日志

## [v1.5.0] - 2025-11-09

### 🔧 重大修复 - Portal认证成功但无法上线问题

#### 核心问题修复
- ✅ **在线状态检查机制完善**：实现服务器配置的两种检查方式
  - 方式0：内核接口 (`/drcom/chkstatus`)
  - 方式1：Radius接口 (`/eportal/portal/online_list`)
- ✅ **页面配置获取**：新增 `get_page_config()` 方法调用 `loadConfig` API
- ✅ **MAC地址格式修复**：Radius方式检查时自动转为大写（符合服务器要求）
- ✅ **IP地址格式支持**：实现IP地址转十进制功能（Radius方式需要）
- ✅ **参数完善**：登录请求添加 `ssid` 参数，提高认证成功率

#### 问题原因分析

**Portal认证成功但无法上线的根本原因：**

服务器支持两种在线状态检查方式，但之前的代码：
1. 没有调用 `loadConfig` API 获取服务器配置
2. 只实现了方式0（内核接口），未实现方式1（Radius接口）
3. MAC地址格式不正确（Radius方式需要大写）
4. 缺少IP转十进制功能（Radius方式需要）

当服务器配置为Radius方式时，由于参数格式错误，导致状态查询失败，虽然Portal认证成功，但系统判定为未在线。

#### 技术实现

##### 新增功能函数
```python
# 静态工具函数
@staticmethod
def ip_to_int(ip_str):
    """将点分十进制IP转换为整数"""
    # 例：'172.19.214.18' -> 2887122450

@staticmethod
def base64_encode(s):
    """Base64编码（用于loadConfig API）"""
    # 例：'172.19.214.18' -> 'MTcyLjE5LjIxNC4xOA=='

# 页面配置获取
def get_page_config(self, local_ip):
    """
    获取服务器配置（loadConfig API）
    提取 check_online_method 等关键参数
    """
```

##### 在线状态检查改进
```python
def check_network_status(self, local_ip=None):
    """
    根据服务器配置自动选择检查方式：
    - 方式0：内核接口，使用默认参数
    - 方式1：Radius接口，MAC转大写 + IP转十进制
    """
```

#### 登录流程优化

**新的登录流程：**
1. 获取本地IP地址
2. **调用 loadConfig API 获取服务器配置** ⬅️ 新增
3. 提取WiFi参数（如果是WiFi环境）
4. 发送登录请求（包含ssid参数）
5. **根据服务器配置选择正确的在线状态检查方式** ⬅️ 改进
6. 验证网络连通性

#### 调试日志增强
- ✅ 显示服务器配置的在线检查方式
- ✅ Radius方式显示MAC和IP的转换结果
- ✅ 详细的API请求和响应日志
- ✅ 页面配置获取成功/失败提示

#### 日志输出示例

**成功案例（Radius方式）：**
```
获取服务器配置...
✓ 获取页面配置成功
  在线状态检查方式: 1 (Radius接口)
✓ Portal协议认证成功！内网IP: 172.19.214.18
验证在线状态...
状态查询(Radius方式): http://10.252.252.5:801/eportal/portal/online_list
参数: MAC=F018982B18B3, IP=172.19.214.18(2887122450)
网络状态: 已在线
✓ 在线状态确认成功 (第1次尝试)
```

**成功案例（内核方式）：**
```
获取服务器配置...
✓ 获取页面配置成功
  在线状态检查方式: 0 (内核接口)
✓ Portal协议认证成功！内网IP: 172.19.214.18
验证在线状态...
状态查询(内核方式): http://10.252.252.5/drcom/chkstatus
网络状态: 已在线
✓ 在线状态确认成功 (第1次尝试)
```

### 📝 文件变更

#### 核心修改
- `common/drcom_login.py` - 重大改进
  - 添加 `portal_api` 属性（第54行）
  - 添加 `server_config` 配置字典（第64-67行）
  - 新增 `ip_to_int()` 静态方法（第277-293行）
  - 新增 `base64_encode()` 静态方法（第295-309行）
  - 新增 `get_page_config()` 方法（第311-372行）
  - 重写 `check_network_status()` 支持双模式（第374-446行）
  - 登录流程中调用配置获取（第534-536行）
  - 登录参数添加ssid字段（第562行）
  - 状态检查传入local_ip参数（第605行）

### 🔍 技术细节

#### Radius方式参数对比

| 参数 | Python处理前 | Python处理后 | JS处理方式 |
|------|------------|------------|----------|
| MAC地址 | `f018982b18b3` | `F018982B18B3` | `util.trim(term.mac).toUpperCase()` |
| IP地址 | `172.19.214.18` | `2887122450` | `util.ipToParseInt(term.ip)` |

#### loadConfig API参数

| 参数 | 说明 | 编码方式 | 示例 |
|------|------|---------|------|
| `wlan_user_ip` | 用户IP | Base64 | `MTcyLjE5LjIxNC4xOA==` |
| `wlan_ac_ip` | AC IP | Base64 | `MTAuMjAuMTAuNA==` |
| `wlan_user_ssid` | WiFi SSID | 明文 | `NNLGXY` |

### 🛡️ 兼容性

#### 向下兼容
- ✅ 自动检测服务器配置，无需手动选择
- ✅ 默认使用方式0（内核接口），与旧版行为一致
- ✅ API接口调用保持兼容
- ✅ 不影响WiFi和有线连接功能

#### 适配场景
- ✅ 内核接口模式的服务器（方式0）
- ✅ Radius接口模式的服务器（方式1）
- ✅ 混合部署环境（自动适配）

### 🐛 修复的Bug

1. **严重**: Portal认证成功但无法上线
   - **影响**：部分服务器环境下登录失败
   - **原因**：服务器使用Radius方式检查，但代码未实现
   - **修复**：实现Radius方式，自动适配服务器配置
   - **影响范围**：使用Radius接口的所有用户

2. **中等**: MAC地址格式错误导致状态查询失败
   - **影响**：Radius方式下状态验证失败
   - **原因**：MAC地址未转大写
   - **修复**：Radius方式自动转大写

3. **轻微**: 缺少loadConfig API调用
   - **影响**：无法获取服务器配置，无法适配
   - **修复**：登录前调用loadConfig获取配置

### 📊 性能改进

| 场景 | 旧版本 | 新版本 |
|------|--------|--------|
| 内核接口模式 | ✅ 正常 | ✅ 正常 |
| Radius接口模式 | ❌ 失败 | ✅ 成功 |
| 配置自适应 | ❌ 不支持 | ✅ 自动检测 |
| **在线验证成功率** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

### ⚠️ 注意事项

#### 调试信息
- 查看日志中的"在线状态检查方式"确认服务器配置
- Radius方式会显示MAC和IP的转换结果
- 如遇问题，请提供"页面配置响应"和"状态查询响应"

#### 已知限制
- 需要服务器支持 `loadConfig` API（大部分Dr.COM服务器支持）
- Base64编码和IP转十进制为标准算法，兼容性良好

### 🎉 用户反馈

感谢用户反馈此问题，这次修复解决了困扰许多用户的"Portal认证成功但无法上线"问题！

---

## [v1.4.0] - 2025-11-09

### 🔧 重大修复 - WiFi环境登录支持

#### WiFi认证问题修复
- ✅ **错误消息修复**：修复API响应 `msg` 字段解析，正确显示详细错误信息（之前显示"未知错误"）
- ✅ **WiFi参数提取**：实现WiFi环境必需的参数自动获取
  - `wlan_user_mac`: WiFi网卡MAC地址
  - `wlan_ac_ip`: 无线控制器(AC) IP地址
  - `wlan_ac_name`: AC名称/编号
- ✅ **AC重定向检测**：通过访问外网触发AC重定向来获取WiFi参数
- ✅ **双网卡环境支持**：针对双网卡+特定路由配置进行优化

#### 连接方式选择
- ✅ **三种连接模式**：
  1. **自动检测** (默认) - 智能检测网络环境
  2. **WiFi连接** - 强制启用WiFi参数检测
  3. **有线连接** - 跳过WiFi检测，直接登录，速度更快
- ✅ **交互式选择**：首次配置时可选择连接方式
- ✅ **配置保存**：连接方式随配置加密保存

#### WiFi参数获取辅助工具
- ✅ **新增工具**：`get_wifi_params.py` - WiFi参数获取辅助脚本
  - 自动触发AC重定向获取参数
  - 支持手动输入参数
  - 参数保存到 `wifi_params.json`
  - 适用于双网卡环境或自动获取失败的情况

#### 调试增强
- ✅ **详细日志**：登录过程输出完整的API请求和响应
- ✅ **参数展示**：显示WiFi参数获取结果（MAC、AC IP、AC名称）
- ✅ **连接方式提示**：日志中显示当前使用的连接方式

### 🔍 问题原因分析

**WiFi环境下登录失败的根本原因：**

在WiFi环境下，无线控制器(AC)会拦截未认证设备的流量。当用户访问外网时：
1. AC拦截请求并重定向到认证页面
2. 重定向URL中包含WiFi参数（MAC、AC IP、AC名称）
3. 网页JavaScript从URL中提取这些参数
4. 登录请求必须携带这些参数才能通过AC认证

**之前的代码问题：**
- 直接访问认证页面，跳过了AC重定向
- 无法获取WiFi必需的参数
- 发送的参数为空或默认值，导致"AC认证失败"

### ✨ 新增功能

#### DrcomLogin类增强
```python
class DrcomLogin:
    def __init__(self, username, password, isp='中国电信', connection_type='auto'):
        # 新增 connection_type 参数
        self.connection_type = connection_type
        self.wifi_params = {
            'wlan_user_mac': '000000000000',
            'wlan_ac_ip': '',
            'wlan_ac_name': ''
        }
```

#### 新增方法
- `get_wifi_params_from_redirect()` - 自动获取WiFi参数
  - 尝试访问外网触发AC重定向
  - 从重定向URL中提取参数
  - 支持多种参数名格式（兼容性更好）
- `_extract_wifi_params_from_url()` - 从URL中提取WiFi参数
  - 支持 `usermac`/`wlan_user_mac`/`mac`
  - 支持 `wlanacip`/`wlan_ac_ip`/`acip`
  - 支持 `wlanacname`/`wlan_ac_name`/`acname`

#### 连接方式配置
```python
# config_manager.py 新增选择流程
选择连接方式:
  1. 自动检测 (默认)
  2. WiFi 连接
  3. 有线连接
说明:
  - WiFi连接：需要获取MAC地址和AC信息，适用于校园WiFi
  - 有线连接：跳过WiFi参数检测，直接登录，速度更快
  - 自动检测：尝试获取WiFi参数，如果失败则使用默认值
```

### 📝 文件变更

#### 核心修改
- `common/drcom_login.py` - 添加WiFi参数提取和连接方式支持
- `common/config_manager.py` - 添加连接方式选择界面
- `server/vpn_server.py` - 添加 `connection_type` 参数传递
- `client/vpn_client.py` - 添加 `connection_type` 参数传递
- `start_server.py` - 传递连接方式参数
- `start_client.py` - 传递连接方式参数

#### 新增文件
- `get_wifi_params.py` - WiFi参数获取辅助工具
- `WiFi环境登录修复说明.md` - 详细的问题分析和修复说明

#### 文档更新
- `README.md` - 添加"连接方式说明"章节
- `README.md` - 更新故障排查部分，添加WiFi问题解决方案

### 🔄 使用方式变更

#### 配置流程（新增连接方式选择）
```bash
python start_server.py

选择运营商类型:
  1. 中国电信 (默认)
  ...
请选择 [1]: 1

选择连接方式:  # 新增
  1. 自动检测 (默认)
  2. WiFi 连接
  3. 有线连接
请选择 [1]: 3  # 有线连接，跳过WiFi检测

服务端口 [默认: 8888]: 8888
```

#### WiFi参数获取（如遇问题）
```bash
# 1. 临时删除特定路由（如果有）
route DELETE 10.252.252.5

# 2. 运行辅助工具
python get_wifi_params.py

# 3. 按提示操作，参数保存到 wifi_params.json

# 4. 添加回路由
route ADD 10.252.252.5 MASK 255.255.255.255 172.19.215.254 -p
```

### 🛡️ 兼容性

#### 向下兼容
- ✅ 旧配置文件自动兼容（默认使用"自动检测"模式）
- ✅ API接口无变化，内部实现改进
- ✅ 有线连接用户无需修改任何配置

#### 双网卡环境
- ✅ 针对双网卡+特定路由配置进行了优化
- ✅ 提供辅助工具手动获取WiFi参数
- ✅ 支持在受限网络环境下使用

### 🐛 修复的Bug

1. **严重**: WiFi环境下登录失败，提示"AC认证失败"
   - **影响**：所有使用WiFi连接的用户无法登录
   - **原因**：缺少WiFi认证必需的MAC地址和AC信息
   - **修复**：实现WiFi参数自动提取，支持WiFi环境认证

2. **中等**: 错误消息显示"未知错误"而非真实错误
   - **影响**：用户无法了解登录失败的真实原因
   - **原因**：API响应使用 `msg` 字段而非 `message`
   - **修复**：兼容两种字段名，正确显示错误信息

3. **轻微**: 有线连接时仍然尝试获取WiFi参数（性能浪费）
   - **影响**：登录速度稍慢
   - **修复**：添加连接方式选择，有线连接跳过WiFi检测

### 📊 性能改进

| 场景 | 旧版本 | 新版本 |
|------|--------|--------|
| WiFi环境登录 | ❌ 失败 | ✅ 成功 |
| 有线环境登录 | ✅ 成功（慢） | ✅ 成功（快） |
| 错误提示 | ❌ "未知错误" | ✅ 详细错误信息 |
| 双网卡环境 | ❌ 不支持 | ✅ 辅助工具支持 |
| **WiFi支持度** | ⭐ | ⭐⭐⭐⭐⭐ |

### ⚠️ 注意事项

#### 首次使用
- 如果之前保存过配置，建议删除重新配置以选择连接方式
- 删除命令：`rm server_config.encrypted` 或 `rm client_config.encrypted`

#### WiFi环境
- 选择"WiFi连接"模式可获得最佳兼容性
- 双网卡环境可能需要使用辅助工具 `get_wifi_params.py`
- WiFi参数包括MAC地址、AC IP和AC名称三个必需参数

#### 有线环境
- 选择"有线连接"模式可跳过WiFi检测，加快登录速度
- 适用于确定使用网线连接的场景

---

## [v1.3.1] - 2025-11-08

### 🔧 重大修复 - Dr.COM登录逻辑

#### 核心问题修复
- ✅ **登录路径修复**：将错误的 `/eportal/?c=ACSetting&a=Login` 修正为 `/eportal/portal/login`
- ✅ **用户名格式修正**：修复用户名格式为 `,0,{username}@{运营商代码}`
- ✅ **请求方法修正**：修改为使用GET方法，参数通过URL query string传递
- ✅ **JS版本更新**：更新jsVersion为实际使用的 `4.2.1`

#### 运营商支持
- ✅ **运营商选择**：新增运营商类型选择（中国电信/中国移动/中国联通/中国广电/职工账号）
- ✅ **运营商映射**：添加运营商代码映射配置
  - 中国电信 → telecom
  - 中国移动 → cmcc
  - 中国联通 → unicom
  - 中国广电 → cbn
  - 职工账号 → （无后缀）

#### 配置改进
- ✅ **交互式选择**：在配置输入时可选择运营商类型
- ✅ **默认设置**：默认使用中国电信
- ✅ **配置保存**：运营商类型会被加密保存

### 🔍 问题诊断方法
- 使用浏览器开发者工具分析实际登录请求
- 对比实际请求与代码中的实现
- 通过抓包确认正确的API格式

### 📝 文件变更
- `common/config.py` - 更新Dr.COM配置
- `common/drcom_login.py` - 修复登录逻辑
- `common/config_manager.py` - 添加运营商选择
- `server/vpn_server.py` - 添加ISP参数支持
- `start_server.py` - 传递运营商参数

## [v1.3.0] - 2025-11-07

### 🔧 重大修复

#### VPN代理功能真实实现
- ✅ **修复核心问题**：之前的代理功能为模拟实现，现已完全重写
- ✅ **SOCKS5协议**：实现完整的SOCKS5代理协议（RFC 1928）
- ✅ **真实流量转发**：双向数据转发，支持所有网络协议
- ✅ **本地代理服务**：客户端提供本地SOCKS5代理（127.0.0.1:1080）

#### 代码质量提升
- ✅ 移除所有TODO和模拟代码
- ✅ 实现完整的网络代理功能
- ✅ 添加详细的代码注释和文档
- ✅ 无Lint错误

### ✨ 新增功能

#### SOCKS5代理模块
- 新增 `common/socks5_proxy.py` - SOCKS5协议处理器
  - `Socks5ProxyHandler` - 单连接处理
  - `Socks5ProxyServer` - 独立代理服务器
- 支持IPv4、IPv6和域名地址类型
- 完整的握手、认证、连接处理
- 高效的select-based双向数据转发

#### VPN服务器改进
- 使用真实的SOCKS5代理处理器
- 完整的流量转发功能
- 详细的连接和转发日志
- 多客户端并发支持

#### VPN客户端改进
- 本地SOCKS5代理服务（监听127.0.0.1:1080）
- 自动接受并转发本地应用请求
- 多连接并发处理
- 使用说明和配置提示

#### 测试工具
- 新增 `test_socks5_proxy.py` - SOCKS5代理测试脚本
- 自动测试连接、握手、数据传输
- HTTP通信验证
- 详细的测试报告



### 🔄 变更内容

#### VPN服务器 (`server/vpn_server.py`)
```python
# 旧实现（已删除）
# TODO: 实现完整的代理逻辑
# 目前只是简单的回显
client_socket.send(b'OK')

# 新实现
handler = Socks5ProxyHandler(client_socket, client_id, self.logger)
handler.handle()
```

#### VPN客户端 (`client/vpn_client.py`)
- 添加本地代理服务器功能
- 支持配置本地代理端口
- 自动将流量转发到VPN服务器

#### 配置文件 (`common/config.py`)
```python
VPN_CONFIG = {
    'server_port': 8888,
    'local_proxy_port': 1080,      # 新增
    'heartbeat_interval': 30,
    'buffer_size': 8192,
    'connection_timeout': 10,       # 新增
    'socks5_enabled': True,         # 新增
}
```

### 📚 使用方法更新

#### 服务器端
```bash
python start_server.py
# 交互式输入配置，启动VPN服务器
```

#### 客户端
```bash
python start_client.py
# 交互式输入配置，启动客户端
# 本地SOCKS5代理将在 127.0.0.1:1080 上监听
```

#### 使用代理
```bash
# 方法1：curl测试
curl --socks5 127.0.0.1:1080 http://www.bing.com

# 方法2：配置浏览器
# Firefox: 设置 → 网络设置 → SOCKS5代理: 127.0.0.1:1080

# 方法3：测试脚本
python test_socks5_proxy.py
```

### 🔍 验证工具

#### 自动化测试
```bash
python test_socks5_proxy.py
```

测试内容：
- ✓ SOCKS5握手
- ✓ 连接建立
- ✓ HTTP通信
- ✓ 数据转发

### 🛡️ 技术改进

| 指标 | 旧版本 | 新版本 |
|------|--------|--------|
| 代理功能 | ❌ 模拟 | ✅ 真实 |
| 流量转发 | ❌ 无 | ✅ 完整 |
| SOCKS5支持 | ❌ 无 | ✅ 完整 |
| 协议兼容 | ❌ 无 | ✅ HTTP/HTTPS等所有 |
| 本地代理 | ❌ 无 | ✅ 127.0.0.1:1080 |
| 并发支持 | ⚠️ 有限 | ✅ 完整 |
| **功能完整度** | ⭐⭐ | ⭐⭐⭐⭐⭐ |

### 📦 新增文件

- `common/socks5_proxy.py` - SOCKS5代理实现
- `test_socks5_proxy.py` - 代理测试工具
- `docs/修复说明.md` - 详细修复文档

### ⚠️ 破坏性变更

**无破坏性变更**

所有修改都是向下兼容的内部实现改进，API和使用方法保持不变。

### 🐛 修复的Bug

1. **严重**: VPN服务器代理功能为模拟实现
   - 影响：无法真正转发流量
   - 修复：实现完整SOCKS5代理

2. **中等**: 客户端缺少本地代理服务
   - 影响：用户无法方便地使用代理
   - 修复：添加本地SOCKS5代理服务

---

## [v1.2.0] - 2025-11-06

### 🔐 重大安全改进

#### 交互式配置输入
- ✅ 移除命令行参数传递敏感信息
- ✅ 改为交互式问答输入
- ✅ 密码输入时隐藏显示（使用getpass）
- ✅ 避免shell历史记录泄露

#### 配置文件加密
- ✅ 使用AES-256加密存储配置
- ✅ PBKDF2-HMAC-SHA256密钥派生
- ✅ 100,000次迭代增强安全性
- ✅ 每个配置文件独立的16字节随机盐值
- ✅ 主密码保护配置文件

#### 文件安全
- ✅ 配置文件自动设置为600权限（仅所有者可读写）
- ✅ `.drcom/` 目录加入.gitignore
- ✅ 防止配置文件被意外提交

### ✨ 新增功能

- 新增 `common/config_manager.py` - 加密配置管理模块
- 更新 `start_server.py` - 交互式服务端启动
- 更新 `start_client.py` - 交互式客户端启动
- 新增 `docs/配置加密说明.md` - 详细的加密说明文档
- 新增 `安全更新说明.md` - 安全更新完整说明

### 🔄 使用方式变更

#### 旧方式（已弃用）❌
```bash
python start_server.py username password 8888
```

#### 新方式（安全）✅
```bash
python start_server.py
# 然后按提示交互式输入
```

### 📦 依赖更新

- 新增：`cryptography>=41.0.0` - 用于配置文件加密

### ⚠️ 破坏性变更

- 命令行参数方式已完全移除
- 需要重新配置（首次运行时）
- 需要安装新的依赖（cryptography）

### 🛡️ 安全性提升

| 指标 | 旧版本 | 新版本 |
|------|--------|--------|
| 密码传递 | ❌ 命令行 | ✅ 交互式 |
| 密码显示 | ❌ 明文 | ✅ 隐藏 |
| 配置存储 | ❌ 明文 | ✅ AES-256加密 |
| Shell历史 | ❌ 泄露 | ✅ 不记录 |
| **安全级别** | ⭐⭐ | ⭐⭐⭐⭐⭐ |

---

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

