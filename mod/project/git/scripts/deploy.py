# coding: utf-8
# -------------------------------------------------------------------
# BT Panel
# -------------------------------------------------------------------
# Copyright (c) 2015-present MissChina. All rights reserved.
# -------------------------------------------------------------------
# Author: MissChina
# License: Proprietary
# -------------------------------------------------------------------

import os,sys,time,datetime,base64,subprocess

if "/www/server/panel/class" not in sys.path:
    sys.path.insert(0, "/www/server/panel/class")
if '/www/server/panel' not in sys.path:
    sys.path.insert(0, '/www/server/panel')

import public

# 全局日志收集变量
DEPLOY_LOGS = []
# 部署开始时间
DEPLOY_START_TIME = 0

def log(msg, icon="🚀"):
    """记录日志并收集到全局变量"""
    log_entry = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {icon} {msg}"
    print(log_entry)
    DEPLOY_LOGS.append(log_entry)

def print_separator():
    """打印分割线"""
    separator = "\n" + "="*60 + "\n" + f"🚀 Git 自动部署 - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}" + "\n" + "="*60 + "\n"
    print(separator)
    DEPLOY_LOGS.append(separator)

def run_cmd(cmd, cwd=None):
    """执行命令并返回输出"""
    cmd = f'bash -l -c \'{cmd}\''
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout.strip())
            DEPLOY_LOGS.append(result.stdout.strip())
        if result.stderr:
            print(result.stderr.strip())
            DEPLOY_LOGS.append(result.stderr.strip())
        return result.returncode == 0
    except Exception as e:
        error_msg = f"命令执行失败: {str(e)}"
        log(error_msg, "❌")
        return False

def get_site_info(site_name):
    """获取网站信息"""
    site = public.M('sites').where("name = ?", (site_name,)).find()
    if not site:
        log(f"网站不存在: {site_name}", "❌")
        return None
    
    site_path = site.get('path')
    if not os.path.exists(f"{site_path}/.git"):
        log(f"不是Git仓库: {site_path}", "❌")
        return None
    
    return {'site': site, 'path': site_path}

def display_git_info(site_path):
    """显示git仓库信息"""
    try:
        # 获取当前分支
        result = subprocess.run(f"cd {site_path} && git rev-parse --abbrev-ref HEAD", 
                              shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            current_branch = result.stdout.strip()
            log(f"当前分支: {current_branch}")
            
            # 获取最新commit信息
            result = subprocess.run(f"cd {site_path} && git log -1 --pretty=format:'%h|%s|%an'", 
                                  shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                commit_info = result.stdout.strip().split('|')
                if len(commit_info) >= 3:
                    log(f"最新提交: {commit_info[0]} - {commit_info[1]} (by {commit_info[2]})")
    except:
        pass

def execute_deploy_script(site_path, deploy_script):
    """执行部署脚本"""
    if not deploy_script:
        return True, ""
    
    log("执行部署脚本...")
    script_file = f"/tmp/deploy_{int(time.time())}.sh"
    try:
        with open(script_file, 'w') as f:
            f.write(f"cd {site_path}\n{deploy_script}")
        os.chmod(script_file, 0o755)
        
        if not run_cmd(f"bash {script_file}"):
            return False, "部署脚本执行失败"
        
        return True, ""
    finally:
        if os.path.exists(script_file):
            os.remove(script_file)

def auto_deploy(config):
    """自动部署（无分支无commit）"""
    site_name = config.get('type_parm')
    config_branch = config.get('branch', 'main')
    deploy_script = config.get('deploy_script', '')
    
    log(f"自动部署: {site_name} -> {config_branch}")
    
    # 获取网站信息
    site_info = get_site_info(site_name)
    if not site_info:
        return False, "网站不存在或不是Git仓库"
    
    site_path = site_info['path']
    display_git_info(site_path)
    
    # 拉取代码
    if not run_cmd(f"cd {site_path} && git pull origin {config_branch}"):
        return False, "代码拉取失败"
    
    log("🚀 仓库成功部署!")
    
    # 执行部署脚本
    success, error_msg = execute_deploy_script(site_path, deploy_script)
    if not success:
        return False, error_msg
    
    # 修正权限
    run_cmd(f"chown -R www:www {site_path}")
    log("部署完成", "✅")
    
    return True, ""

def manual_branch_deploy(config, manual_branch):
    """手动分支部署（有分支）"""
    site_name = config.get('type_parm')
    deploy_script = config.get('deploy_script', '')
    
    log(f"手动部署分支: {site_name} -> {manual_branch}")
    
    # 获取网站信息
    site_info = get_site_info(site_name)
    if not site_info:
        return False, "网站不存在或不是Git仓库"
    
    site_path = site_info['path']
    display_git_info(site_path)
    
    # 切换分支并拉取代码
    if not run_cmd(f"cd {site_path} && git checkout {manual_branch}"):
        return False, f"切换到分支失败: {manual_branch}"
    
    if not run_cmd(f"cd {site_path} && git pull origin {manual_branch}"):
        return False, "代码拉取失败"
    
    log("🚀 手动分支部署成功!")
    
    # 执行部署脚本
    success, error_msg = execute_deploy_script(site_path, deploy_script)
    if not success:
        return False, error_msg
    
    # 修正权限
    run_cmd(f"chown -R www:www {site_path}")
    log("部署完成", "✅")
    
    return True, ""

def manual_rollback_deploy(config, manual_branch, manual_commit):
    """手动回滚部署（有分支有commit）"""
    site_name = config.get('type_parm')
    deploy_script = config.get('deploy_script', '')
    
    log(f"回滚代码: {site_name} -> {manual_branch} -> {manual_commit[:8]}")
    
    # 获取网站信息
    site_info = get_site_info(site_name)
    if not site_info:
        return False, "网站不存在或不是Git仓库"
    
    site_path = site_info['path']
    display_git_info(site_path)
    
    # 切换分支
    if not run_cmd(f"cd {site_path} && git checkout {manual_branch}"):
        return False, f"切换到分支失败: {manual_branch}"
    
    # 回滚到指定commit
    if not run_cmd(f"cd {site_path} && git reset --hard {manual_commit}"):
        return False, "回滚失败"
    
    log(f"🚀 成功回退到commit: {manual_commit[:8]}!")
    
    # 执行部署脚本
    success, error_msg = execute_deploy_script(site_path, deploy_script)
    if not success:
        return False, error_msg
    
    # 修正权限
    run_cmd(f"chown -R www:www {site_path}")
    log("部署完成", "✅")
    
    return True, ""

def save_deploy_log(config, success, error_msg="", deploy_mode=1):
    """保存部署日志到数据库（总是被调用）"""
    try:
        # 基础信息
        git_manager_id = config.get('id', 0)
        webhook_name = config.get('webhook_name', '')
        site_name = config.get('type_parm', '')
        deploy_type = config.get('type', 'site')
        branch = config.get('branch', 'main')
        deploy_script = config.get('deploy_script', '')
        duration = time.time() - DEPLOY_START_TIME
        log_content = get_deploy_logs()
        deploy_time = int(time.time())
        status = 1 if success else 0
        
        # 获取commit信息
        commit_hash, commit_message, commit_author = "", "", ""
        if site_name:
            site_info = get_site_info(site_name)
            if site_info:
                commit_hash, commit_message, commit_author = get_commit_info(site_info['path'])
        
        # 插入日志记录
        public.M('git_deploy_logs').insert({
            'git_manager_id': git_manager_id,
            'webhook_name': webhook_name,
            'site_name': site_name,
            'type': deploy_type,
            'status': status,
            'deploy_time': deploy_time,
            'duration': round(duration, 2),
            'commit_hash': commit_hash,
            'branch': branch,
            'log_content': log_content,
            'error_msg': error_msg,
            'deploy_script': deploy_script,
            'deploy_mode': deploy_mode,
            'commit_message': commit_message,
            'commit_author': commit_author
        })
        
        mode_name = {1: "自动部署", 2: "手动分支部署", 3: "手动回滚部署"}.get(deploy_mode, "未知")
        log(f"部署日志已保存 ({mode_name}, git_manager_id: {git_manager_id})", "📋")
        
    except Exception as e:
        log(f"保存部署日志失败: {str(e)}", "⚠️")

def get_commit_info(site_path):
    """获取commit信息"""
    commit_hash = ""
    commit_message = ""
    commit_author = ""
    
    try:
        # 获取commit hash
        result = subprocess.run(f"cd {site_path} && git rev-parse HEAD", 
                                shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            commit_hash = result.stdout.strip()
            
            # 获取commit message和author
            result = subprocess.run(f"cd {site_path} && git log -1 --pretty=format:'%s|%an' {commit_hash}", 
                                  shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                log_info = result.stdout.strip().split('|')
                if len(log_info) >= 2:
                    commit_message = log_info[0]
                    commit_author = log_info[1]
    except:
        pass
    
    return commit_hash, commit_message, commit_author

def get_deploy_logs():
    """获取完整的部署日志"""
    return "\n".join(DEPLOY_LOGS)

def prepare_deployment():
    """准备部署：解析参数、确定模式、获取配置"""
    # 解析参数
    if len(sys.argv) < 2:
        log("缺少参数", "❌")
        return None, None, None, None, None
    
    try:
        webhook_name = base64.b64decode(sys.argv[1]).decode('utf-8')
        
        # 解析手动部署参数
        manual_branch = None
        manual_commit = None
        
        if len(sys.argv) >= 3:
            manual_branch = sys.argv[2]
            log(f"检测到手动分支参数: {manual_branch}")
            
        if len(sys.argv) >= 4:
            manual_commit = sys.argv[3]
            log(f"检测到手动回滚参数: {manual_commit[:8]}")
        
        # 确定部署模式
        if manual_commit:
            deploy_mode, mode_name = 3, "手动回滚部署"
        elif manual_branch:
            deploy_mode, mode_name = 2, "手动分支部署"
        else:
            deploy_mode, mode_name = 1, "自动部署"
        
        # 获取配置
        config = public.M('git_manager').where("webhook_name = ?", (webhook_name,)).find()
        if not config:
            log(f"未找到配置: {webhook_name}", "❌")
            return None, None, None, None, None
        
        deploy_type = config.get('type', 'site')
        log(f"部署类型: {deploy_type}")
        return config, manual_branch, manual_commit, deploy_mode, mode_name
        
    except Exception as e:
        log(f"参数解析失败: {str(e)}", "❌")
        return None, None, None, None, None

def execute_deployment(config, manual_branch, manual_commit, deploy_mode):
    """执行部署"""
    deploy_type = config.get('type', 'site')
    
    if deploy_type == 'site':
        if deploy_mode == 1:
            return auto_deploy(config)
        elif deploy_mode == 2:
            return manual_branch_deploy(config, manual_branch)
        elif deploy_mode == 3:
            return manual_rollback_deploy(config, manual_branch, manual_commit)
    elif deploy_type == 'project':
        log("项目类型部署，跳过...")
        return True, ""
    else:
        log(f"未知部署类型: {deploy_type}", "❌")
        return False, f"未知部署类型: {deploy_type}"

if __name__ == '__main__':
    # 记录开始时间
    DEPLOY_START_TIME = time.time()
    
    # 准备部署
    config, manual_branch, manual_commit, deploy_mode, mode_name = prepare_deployment()
    if not config:
        sys.exit(1)
    
    print_separator()
    webhook_name = config.get('webhook_name', '')
    log(f"开始部署: {webhook_name} ({mode_name})")
    
    try:
        # 执行部署
        success, error_msg = execute_deployment(config, manual_branch, manual_commit, deploy_mode)
        
    except Exception as e:
        error_msg = str(e)
        log(f"部署异常: {error_msg}", "❌")
        success = False

    # 保存部署日志（总是被调用）
    # config['branch'] = manual_branch or config.get('branch', '')
    save_deploy_log(config, success, error_msg, deploy_mode)
    
    sys.exit(0 if success else 1)

