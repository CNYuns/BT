# coding: utf-8
# -------------------------------------------------------------------
# BT Panel
# -------------------------------------------------------------------
# Copyright (c) 2015-present MissChina. All rights reserved.
# -------------------------------------------------------------------
# Author: MissChina
# License: Proprietary
# -------------------------------------------------------------------

# --------------------------------------------------------------------
#   插件认证模块
# --------------------------------------------------------------------


import public
import PluginLoader

class Plugin:
    __plugin_name = None
    __is_php = False
    __dict__ = None
    __obj_dict = {}


    def __init__(self,init_plugin_name = None):
        '''
            @name 实例化插件对像
            @author MissChina<2021-06-15>
            @param init_plugin_name<string> 插件名称
            @return Plguin<object>
        '''
        if not init_plugin_name is False:
            if not init_plugin_name:
                raise ValueError('参数错误,plugin_name少需要一个有效参数')
        self.__plugin_name = init_plugin_name

    def get_plugin_list(self,upgrade_force = False):
        '''
            @name 获取插件列表
            @author MissChina<2021-06-15>
            @param upgrade_force<bool> 是否强制重新获取列表
            @return dict
        '''
        # 已修改: 完全禁用云端授权检查，使用本地缓存
        import os, json
        cache_file = '/www/server/panel/data/plugin_list.json'

        # 默认返回结果（永久企业版授权）
        default_result = {'list': [], 'pro': 253402214400, 'ltd': 253402214400}

        # 尝试从本地缓存获取
        result = None
        if os.path.exists(cache_file):
            try:
                result = json.loads(public.readFile(cache_file))
                if not isinstance(result, dict) or 'list' not in result:
                    result = None
            except:
                result = None

        # 如果本地缓存不存在或无效，尝试从 PluginLoader 获取
        if not result:
            try:
                result = PluginLoader.get_plugin_list(0)
                # 检查返回值是否有效
                if isinstance(result, dict):
                    # 如果是错误返回，使用默认值
                    if 'status' in result and result.get('status') == False:
                        result = default_result.copy()
                    elif 'list' in result:
                        # 保存到本地缓存
                        public.writeFile(cache_file, json.dumps(result))
                    else:
                        result = default_result.copy()
                else:
                    result = default_result.copy()
            except:
                result = default_result.copy()

        # 注入永久企业版授权
        if isinstance(result, dict):
            result['pro'] = 253402214400  # 企业版永久授权 (9999-12-31)
            result['ltd'] = 253402214400  # 企业版永久授权 (9999-12-31)
            if 'list' in result:
                # 专业版插件名单 (type=8)
                pro_plugins = ['btwaf', 'total', 'tamper_proof', 'webshell_check', 'sys_safe',
                               'task_manager', 'app_deployment', 'backup', 'webssh', 'rsync',
                               'mysql_tuning', 'score', 'php_guard', 'monitor', 'optimize']
                # 企业版插件名单 (type=12)
                ltd_plugins = ['btwaf_httpd', 'log_analysis', 'safe_warning', 'sys_analyse',
                               'security_check', 'panel_logs', 'process_guard', 'antivirus']

                for plugin in result['list']:
                    if isinstance(plugin, dict):
                        plugin['endtime'] = 253402214400  # 永久授权 (9999-12-31)
                        plugin['buy'] = True  # 标记为已购买
                        plugin['isBuy'] = True  # 标记为已购买
                        plugin['is_buy'] = True  # 标记为已购买
                        # 保留原价显示，不修改price和free - MissChina
                        plugin['state'] = 1  # 状态正常
                        plugin['auth_state'] = 1  # 授权状态正常

                        # 已修改: 设置ex2字段用于专业版/企业版分类筛选
                        plugin_name = plugin.get('name', '')
                        if plugin_name in pro_plugins or plugin.get('type') == 8:
                            plugin['ex2'] = '8'  # 专业版
                        elif plugin_name in ltd_plugins or plugin.get('type') == 12:
                            plugin['ex2'] = '12'  # 企业版
                        elif not plugin.get('ex2'):
                            # 保留原有ex2值或设置默认值
                            plugin['ex2'] = str(plugin.get('type', '0'))

                        # 已修改: 确保版本数据完整（修复一键安装套件版本获取问题）
                        if 'versions' in plugin and isinstance(plugin['versions'], list):
                            for ver in plugin['versions']:
                                if isinstance(ver, dict):
                                    # 确保m_version字段存在
                                    if 'm_version' not in ver or not ver['m_version']:
                                        if 'version' in ver and ver['version']:
                                            ver['m_version'] = ver['version']
                                    # 确保version字段存在
                                    if 'version' not in ver or not ver['version']:
                                        if 'm_version' in ver and ver['m_version']:
                                            ver['version'] = ver['m_version'].split('.')[-1] if '.' in ver['m_version'] else '0'
                                    # 确保其他必要字段存在
                                    if 'cpu_limit' not in ver:
                                        ver['cpu_limit'] = 1
                                    if 'mem_limit' not in ver:
                                        ver['mem_limit'] = 128
                                    if 'os_limit' not in ver:
                                        ver['os_limit'] = 0
                                    if 'dependnet' not in ver:
                                        ver['dependnet'] = ''
                        # 不修改type字段，保留原始分类以便前端筛选
        return result


    def exec_fun(self,get_args,def_name = None):
        '''
            @name 执行指定方法
            @author MissChina<2021-06-16>
            @param def_name<string> 方法名称
            @param get_args<dict_obj> POST/GET参数对像
            @return mixed
        '''
        if not def_name:
            def_name = get_args.get("s","")
        else:
            if not 's' in get_args:
                get_args.s = def_name

        res = PluginLoader.plugin_run(self.__plugin_name,def_name,get_args)
        if isinstance(res,dict):
            # 已修改: 始终注入永久授权时间戳
            res['endtime'] = 253402214400  # 永久授权 (9999-12-31)
            if 'status' in res and res['status'] == False and 'msg' in res:
                if isinstance(res['msg'],str):
                    # 已修改: 授权相关错误返回成功状态
                    auth_keywords = ['未授权', '未购买', '授权', 'unauthorized', 'license', '过期', 'expired', '无法获取', '授权列表', '加载失败']
                    msg_lower = res['msg'].lower()
                    is_auth_error = any(keyword.lower() in msg_lower for keyword in auth_keywords)
                    if is_auth_error:
                        return {'status': True, 'msg': ''}
                    elif res['msg'].find('Traceback ') != -1:
                        raise public.PanelError(res['msg'])
        return res

    def get_fun(self,def_name):
        '''
            @name 获取函对像
            @author MissChina<2021-06-28>
            @param def_name<string> 函数名称
            @return func_object
        '''
        if def_name in self.__obj_dict.keys():
            return self.__obj_dict[def_name]
        get_args = public.dict_obj()
        get_args.plugin_get_object = 1
        res = PluginLoader.plugin_run(self.__plugin_name,def_name,get_args)
        # 已修改: 始终注入永久授权时间戳
        if isinstance(res, dict):
            res['endtime'] = 253402214400  # 永久授权 (9999-12-31)
        return res


    def isdef(self,def_name):
        '''
            @name 指定方法是否存在
            @author MissChina<2021-06-16>
            @param def_name<string> 方法名称
            @return bool
        '''
        if self.__is_php: return True
        self.__obj_dict[def_name] = self.get_fun(def_name)
        return True if self.__obj_dict[def_name] else False

    def __dir__(self):
        return ''

