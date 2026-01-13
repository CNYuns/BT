# BaoTa Panel 项目文档

## 作者: MissChina
## 邮箱: 391475293@qq.com
## 更新日期: 2026-01-13

---

# 第一部分：项目修改要求

**警告：此文档不允许删除！**

---

## 1. 作者信息要求 (重要!)

- **唯一允许的作者名字**：MissChina
- **唯一允许的邮箱**：391475293@qq.com
- **禁止**：任何其他作者名字或邮箱出现在项目中
- **禁止**：Git commit 消息中包含 `Co-Authored-By` 或其他作者信息
- **Git 提交格式**：
```bash
git commit -m "v版本号 - 简短描述"
```

---

## 2. 版本号管理

### 2.1 版本号定义位置 (唯一)

```python
# class/common.py:33
g.version = '11.3.41'
```

### 2.2 获取版本号方法

- `public.version()` - 从 common.py 读取版本号
- `session['version']` - 前端页面使用

### 2.3 版本号使用规范

- **一处修改，处处显示**
- 所有需要显示版本号的地方使用 `public.version()`
- 禁止硬编码版本号字符串

---

## 3. 授权绕过要求

- 所有 `__check_auth()` 等授权检查函数必须修改为**始终返回已授权状态**
- **不允许**创建新文件
- **不允许**删除代码逻辑，仅修改返回值
- **不允许**修改下载URL（除非配置自定义URL）

---

## 4. 授权时间显示要求

- 前端显示的授权时间必须为 **9999年**
- **无需登录宝塔账号**
- 使用时间戳 `253402214400` (对应 9999-12-31)

---

## 5. 其他要求

- 提交代码前必须先确认作者信息
- 不允许执行可能导致数据丢失的危险操作

---

# 第二部分：当前版本状态 (v11.3.59)

## 一、已完成的修改

### 1.1 授权绕过点 (18处)

| # | 文件路径 | 函数/方法 | 修改内容 |
|---|----------|-----------|----------|
| 1 | `class/pluginAuth.py:38-137` | `get_plugin_list()` | 注入永久授权 253402214400 |
| 2 | `class/pluginAuth.py:140-168` | `exec_fun()` | 拦截授权错误返回成功 |
| 3 | `class/pluginAuth.py:170-185` | `get_fun()` | 注入授权时间戳 |
| 4 | `class/panelPlugin.py` | `__download_plugin()` | 支持自定义URL下载 |
| 5 | `class/panelPlugin.py` | `get_soft_find()` | 注入购买状态 |
| 6 | `class/database.py:174` | `__check_auth()` | return True |
| 7 | `class/safeModel/firewallModel.py:1245` | `__check_auth()` | return True |
| 8 | `class/projectModel/java_scanningModel.py:82` | `__check_auth()` | return True |
| 9 | `class/mailModel/mainModel.py:6527` | `__check_auth()` | return True |
| 10 | `script/cron_scaning.py:20` | `__check_auth()` | return True |
| 11 | `script/cron_file.py:20` | `__check_auth()` | return True |
| 12 | `class/plugin_tool.py:98` | `_call_plugin_func()` | 跳过未购买检查 |
| 13 | `BTPanel/__init__.py` | `get_pd()` | 返回永久授权 |
| 14 | `BTPanel/__init__.py` | `panel_other()` | 授权错误时渲染插件模板 |
| 15 | `class/ajax.py` | `get_pd()` | 返回永久授权 |
| 16 | `class/ajax.py` | `UpdatePanel()` | 使用 public.version() |
| 17 | `class/panelModel/publicModel.py:162` | `get_pd()` | 返回永久授权 |
| 18 | `mod/base/public_aap/common.py:4295` | `get_pd()` | 返回永久授权 |
| 19 | `plugin/btwaf/static/js/btwaf.js:657` | 恶意情报库检查 | 注释授权检查代码 |

### 1.2 版本号统一管理

| 文件 | 修改 |
|------|------|
| `class/common.py:33` | 版本号定义: `g.version = '11.3.53'` |
| `class/ajax.py:918` | 使用 `public.version()` 替代硬编码 |

### 1.3 WAF安装页面修复

| 问题 | 解决方案 |
|------|----------|
| 安装按钮无响应 | 直接调用 `/plugin?action=install_plugin` API |
| 授权列表错误未拦截 | 扩展授权错误关键词列表 |

---

## 二、授权错误拦截关键词

以下错误信息会被拦截并返回成功：

```python
auth_errors = [
    '未授权', '未购买', '授权列表', '无法获取',
    '已到期', '过期', 'unauthorized', 'license', 'expired'
]
```

**位置**: `BTPanel/__init__.py:2366`

---

## 三、自定义插件下载URL

### 3.1 配置位置

`class/panelPlugin.py` 类变量:

```python
__custom_plugin_url_prefix = 'https://github.com/CNYuns/files/releases/download/v1.0.0'
__custom_plugin_list = [
    'bt_ssh_auth', 'btwaf', 'btwaf_httpd', 'load_balance', 'masterslave',
    'monitor', 'msg_push', 'mysql_replicate', 'nfs_tools', 'ossfs',
    'rsync', 'syssafe', 'tamper_core', 'tamper_proof_refactored',
    'task_manager', 'total', 'wp_toolkit'
]
```

### 3.2 下载逻辑

1. 检查插件是否在 `__custom_plugin_list` 中
2. 是 → 从自定义URL下载 (跳过官方服务器)
3. 否 → 从 bt.cn 官方服务器下载

---

## 四、关键代码位置

### 4.1 BTPanel/__init__.py

```python
# 第2366-2382行: 授权错误拦截
auth_errors = ['未授权', '未购买', '授权列表', '无法获取', '已到期', '过期', 'unauthorized', 'license', 'expired']
is_auth_error = any(err in msg.lower() if err.islower() else err in msg for err in auth_errors)
if is_auth_error:
    if name == 'btwaf':
        return render_template('error3.html', data={})  # WAF返回安装页
    data = {'status': True, 'msg': ''}  # 其他插件返回成功
```

### 4.2 class/pluginAuth.py

```python
# exec_fun() 中的授权错误拦截
auth_keywords = ['未授权', '未购买', '授权', 'unauthorized', 'license', '过期', 'expired', '无法获取', '授权列表', '加载失败']
if any(keyword.lower() in msg_lower for keyword in auth_keywords):
    return {'status': True, 'msg': ''}
```

### 4.3 BTPanel/templates/default/error3.html

```javascript
// WAF安装按钮 - 直接调用API
$('.daily-product-buy').on('click', '.installWaf', function(){
    bt_tools.send({url:'/plugin?action=install_plugin', data:{
        sName: 'btwaf',
        version: m_version,
        min_version: min_version,
        type: 0
    }}, function(res){ ... });
});
```

---

## 五、安装脚本

### 5.1 位置

`install.sh` - 一键安装脚本

### 5.2 pyenv下载源

```bash
# Ubuntu系统使用GitHub镜像
PYENV_URL="https://github.com/MissChina/file/releases/download/1.0/pyenv-ubuntu22-x64.tar.gz"
```

### 5.3 GitHub Release 自动构建

`.github/workflows/release.yml` - 推送 v* 标签时自动构建7个系统版本

---

## 六、2026-01-09 更新记录

### 6.1 修复WAF授权列表错误

**问题**: `"加载失败: 无法获取授权列表"` 错误未被正确拦截

**解决**: 扩展 `panel_other()` 中的授权错误检测关键词

### 6.2 统一版本号管理

**修改**:
- `class/common.py:33` - 定义 `g.version = '11.3.50'`
- `class/ajax.py:918` - 使用 `public.version()` 替代硬编码

### 6.3 2026-01-10 更新 - btwaf插件前端授权绕过

**问题**: btwaf插件安装后，点击"恶意情报库"功能弹出购买窗口

**原因**: `plugin/btwaf/static/js/btwaf.js:657-661` 检查 `rdata.endtime < 0`

**解决**: 在检查前强制设置 endtime 为永久授权

```javascript
// 已修改: 强制设置为已授权 - MissChina
rdata.endtime = 253402214400;
```

### 6.4 2026-01-10 更新 - btwaf安装后显示两个界面问题

**问题**: btwaf插件安装成功后，刷新页面仍显示安装页面而非WAF界面

**原因**: `panel_other()` 函数在捕获授权错误时返回 `error3.html`（安装页），即使插件已安装

**解决**: 修改 `BTPanel/__init__.py` 中4处返回 error3.html 的位置，改为检测插件模板是否存在，存在则直接渲染插件模板

```python
# 已修改: 插件已安装时直接渲染插件模板
if name == 'btwaf' and fun == 'index':
    t_path = p_path + '/templates/index.html'
    if os.path.exists(t_path):
        g.btwaf_version = '1.0'
        t_body = public.readFile(t_path)
        return render_template_string(t_body, data={'js_random': get_js_random()})
    return render_template('error3.html', data={})
```

**修改位置**:
1. `BTPanel/__init__.py:2369-2377` - panel_other() 中 is_auth_error 判断
2. `BTPanel/__init__.py:2387-2394` - panel_other() 异常处理
3. `BTPanel/__init__.py:2424-2434` - panel_other() dict类型返回值处理
4. `BTPanel/__init__.py:3588-3598` - panel_mod() dict类型返回值处理

---

## 七、技术实现原理

### 7.1 授权时间戳

`253402214400` = 9999-12-31 00:00:00 UTC

### 7.2 授权绕过机制

1. **前端显示**: `get_pd()` 返回永久授权HTML
2. **后端验证**: `exec_fun()` 拦截授权错误消息
3. **列表注入**: `get_plugin_list()` 为所有插件注入授权时间
4. **WAF安装**: 直接调用 API 而非 postMessage

### 7.3 版本号获取流程

```
public.version()
    ↓
读取 class/common.py 文件内容
    ↓
正则匹配 g.version = 'x.x.x'
    ↓
返回版本号字符串
```

---

## 八、注意事项

1. **Git 提交**: 只允许 MissChina 作者，禁止 Co-Authored-By
2. **版本号**: 只在 `class/common.py:33` 修改
3. **插件下载**: 本地授权绕过不影响 bt.cn 服务器验证
4. **测试**: 每次修改后需在实际服务器测试

### 6.5 2026-01-10 更新 - btwaf安装错误处理改进

**问题**: btwaf安装显示成功但页面刷新后仍需安装，第二次安装失败

**原因分析**:
1. install.sh执行结果没有被检查，即使失败也返回"安装成功"
2. 下载错误没有详细日志，难以排查GitHub URL问题
3. 安装状态检测没有调试日志

**解决方案**:

1. **改进install_sync函数** (`class/panelPlugin.py:1141-1169`)
   - 执行install.sh并捕获输出
   - 记录安装脚本执行结果到调试日志
   - 验证安装成功后info.json文件是否存在

2. **改进下载错误处理** (`class/panelPlugin.py:1115-1133`)
   - 记录下载开始、响应状态的详细日志
   - 提供更明确的错误消息，指导用户检查GitHub release

3. **添加安装状态检测日志** (`class/panelPlugin.py:2433-2440`)
   - 当检测btwaf时记录详细的路径检查结果

**调试日志位置**: `/log/waf_install_debug.log`

---

## 九、2026-01-13 更新 - v11.3.59

### 9.1 自定义插件下载URL (17个付费插件)

**修改文件**: `class/panelPlugin.py:650-657`

```python
__custom_plugin_url_prefix = 'https://github.com/CNYuns/files/releases/download/v1.0.0'
__custom_plugin_list = [
    'bt_ssh_auth', 'btwaf', 'btwaf_httpd', 'load_balance', 'masterslave',
    'monitor', 'msg_push', 'mysql_replicate', 'nfs_tools', 'ossfs',
    'rsync', 'syssafe', 'tamper_core', 'tamper_proof_refactored',
    'task_manager', 'total', 'wp_toolkit'
]
```

### 9.2 禁用错误上报 (3处)

| 文件 | 行号 | 说明 |
|------|------|------|
| `class/config.py` | 4233-4239 | 禁用 api.bt.cn 错误上报 |
| `class/public.py` | 8397-8403 | 禁用异常报告提交 |
| `class/userlogin.py` | 262-268 | 禁用登录错误上报 |

### 9.3 禁用木马误报上报

**文件**: `class/files.py:4300-4306`

```python
# 云端误报上报已禁用
return public.returnMsg(True, "提交误报完成（云端上报已禁用）")
```

### 9.4 插件目录gitignore

17个付费插件目录已添加到 `.gitignore`，从GitHub Release下载而非提交到主仓库。

---

# 第三部分：SSL证书申请系统

## 一、Let's Encrypt免费证书申请

### 1.1 核心文件

| 文件 | 功能 |
|------|------|
| `class/panelLets.py` | Let's Encrypt ACME v1/v2 客户端 |
| `class/acme_v2.py` | ACME v2 协议完整实现 |
| `class/letsencrypt.py` | Legacy Let's Encrypt 支持 |

### 1.2 DNS验证流程 (`panelLets.py:441-541`)

```
1. 初始化ACME客户端
2. client.acme_register() - 账户注册
3. client.apply_for_cert_issuance() - 获取授权URL
4. client.get_identifier_authorization(url) - 获取DNS令牌
5. dns_class.create_dns_record() - 创建DNS TXT记录
6. self.check_dns() - 验证DNS解析
7. client.check_authorization_status() - 请求CA验证
8. client.send_csr() - 发送证书签名请求
9. client.download_certificate() - 下载证书
```

### 1.3 HTTP文件验证流程 (`panelLets.py:544-635`)

```
1. 初始化ACME客户端
2. client.get_identifier_authorization() - 获取HTTP令牌
3. public.writeFile(wellknown_path, token) - 写入验证文件
   路径: /.well-known/acme-challenge/{token}
4. public.httpGet(wellknown_url) - 验证HTTP访问
5. client.check_authorization_status() - 请求CA验证
6. client.download_certificate() - 下载证书
```

### 1.4 支持的DNS服务商 (`panelLets.py:159-180`)

| 标识 | 服务商 |
|------|--------|
| `dns_ali` | 阿里云DNS |
| `dns_dp` | DNSPod |
| `dns_cx` | CloudXNS |
| `dns_bt` | 宝塔DNS |

### 1.5 证书保存位置 (`panelLets.py:308-321`)

```python
path = '/www/server/panel/vhost/cert/' + siteName

# 保存文件:
privkey.pem      # 私钥
fullchain.pem    # 证书链 (cert + ca_data)
account_key.key  # 续签密钥
fullchain.pfx    # IIS证书 (Windows)
```

---

## 二、商业证书申请 (需BT官方服务器)

### 2.1 核心文件

**文件**: `class/panelSSL.py` (2500+行)

### 2.2 API端点配置 (`panelSSL.py:24-27`)

```python
__APIURL = public.GetConfigValue('home') + '/api/Auth'
__APIURL2 = public.GetConfigValue('home') + '/api/Cert'
__APIURL3 = public.GetConfigValue('home') + '/api/v2'
__API = public.GetConfigValue('home') + '/api'
```

### 2.3 关键接口

| 函数 | 行号 | 功能 |
|------|------|------|
| `ApplyDVSSL()` | 727 | 申请DV证书 |
| `apply_order_ca()` | 888 | 提交到CA签发 |
| `apply_order()` | 318 | 提交订单 |
| `get_verify_info()` | 327 | 获取验证方式 |
| `get_verify_result()` | 478 | 检查验证结果 |
| `download_cert()` | 224 | 下载证书 |
| `set_cert()` | 234 | 部署证书到网站 |

### 2.4 数据加密方式 (`panelSSL.py:1593-1618`)

```python
def De_Code(self, data):  # 加密发送
    pdata = urllib.parse.urlencode(data)
    return binascii.hexlify(pdata).decode()

def En_Code(self, data):  # 解密接收
    tmp = binascii.unhexlify(data)
    result = urllib.parse.unquote(tmp.decode('utf-8'))
    return json.loads(result)
```

---

## 三、证书自动续签

### 3.1 续签任务 (`panelSSL.py:656-706`)

```python
# 创建定时任务
args.sBody = "{panelpath}/pyenv/bin/python3 -u {panelpath}/script/renew_certificate.py"

# 任务在凌晨0-4点随机运行
run_hour = random.randint(0, 4)
run_minute = random.randint(0, 59)
```

### 3.2 Let's Encrypt续签 (`panelLets.py:183-217`)

```python
def renew_lest_cert(self, data):
    path = self.setupPath + '/panel/vhost/cert/' + data['siteName']
    account_key = public.readFile(path + "/account_key.key")

    # 使用存储的account_key续签
    certificate = self.crate_let_by_dns(data)

    # 更新证书文件
    public.writeFile(path + "/privkey.pem", certificate['key'])
```

---

## 四、ACME服务器地址

```python
# 正式环境
https://acme-v02.api.letsencrypt.org/directory

# 测试环境
https://acme-staging-v02.api.letsencrypt.org/directory
```

---

## 五、SSL相关API路由 (`BTPanel/__init__.py`)

### 5.1 免身份验证操作

```python
'download_cert'
```

### 5.2 需要宝塔账号的操作

```python
'check_auth_status', 'download_cert', 'apply_cert', 'renew_cert',
'apply_cert_api', 'apply_dns_auth', 'get_order_list',
'get_order_detail', 'validate_domain', 'delete_order',
'download_cert_to_local', 'SetCertToSite'
```

### 5.3 商业证书操作 (行1413-1420)

```python
'SyncOrder', 'download_cert', 'set_cert', 'cancel_cert_order',
'ApplyDVSSL', 'apply_cert_order_pay', 'get_order_list',
'apply_cert_install_pay', 'check_ssl_method'
```

---

## 六、SSL授权绕过建议

### 6.1 Let's Encrypt (免费) - 无需绕过

Let's Encrypt证书申请直接与 `acme-v02.api.letsencrypt.org` 交互，不经过BT官方服务器，无需授权绕过。

### 6.2 商业证书 - 需绕过BT官方API

商业证书的所有操作都需要与 `api.bt.cn` 交互：

| 操作 | 绕过方案 |
|------|----------|
| 申请DV证书 | 需本地模拟 `ApplyDVSSL()` 返回 |
| 下载证书 | 需从替代源下载或本地证书 |
| 验证结果 | 需本地模拟验证成功状态 |

### 6.3 推荐方案

1. **使用Let's Encrypt免费证书** - 完全本地处理，无需绕过
2. **自建ACME服务器** - 替换 `__APIURL` 指向自建服务
3. **本地证书导入** - 使用 `set_cert()` 直接导入已有证书

---

## 七、SSL授权绕过实现 (v11.3.60)

### 7.1 panelSSL.py 修改 (3处)

**1. request() 函数 (行2434-2497)**

```python
def request(self,dname):
    # === 本地绕过逻辑 ===
    bypass_result = self.__bypass_bt_api(dname)
    if bypass_result is not None:
        return bypass_result
    # === 原有逻辑 ===
    ...

def __bypass_bt_api(self, dname):
    # 获取产品列表 - 返回空列表
    if dname.startswith('get_product_list'):
        return {'status': True, 'msg': '请使用Let\'s Encrypt免费证书', 'data': []}

    # 获取订单列表 - 返回空列表
    if dname == 'get_bt_ssl_list':
        return []

    # 商业证书操作 - 返回禁用提示
    bypass_actions = ['apply_cert_order', 'apply_cert', 'download_cert', ...]
    if dname in bypass_actions:
        return {'status': False, 'msg': '商业证书功能已禁用，请使用Let\'s Encrypt免费证书'}
```

**2. request_v2() 函数 (行2499-2541)**

```python
def request_v2(self,dname):
    bypass_result = self.__bypass_bt_api_v2(dname)
    if bypass_result is not None:
        return bypass_result
    ...

def __bypass_bt_api_v2(self, dname):
    if 'cert_ssl' in dname:
        return {'status': False, 'msg': '商业证书功能已禁用'}
```

**3. request_post() 函数 (行2547-2556)**

```python
def request_post(self,url,params):
    if 'bt.cn' in url or 'api.bt' in url:
        if '/Auth/' in url or '/Cert/' in url:
            return {'status': False, 'msg': '商业证书功能已禁用'}
```

### 7.2 ssl_manage.py 修改 (3处)

| 函数 | 行号 | 修改内容 |
|------|------|----------|
| `_refresh_ssl_info_by_cloud()` | 426-429 | 直接return，跳过云端同步 |
| `remove_cert()` | 616-631 | 移除云端删除API调用 |
| `upload_cert()` | 633-639 | 返回禁用提示，跳过云端上传 |

### 7.3 绕过效果

| 功能 | 状态 | 说明 |
|------|------|------|
| Let's Encrypt免费证书 | ✅ 正常 | 直接与letsencrypt.org交互 |
| 商业证书申请 | ❌ 禁用 | 返回提示使用免费证书 |
| 商业证书下载 | ❌ 禁用 | 返回提示使用免费证书 |
| 云端证书同步 | ❌ 禁用 | 证书仅保存本地 |
| 本地证书导入 | ✅ 正常 | 可直接导入已有证书 |

---

**文档创建时间**：2026-01-02
**最后更新时间**：2026-01-13
**维护者**：MissChina <391475293@qq.com>
