#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
宝塔面板付费插件下载脚本
作者: MissChina
说明: 在已授权的宝塔面板服务器上运行此脚本，下载所有专业版/企业版付费插件
使用: python3 download_plugins.py
"""

import os
import sys
import json
import time
import requests

# 添加宝塔面板路径
panel_path = '/www/server/panel'
sys.path.insert(0, panel_path + '/class')

# API配置
API_ROOT = 'https://api.bt.cn'
API_GET_LIST = API_ROOT + '/panel/get_plugin_list'
API_DOWNLOAD = API_ROOT + '/down/download_plugin'

# 下载保存目录
SAVE_DIR = '/www/server/panel/temp/plugins_backup'

def get_user_info():
    """获取用户信息"""
    user_file = panel_path + '/data/userInfo.json'
    userInfo = {}

    # 获取OEM名称
    oem_file = panel_path + '/data/o.pl'
    if os.path.exists(oem_file):
        with open(oem_file, 'r') as f:
            userInfo['oem'] = f.read().strip()
    else:
        userInfo['oem'] = 'bt'
    userInfo['o'] = userInfo['oem']

    # 获取MAC地址
    try:
        import uuid
        mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
        userInfo['mac'] = ':'.join([mac[i:i+2] for i in range(0, 12, 2)])
    except:
        userInfo['mac'] = '00:00:00:00:00:00'

    # 读取用户信息文件
    try:
        with open(user_file, 'r') as f:
            userTmp = json.load(f)
        userInfo['uid'] = userTmp.get('uid', -1)
        userInfo['address'] = userTmp.get('address', '')
        userInfo['access_key'] = userTmp.get('access_key', '')
        userInfo['username'] = userTmp.get('username', '')
        userInfo['serverid'] = userTmp.get('serverid', '')
    except Exception as e:
        print(f"[错误] 无法读取用户信息: {e}")
        print("[提示] 请确保此脚本在已登录宝塔账号的面板服务器上运行")
        return None

    return userInfo

def get_plugin_list(userInfo):
    """获取插件列表"""
    print("\n[1/3] 正在获取插件列表...")

    data = userInfo.copy()
    data['panel_version'] = '9.3.0'  # 面板版本

    headers = {
        'User-Agent': 'BT-Panel',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    try:
        response = requests.post(API_GET_LIST, data=data, headers=headers, timeout=30)
        result = response.json()

        if 'list' not in result:
            print(f"[错误] 获取插件列表失败: {result}")
            return None

        return result
    except Exception as e:
        print(f"[错误] 请求失败: {e}")
        return None

def filter_paid_plugins(plugin_list):
    """筛选付费插件(专业版type=8和企业版type=12)"""
    paid_plugins = []

    for plugin in plugin_list.get('list', []):
        plugin_type = plugin.get('type', 0)
        # type=8 专业版, type=12 企业版
        if plugin_type in [8, 12]:
            name = plugin.get('name', '')
            title = plugin.get('title', '')
            versions = plugin.get('versions', [])
            price = plugin.get('price', 0)

            # 获取默认版本
            default_version = ''
            if versions:
                for ver in versions:
                    if isinstance(ver, dict):
                        default_version = ver.get('m_version', ver.get('version', ''))
                        break

            paid_plugins.append({
                'name': name,
                'title': title,
                'type': plugin_type,
                'type_name': '专业版' if plugin_type == 8 else '企业版',
                'version': default_version,
                'price': price,
                'versions': versions
            })

    return paid_plugins

def download_plugin(userInfo, plugin_name, plugin_version):
    """下载单个插件"""
    data = userInfo.copy()
    data['name'] = plugin_name
    data['version'] = plugin_version
    data['os'] = 'Linux'

    headers = {
        'User-Agent': 'BT-Panel'
    }

    try:
        response = requests.post(API_DOWNLOAD, data=data, headers=headers, timeout=300, stream=True)

        # 检查是否返回JSON错误
        content_type = response.headers.get('Content-Type', '')
        if 'application/json' in content_type:
            error = response.json()
            return None, f"服务器返回错误: {error.get('msg', error)}"

        # 获取文件大小
        file_size = int(response.headers.get('File-size', response.headers.get('Content-Length', 0)))

        if file_size == 0:
            return None, "无法获取文件大小，可能未授权"

        # 保存文件
        filename = os.path.join(SAVE_DIR, f"{plugin_name}.zip")
        downloaded = 0

        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)

        return filename, None

    except Exception as e:
        return None, str(e)

def main():
    print("=" * 60)
    print("宝塔面板付费插件下载工具")
    print("作者: MissChina")
    print("=" * 60)

    # 创建保存目录
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    # 获取用户信息
    userInfo = get_user_info()
    if not userInfo:
        return

    print(f"[信息] 用户名: {userInfo.get('username', 'N/A')}")
    print(f"[信息] 用户ID: {userInfo.get('uid', 'N/A')}")
    print(f"[信息] 服务器ID: {userInfo.get('serverid', 'N/A')[:16]}...")

    # 获取插件列表
    plugin_result = get_plugin_list(userInfo)
    if not plugin_result:
        return

    # 筛选付费插件
    paid_plugins = filter_paid_plugins(plugin_result)

    print(f"\n[2/3] 找到 {len(paid_plugins)} 个付费插件:")
    print("-" * 60)

    # 保存插件列表
    list_file = os.path.join(SAVE_DIR, 'plugin_list.json')
    with open(list_file, 'w', encoding='utf-8') as f:
        json.dump(paid_plugins, f, ensure_ascii=False, indent=2)
    print(f"[信息] 插件列表已保存到: {list_file}")

    # 显示插件列表
    for i, p in enumerate(paid_plugins, 1):
        print(f"  {i:2d}. [{p['type_name']}] {p['title']} ({p['name']}) v{p['version']} - ¥{p['price']}")

    print("-" * 60)

    # 下载所有插件
    print(f"\n[3/3] 开始下载插件...")

    success_count = 0
    fail_count = 0

    for i, plugin in enumerate(paid_plugins, 1):
        name = plugin['name']
        version = plugin['version']
        title = plugin['title']

        print(f"\n[{i}/{len(paid_plugins)}] 下载 {title} ({name}) v{version}...", end=' ')

        filename, error = download_plugin(userInfo, name, version)

        if filename:
            file_size = os.path.getsize(filename)
            print(f"成功 ({file_size/1024:.1f}KB)")
            success_count += 1
        else:
            print(f"失败: {error}")
            fail_count += 1

        # 避免请求过快
        time.sleep(1)

    # 总结
    print("\n" + "=" * 60)
    print(f"下载完成! 成功: {success_count}, 失败: {fail_count}")
    print(f"保存目录: {SAVE_DIR}")
    print("=" * 60)

    # 创建打包脚本
    pack_script = os.path.join(SAVE_DIR, 'pack.sh')
    with open(pack_script, 'w') as f:
        f.write(f'''#!/bin/bash
cd {SAVE_DIR}
tar -czvf plugins_backup_$(date +%Y%m%d_%H%M%S).tar.gz *.zip plugin_list.json
echo "打包完成!"
''')
    os.chmod(pack_script, 0o755)
    print(f"\n[提示] 运行 {pack_script} 可以打包所有插件")

if __name__ == '__main__':
    main()
