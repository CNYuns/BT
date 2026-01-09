# BT Panel 宝塔面板

**作者：** MissChina
**许可证：** 专有软件

## 简介

BT Panel 是一款 Linux 服务器管理面板。

## 支持系统

| 系统 | 版本 |
|--------|---------|
| CentOS | 7.x, 8.x |
| Ubuntu | 20.04, 22.04 |
| Debian | 10, 11, 12 |
| Rocky Linux | 8.x, 9.x |
| AlmaLinux | 8.x, 9.x |

## 快速安装

```bash
curl -sSL https://raw.githubusercontent.com/CNYuns/BT/main/install.sh | bash
```

## 手动安装

```bash
# 下载对应系统的安装包
wget https://github.com/CNYuns/BT/releases/latest/download/bt-panel-ubuntu22.tar.gz

# 解压安装
tar -xzf bt-panel-ubuntu22.tar.gz -C /
chmod +x /etc/init.d/bt
ln -sf /etc/init.d/bt /usr/bin/bt

# 启动面板
bt start
```

## 常用命令

```bash
bt              # 进入交互式菜单
bt start        # 启动面板
bt stop         # 停止面板
bt restart      # 重启面板
bt reload       # 重载面板
bt status       # 查看状态
bt logs         # 查看错误日志
bt default      # 查看默认账号密码
bt 1            # 重启面板服务
bt 2            # 停止面板服务
bt 3            # 启动面板服务
bt 4            # 重载面板服务
bt 5            # 修改面板密码
bt 6            # 修改面板用户名
bt 7            # 强制修改MySQL密码
bt 8            # 修改面板端口
bt 9            # 清除面板缓存
bt 10           # 清除登录限制
bt 14           # 查看面板默认信息
bt 15           # 清理系统垃圾
bt 16           # 修复面板
bt 22           # 显示面板错误日志
bt 23           # 关闭BasicAuth认证
bt 24           # 关闭动态口令认证
bt 26           # 关闭面板SSL
bt 28           # 修改安全入口
bt 34           # 更新面板
```

## 许可证

本软件为专有软件，详见 [LICENSE](LICENSE)。

---

Copyright (c) 2026-present MissChina. All Rights Reserved.
