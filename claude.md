# BaoTa Panel 项目文档

## 作者: MissChina
## 邮箱: 391475293@qq.com
## 更新日期: 2026-01-09

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
g.version = '11.3.40'
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

# 第二部分：当前版本状态 (v11.3.40)

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
| 14 | `BTPanel/__init__.py` | `panel_other()` | 拦截授权错误 |
| 15 | `class/ajax.py` | `get_pd()` | 返回永久授权 |
| 16 | `class/ajax.py` | `UpdatePanel()` | 使用 public.version() |
| 17 | `class/panelModel/publicModel.py:162` | `get_pd()` | 返回永久授权 |
| 18 | `mod/base/public_aap/common.py:4295` | `get_pd()` | 返回永久授权 |

### 1.2 版本号统一管理

| 文件 | 修改 |
|------|------|
| `class/common.py:33` | 版本号定义: `g.version = '11.3.40'` |
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
__custom_plugin_url_prefix = 'https://github.com/MissChina/file/releases/download/1.0'
__custom_plugin_list = ['btwaf']
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
- `class/common.py:33` - 定义 `g.version = '11.3.40'`
- `class/ajax.py:918` - 使用 `public.version()` 替代硬编码

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

---

**文档创建时间**：2026-01-02
**最后更新时间**：2026-01-09
**维护者**：MissChina <391475293@qq.com>
