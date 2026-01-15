#!/bin/bash
# BT Panel 安装脚本
# 作者: MissChina
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
LANG=en_US.UTF-8

setup_path=/www
PANEL_PATH="${setup_path}/server/panel"
REPO="CNYuns/BT"

Red_Error(){
    echo '=================================================';
    printf '\033[1;31;40m%b\033[0m\n' "$1";
    echo '=================================================';
    exit 1;
}

if [ $(whoami) != "root" ]; then
    Red_Error "请使用root用户运行安装脚本"
fi

is64bit=$(getconf LONG_BIT)
if [ "${is64bit}" != '64' ]; then
    Red_Error "抱歉, 当前面板版本不支持32位系统"
fi

MEM_TOTAL=$(free -m|grep Mem|awk '{print $2}')
if [ "${MEM_TOTAL}" ] && [ "${MEM_TOTAL}" -lt "450" ]; then
    Red_Error "内存小于450MB，无法安装宝塔面板"
fi

Get_Sys_Info(){
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        SYS_NAME=$ID
        SYS_VERSION=$VERSION_ID
    elif [ -f /etc/redhat-release ]; then
        SYS_NAME="centos"
        SYS_VERSION=$(cat /etc/redhat-release | grep -oE '[0-9]+' | head -1)
    else
        Red_Error "不支持的操作系统"
    fi

    SYS_VERSION_MAIN=${SYS_VERSION%%.*}

    case $SYS_NAME in
        centos|rhel|rocky|almalinux|fedora)
            if [ "$SYS_VERSION_MAIN" -ge 8 ]; then
                OS_PACKAGE="centos8"
                PM="dnf"
            else
                OS_PACKAGE="centos7"
                PM="yum"
            fi
            ;;
        ubuntu)
            if [ "$SYS_VERSION_MAIN" -ge 22 ]; then
                OS_PACKAGE="ubuntu22"
            else
                OS_PACKAGE="ubuntu20"
            fi
            PM="apt-get"
            ;;
        debian)
            if [ "$SYS_VERSION_MAIN" -ge 12 ]; then
                OS_PACKAGE="debian12"
            elif [ "$SYS_VERSION_MAIN" -ge 11 ]; then
                OS_PACKAGE="debian11"
            else
                OS_PACKAGE="debian10"
            fi
            PM="apt-get"
            ;;
        *)
            Red_Error "不支持的系统: $SYS_NAME"
            ;;
    esac

    echo "系统: $SYS_NAME $SYS_VERSION -> $OS_PACKAGE"
}

Install_Deps(){
    echo "安装依赖..."
    if [ "$PM" = "apt-get" ]; then
        apt-get update -y
        apt-get install -y wget curl python3 python3-pip python3-dev libffi-dev libssl-dev
    else
        $PM install -y wget curl python3 python3-pip python3-devel libffi-devel openssl-devel
    fi
}

Install_Pyenv(){
    echo "安装Python环境..."

    # 确定pyenv下载URL
    case "$OS_PACKAGE" in
        centos7) PYENV_OS="el7" ;;
        centos8) PYENV_OS="el8" ;;
        *) PYENV_OS="$OS_PACKAGE" ;;
    esac

    # 自定义镜像URL (加速下载)
    case "$PYENV_OS" in
        ubuntu*) PYENV_URL="https://github.com/MissChina/file/releases/download/1.0/pyenv-ubuntu22-x64.tar.gz" ;;
        *) PYENV_URL="https://download.bt.cn/install/pyenv/pyenv-${PYENV_OS}-x64.tar.gz" ;;
    esac
    echo "下载地址: $PYENV_URL"

    cd /tmp
    rm -f pyenv.tar.gz

    wget --no-check-certificate -O pyenv.tar.gz "$PYENV_URL" -T 300 --tries=3

    if [ $? -ne 0 ] || [ ! -s pyenv.tar.gz ]; then
        echo "pyenv下载失败，使用系统Python"
        return 1
    fi

    # 检查文件大小
    FILE_SIZE=$(stat -c%s pyenv.tar.gz 2>/dev/null || stat -f%z pyenv.tar.gz 2>/dev/null)
    if [ "$FILE_SIZE" -lt 10000000 ]; then
        echo "pyenv文件不完整，使用系统Python"
        rm -f pyenv.tar.gz
        return 1
    fi

    echo "解压pyenv..."
    tar -xzf pyenv.tar.gz -C $PANEL_PATH/
    rm -f pyenv.tar.gz

    chmod -R 700 $PANEL_PATH/pyenv/bin
    echo "pyenv安装完成"
    return 0
}

Install_Python_Deps(){
    echo "安装Python依赖..."
    if [ -f "/usr/bin/pip3" ]; then
        pip3 install -U pip setuptools -q
        pip3 install flask gevent psutil chardet pyOpenSSL cryptography -q
    fi
}

Download_Panel(){
    echo "获取下载地址..."
    RELEASE_API="https://api.github.com/repos/${REPO}/releases/latest"
    DOWNLOAD_URL=$(curl -sS --connect-timeout 10 $RELEASE_API | grep "browser_download_url.*${OS_PACKAGE}.tar.gz\"" | cut -d '"' -f 4 | head -1)

    if [ -z "$DOWNLOAD_URL" ]; then
        Red_Error "获取下载地址失败"
    fi

    echo "下载地址: $DOWNLOAD_URL"
    echo "下载面板文件..."

    cd /tmp
    rm -f bt-panel.tar.gz
    wget -O bt-panel.tar.gz "$DOWNLOAD_URL" -T 120

    if [ $? -ne 0 ] || [ ! -s bt-panel.tar.gz ]; then
        Red_Error "下载失败"
    fi

    echo "解压文件..."
    tar -xzf bt-panel.tar.gz -C /

    if [ $? -ne 0 ]; then
        Red_Error "解压失败"
    fi

    rm -f bt-panel.tar.gz
}

Set_Panel(){
    echo "配置面板..."

    # 停止旧进程
    if [ -f "/etc/init.d/bt" ]; then
        /etc/init.d/bt stop
        sleep 1
    fi

    # 创建www用户
    wwwUser=$(cat /etc/passwd|cut -d ":" -f 1|grep ^www$)
    if [ "${wwwUser}" != "www" ]; then
        groupadd www
        useradd -s /sbin/nologin -g www www
    fi

    # bt命令
    chmod +x /etc/init.d/bt
    ln -sf /etc/init.d/bt /usr/bin/bt

    # 面板脚本权限
    chmod +x $PANEL_PATH/BT-Panel 2>/dev/null
    chmod +x $PANEL_PATH/BT-Task 2>/dev/null
    chmod -R 700 $PANEL_PATH/pyenv/bin 2>/dev/null

    # 确定Python路径
    if [ -f "$PANEL_PATH/pyenv/bin/python3" ]; then
        pythonV="$PANEL_PATH/pyenv/bin/python3"
        ln -sf $PANEL_PATH/pyenv/bin/pip3 /usr/bin/btpip
        ln -sf $PANEL_PATH/pyenv/bin/python3 /usr/bin/btpython
    elif [ -f "/usr/bin/python3" ]; then
        pythonV="/usr/bin/python3"
    elif [ -f "/usr/bin/python" ]; then
        pythonV="/usr/bin/python"
    else
        Red_Error "未找到Python环境"
    fi

    cd $PANEL_PATH

    # 初始化数据库
    if [ -f "$PANEL_PATH/script/init_db.py" ]; then
        $pythonV $PANEL_PATH/script/init_db.py init_db
    fi
    if [ -f "$PANEL_PATH/tools.py" ]; then
        $pythonV $PANEL_PATH/tools.py check_db
    fi

    # 端口
    if [ ! -f "$PANEL_PATH/data/port.pl" ]; then
        panelPort=$(shuf -i 8000-65000 -n 1)
        echo $panelPort > $PANEL_PATH/data/port.pl
    else
        panelPort=$(cat $PANEL_PATH/data/port.pl)
    fi

    # 安全入口
    if [ ! -f "$PANEL_PATH/data/admin_path.pl" ]; then
        auth_path=$(head -c 16 /dev/urandom | md5sum | head -c 8)
        echo "/$auth_path" > $PANEL_PATH/data/admin_path.pl
    fi
    auth_path=$(cat $PANEL_PATH/data/admin_path.pl)

    chmod 600 $PANEL_PATH/data/*.pl 2>/dev/null
}

Set_Firewall(){
    echo "配置防火墙..."

    if command -v firewall-cmd >/dev/null 2>&1; then
        firewall-cmd --permanent --add-port=${panelPort}/tcp >/dev/null 2>&1
        firewall-cmd --permanent --add-port=80/tcp >/dev/null 2>&1
        firewall-cmd --permanent --add-port=443/tcp >/dev/null 2>&1
        firewall-cmd --permanent --add-port=22/tcp >/dev/null 2>&1
        firewall-cmd --reload >/dev/null 2>&1
    fi

    if command -v ufw >/dev/null 2>&1; then
        ufw allow ${panelPort}/tcp >/dev/null 2>&1
        ufw allow 80/tcp >/dev/null 2>&1
        ufw allow 443/tcp >/dev/null 2>&1
        ufw allow 22/tcp >/dev/null 2>&1
    fi
}

Start_Panel(){
    echo "启动面板..."
    /etc/init.d/bt start
    sleep 2

    # 设置默认用户名和密码
    cd $PANEL_PATH

    # bt 5 设置用户名为 050213
    username="050213"
    $pythonV tools.py username "$username"

    # bt 6 设置密码为 xzc050213 (密码需大于5位)
    password="xzc050213"
    $pythonV tools.py panel "$password"

    echo $password > $PANEL_PATH/default.pl
    chmod 600 $PANEL_PATH/default.pl
}

Get_Ip_Address(){
    # 获取外网IP
    getIpAddress=$(curl -4 -sS --connect-timeout 5 -m 10 https://api.bt.cn/Api/getIpAddress 2>/dev/null)
    if [ -z "$getIpAddress" ]; then
        getIpAddress=$(curl -4 -sS --connect-timeout 5 -m 10 ip.sb 2>/dev/null)
    fi
    if [ -z "$getIpAddress" ]; then
        getIpAddress=$(ip addr | grep -E -o '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' | grep -E -v "^127\.|^255\.|^0\.|^10\.|^172\.(1[6-9]|2[0-9]|3[01])\.|^192\.168\." | head -n 1)
    fi

    # 获取内网IP
    localIpAddress=$(ip addr | grep -E -o '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' | grep -E "^10\.|^172\.(1[6-9]|2[0-9]|3[01])\.|^192\.168\." | head -n 1)
    if [ -z "$localIpAddress" ]; then
        localIpAddress=$(hostname -I 2>/dev/null | awk '{print $1}')
    fi
}

Show_Result(){
    Get_Ip_Address

    echo ""
    echo "=================================================================="
    echo -e "\033[32m安装完成!\033[0m"
    echo "=================================================================="
    echo ""
    echo " 外网面板地址: http://${getIpAddress}:${panelPort}${auth_path}"
    if [ -n "$localIpAddress" ]; then
        echo " 内网面板地址: http://${localIpAddress}:${panelPort}${auth_path}"
    fi
    echo ""
    echo " username: $username"
    echo " password: $password"
    echo ""
    echo -e "\033[33m注意：初始密码仅在首次登录面板前能正确获取，其它时间请通过 bt 5 命令修改密码\033[0m"
    echo "=================================================================="
}

echo ""
echo "+----------------------------------------------------------------------"
echo "| BT Panel 宝塔面板安装脚本"
echo "| 作者: MissChina"
echo "+----------------------------------------------------------------------"
echo ""

Get_Sys_Info
Install_Deps
Download_Panel
Install_Pyenv || Install_Python_Deps
Set_Panel
Set_Firewall
Start_Panel
Show_Result
