# OpenWrt 部署指南

本指南介绍如何在OpenWrt路由器上部署Dr.COM自动认证工具。

## 前提条件

- OpenWrt路由器（已刷入OpenWrt系统）
- 路由器已连接到校园网
- 路由器有足够的存储空间（至少10MB）
- SSH访问权限

## 安装步骤

### 1. 安装Python环境

通过SSH连接到路由器，然后安装Python：

```bash
# 更新软件包列表
opkg update

# 安装Python 3
opkg install python3 python3-pip

# 安装必要的Python库
pip3 install requests beautifulsoup4 pyyaml
```

### 2. 上传工具到路由器

#### 方法1：使用SCP

在本地电脑上：

```bash
# 打包项目
tar -czf drcom.tar.gz drcom_auth.py common/ config.yaml.example

# 上传到路由器
scp drcom.tar.gz root@192.168.1.1:/root/

# SSH到路由器
ssh root@192.168.1.1

# 解压
cd /root
tar -xzf drcom.tar.gz
rm drcom.tar.gz
```

#### 方法2：使用Git（如果路由器有git）

```bash
# 在路由器上
cd /root
opkg install git git-http
git clone https://github.com/yourusername/drcom.git
cd drcom
```

### 3. 配置工具

```bash
cd /root/drcom

# 复制配置文件
cp config.yaml.example config.yaml

# 编辑配置文件
vi config.yaml

# 填入你的账号信息
# account:
#   username: "your_username"
#   password: "your_password"
```

### 4. 测试认证

```bash
# 测试登录
python3 drcom_auth.py -u 用户名 -p 密码

# 查看状态
python3 drcom_auth.py --status
```

## 自动运行配置

### 方法1：使用Cron定时任务（推荐）

编辑crontab：

```bash
crontab -e
```

添加以下内容：

```cron
# 每5分钟检查一次在线状态，掉线自动重连
*/5 * * * * /usr/bin/python3 /root/drcom/drcom_auth.py --config /root/drcom/config.yaml --auto-reconnect --check-interval 300 >> /tmp/drcom.log 2>&1

# 或者，简单的定时登录（不检查状态，直接登录）
*/10 * * * * /usr/bin/python3 /root/drcom/drcom_auth.py --config /root/drcom/config.yaml >> /tmp/drcom.log 2>&1
```

### 方法2：开机自启动脚本

创建启动脚本：

```bash
vi /etc/init.d/drcom
```

内容如下：

```bash
#!/bin/sh /etc/rc.common

START=99
STOP=10

USE_PROCD=1

start_service() {
    procd_open_instance
    procd_set_param command /usr/bin/python3 /root/drcom/drcom_auth.py \
        --config /root/drcom/config.yaml \
        --auto-reconnect
    procd_set_param respawn
    procd_set_param stdout 1
    procd_set_param stderr 1
    procd_close_instance
}
```

设置权限并启用：

```bash
# 设置执行权限
chmod +x /etc/init.d/drcom

# 启用开机自启
/etc/init.d/drcom enable

# 启动服务
/etc/init.d/drcom start

# 查看状态
/etc/init.d/drcom status

# 停止服务
/etc/init.d/drcom stop
```

## 日志查看

### 查看实时日志

```bash
tail -f /tmp/drcom.log
```

### 查看系统日志

```bash
logread | grep drcom
```

## 故障排查

### 1. Python未安装或版本过低

```bash
# 检查Python版本
python3 --version

# 如果版本低于3.7，需要升级
opkg update
opkg upgrade python3
```

### 2. 依赖包缺失

```bash
# 重新安装依赖
pip3 install --upgrade requests beautifulsoup4 pyyaml
```

### 3. 存储空间不足

```bash
# 查看存储空间
df -h

# 清理缓存
opkg clean
rm -rf /tmp/*
```

### 4. 权限问题

```bash
# 确保脚本有执行权限
chmod +x /root/drcom/drcom_auth.py

# 检查配置文件权限
chmod 600 /root/drcom/config.yaml
```

### 5. 网络问题

```bash
# 检查网络连接
ping 10.252.252.5

# 检查DNS
nslookup baidu.com

# 检查路由
ip route show
```

## 高级配置

### 使用外部USB存储

如果路由器内部存储不足，可以使用USB存储：

```bash
# 挂载USB设备
mkdir -p /mnt/usb
mount /dev/sda1 /mnt/usb

# 移动drcom到USB
mv /root/drcom /mnt/usb/
ln -s /mnt/usb/drcom /root/drcom

# 添加到启动脚本，确保USB先挂载
```

### 日志轮转

创建日志清理脚本：

```bash
vi /root/drcom/clean_log.sh
```

内容：

```bash
#!/bin/sh
# 清理超过7天的日志
find /tmp -name "drcom*.log" -mtime +7 -delete

# 限制当前日志大小
LOG_FILE="/tmp/drcom.log"
if [ -f "$LOG_FILE" ]; then
    SIZE=$(stat -c%s "$LOG_FILE")
    if [ $SIZE -gt 1048576 ]; then  # 1MB
        tail -n 100 "$LOG_FILE" > "${LOG_FILE}.tmp"
        mv "${LOG_FILE}.tmp" "$LOG_FILE"
    fi
fi
```

添加到crontab：

```bash
# 每天凌晨清理日志
0 0 * * * /bin/sh /root/drcom/clean_log.sh
```

## 性能优化

### 减少资源占用

在config.yaml中：

```yaml
reconnect:
  check_interval: 300  # 增加检查间隔到5分钟

logging:
  level: "WARNING"  # 只记录警告和错误
  file: ""  # 不写文件，只输出到系统日志
```

### 使用轻量级定时任务

只在需要时登录，而不是持续监控：

```cron
# 每小时登录一次（简单粗暴）
0 * * * * /usr/bin/python3 /root/drcom/drcom_auth.py --config /root/drcom/config.yaml
```

## 卸载

```bash
# 停止服务
/etc/init.d/drcom stop
/etc/init.d/drcom disable

# 删除文件
rm -rf /root/drcom
rm /etc/init.d/drcom

# 清理crontab
crontab -e
# 删除相关行

# 卸载Python（可选）
# opkg remove python3 python3-pip
```

## 常见使用场景

### 场景1：宿舍路由器

- 路由器WAN口连接校园网
- 开机自动认证
- 掉线自动重连

```bash
# 使用开机脚本 + cron定时检查
/etc/init.d/drcom enable
# crontab: */5 * * * * ...
```

### 场景2：实验室路由器

- 需要稳定的网络连接
- 频繁检查在线状态

```bash
# 短间隔检查（2分钟）
*/2 * * * * /usr/bin/python3 /root/drcom/drcom_auth.py --status || /usr/bin/python3 /root/drcom/drcom_auth.py --config /root/drcom/config.yaml
```

### 场景3：临时使用

- 手动控制登录/下线

```bash
# 登录
python3 drcom_auth.py --config config.yaml

# 下线
python3 drcom_auth.py --logout
```

## 监控和通知

### 使用webhook通知

修改认证脚本，在认证成功/失败时发送webhook：

```bash
# 在crontab中
*/5 * * * * /usr/bin/python3 /root/drcom/drcom_auth.py --config /root/drcom/config.yaml && curl -X POST "https://your-webhook-url?status=success" || curl -X POST "https://your-webhook-url?status=failed"
```

## 注意事项

1. **账号安全**
   - 配置文件包含明文密码，注意权限：`chmod 600 config.yaml`
   - 不要在公共路由器上使用

2. **性能影响**
   - Python运行会占用一定内存（约10-20MB）
   - 建议使用内存≥64MB的路由器

3. **网络稳定性**
   - 认证失败可能导致短暂断网
   - 建议设置合理的检查间隔

4. **学校政策**
   - 遵守学校网络使用规定
   - 不要滥用认证功能

## 支持的OpenWrt版本

- OpenWrt 19.07+
- OpenWrt 21.02+（推荐）
- OpenWrt 22.03+

## 更多帮助

- 查看主文档：[README.md](../README.md)
- 提交问题：[Issues](https://github.com/yourusername/drcom/issues)

