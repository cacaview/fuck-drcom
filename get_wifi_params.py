"""
WiFi参数获取工具

用于在双网卡环境下获取WiFi认证所需的参数（MAC地址、AC IP、AC名称）

⚠️ 使用前请先删除特定路由：
   route DELETE 10.252.252.5

运行此脚本后再添加回路由：
   route ADD 10.252.252.5 MASK 255.255.255.255 172.19.215.254 -p
"""

import requests
import re
import sys
import json
from pathlib import Path

print("=" * 60)
print("📡 WiFi参数获取工具")
print("=" * 60)
print()

def get_wifi_params():
    """
    通过访问外网触发AC重定向来获取WiFi参数
    """
    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        print("🔍 尝试访问外网以触发AC重定向...")
        
        # 访问多个可能的测试地址
        test_urls = [
            'http://www.baidu.com',
            'http://www.msftconnecttest.com/connecttest.txt',
            'http://www.google.com',
            'http://1.1.1.1'
        ]
        
        wifi_params = None
        
        for test_url in test_urls:
            try:
                print(f"   尝试访问: {test_url}")
                response = session.get(test_url, allow_redirects=True, timeout=5)
                final_url = response.url
                
                print(f"   重定向后URL: {final_url}")
                
                # 检查是否被重定向到认证页面
                if '10.252.252.5' in final_url or 'dr.com' in final_url.lower():
                    print(f"\n✅ 检测到AC重定向！")
                    print(f"   完整URL: {final_url}\n")
                    
                    # 提取WiFi参数
                    params = {}
                    
                    # MAC地址
                    mac_match = re.search(r'usermac=([0-9a-fA-F\-:]+)', final_url, re.IGNORECASE)
                    if mac_match:
                        mac = mac_match.group(1).replace('-', '').replace(':', '').lower()
                        params['wlan_user_mac'] = mac
                        print(f"   ✓ MAC地址: {mac}")
                    
                    # AC IP
                    ac_ip_match = re.search(r'wlanacip=(\d+\.\d+\.\d+\.\d+)', final_url, re.IGNORECASE)
                    if ac_ip_match:
                        params['wlan_ac_ip'] = ac_ip_match.group(1)
                        print(f"   ✓ AC IP: {ac_ip_match.group(1)}")
                    
                    # AC名称
                    ac_name_match = re.search(r'wlanacname=([^&]+)', final_url, re.IGNORECASE)
                    if ac_name_match:
                        params['wlan_ac_name'] = ac_name_match.group(1)
                        print(f"   ✓ AC名称: {ac_name_match.group(1)}")
                    
                    # 用户IP
                    ip_match = re.search(r'wlanuserip=(\d+\.\d+\.\d+\.\d+)', final_url, re.IGNORECASE)
                    if ip_match:
                        params['wlan_user_ip'] = ip_match.group(1)
                        print(f"   ✓ 用户IP: {ip_match.group(1)}")
                    
                    if params:
                        wifi_params = params
                        break
                    
            except Exception as e:
                print(f"   ✗ 访问失败: {e}")
                continue
        
        if wifi_params:
            print("\n" + "=" * 60)
            print("🎉 成功获取WiFi参数！")
            print("=" * 60)
            
            # 保存到文件
            save_path = Path('wifi_params.json')
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(wifi_params, f, indent=2, ensure_ascii=False)
            
            print(f"\n已保存到文件: {save_path}")
            print("\n参数内容：")
            print(json.dumps(wifi_params, indent=2, ensure_ascii=False))
            
            print("\n" + "=" * 60)
            print("📝 下一步操作：")
            print("=" * 60)
            print("1. 现在可以添加回路由：")
            print("   route ADD 10.252.252.5 MASK 255.255.255.255 172.19.215.254 -p")
            print()
            print("2. WiFi参数已保存，可以在代码中手动使用这些参数")
            print()
            
            return wifi_params
        else:
            print("\n" + "=" * 60)
            print("❌ 未能获取WiFi参数")
            print("=" * 60)
            print("\n可能的原因：")
            print("1. 您可能已经登录了")
            print("2. 特定路由仍然存在（请确认已删除）")
            print("3. 您可能在有线网络环境")
            print()
            print("请尝试：")
            print("1. 确认已删除路由：route DELETE 10.252.252.5")
            print("2. 在浏览器中访问 www.baidu.com 查看是否会跳转")
            print("3. 如果跳转，请复制浏览器地址栏中的完整URL")
            print()
            
            return None
            
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        return None

def manual_input_wifi_params():
    """
    手动输入WiFi参数（从浏览器URL中复制）
    """
    print("\n" + "=" * 60)
    print("✋ 手动输入WiFi参数")
    print("=" * 60)
    print()
    print("请在浏览器中访问任意外网网址（如 www.baidu.com）")
    print("如果被重定向到认证页面，请复制地址栏中的完整URL")
    print()
    
    url = input("请粘贴URL（或按Enter跳过）: ").strip()
    
    if not url:
        return None
    
    # 提取WiFi参数
    params = {}
    
    # MAC地址
    mac_match = re.search(r'usermac=([0-9a-fA-F\-:]+)', url, re.IGNORECASE)
    if mac_match:
        mac = mac_match.group(1).replace('-', '').replace(':', '').lower()
        params['wlan_user_mac'] = mac
    
    # AC IP
    ac_ip_match = re.search(r'wlanacip=(\d+\.\d+\.\d+\.\d+)', url, re.IGNORECASE)
    if ac_ip_match:
        params['wlan_ac_ip'] = ac_ip_match.group(1)
    
    # AC名称
    ac_name_match = re.search(r'wlanacname=([^&]+)', url, re.IGNORECASE)
    if ac_name_match:
        params['wlan_ac_name'] = ac_name_match.group(1)
    
    # 用户IP
    ip_match = re.search(r'wlanuserip=(\d+\.\d+\.\d+\.\d+)', url, re.IGNORECASE)
    if ip_match:
        params['wlan_user_ip'] = ip_match.group(1)
    
    if params:
        print("\n✅ 成功提取WiFi参数：")
        print(json.dumps(params, indent=2, ensure_ascii=False))
        
        # 保存到文件
        save_path = Path('wifi_params.json')
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(params, f, indent=2, ensure_ascii=False)
        
        print(f"\n已保存到文件: {save_path}")
        return params
    else:
        print("\n❌ 无法从URL中提取WiFi参数")
        return None

if __name__ == '__main__':
    print("⚠️  注意：使用此工具前请确保已删除特定路由")
    print("   命令：route DELETE 10.252.252.5")
    print()
    
    choice = input("是否继续？(y/n) [y]: ").strip().lower()
    if choice and choice != 'y':
        print("已取消")
        sys.exit(0)
    
    print()
    
    # 尝试自动获取
    wifi_params = get_wifi_params()
    
    # 如果自动获取失败，提供手动输入选项
    if not wifi_params:
        print()
        choice = input("是否手动输入WiFi参数？(y/n) [y]: ").strip().lower()
        if not choice or choice == 'y':
            wifi_params = manual_input_wifi_params()
    
    if wifi_params:
        print("\n" + "=" * 60)
        print("✅ 任务完成！")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ 未能获取WiFi参数")
        print("=" * 60)

