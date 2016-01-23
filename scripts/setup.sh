#!/bin/bash

__authors__='Bruno Adelé <bruno@adele.im>'
__copyright__='Copyright (C) 2016 Bruno Adelé'
__description__="""Tool for easily create sensors daemons"""
__license__='GPL'
__version__='0.0.1'

# Vars
destdir="/opt/mksensors"
pip="$destdir/bin/pip"

# Check if the script run with the root account
checkRootUser() {
    if [ "$(id -u)" != "0" ]; then
        echo "Please run with root account"
        exit 1
    fi
}

checkToInstall() {
    checkfile=$1
    install_pkg=$2

    result=$(which $checkfile)
    if [ $? -eq 1 ]; then
        echo "$install_pkg"
        return
    fi

    echo ""
}

# Return the linux type
getLinuxType() {
    # Other version cat /etc/*-release

    if [ -f /etc/debian_version ]; then
        echo 'debian'
        return
    fi

    if [ -f /etc/arch-release ]; then
        echo 'archlinux'
        return
    fi

    echo "undefined"

}

install_pip(){
    if [ ! -x "$destdir/bin/mksensors" ]; then
        virtualenv --setuptools --no-site-packages $destdir
    fi
}

install_mksensors(){
    $pip install -U git+https://github.com/badele/mksensors.git
}

check_mksensors_configuration(){
    # Create directories
    for createpath in bin conf log
    do
        if [ ! -d "$destdir/datas/$createpath" ]; then
            mkdir -p "$destdir/datas/$createpath"
        fi
    done

    # Check /etc/supervisord.d folder
    dirname="$destdir/datas/conf/supervisord.d"
    if [ ! -d "$dirname" ]; then
        mkdir -p $dirname
    fi

    # Check supervisord.conf file
    filename="$destdir/datas/conf/supervisord.conf"
    if [ ! -x "$filename" ]; then
        cat << EOF > "$filename"
[unix_http_server]
file=/tmp/supervisor_mksensors.sock
[supervisord]
logfile=/tmp/supervisord_mksensors.log
logfile_maxbytes=50MB
logfile_backups=10
loglevel=info
pidfile=/tmp/supervisord_mksensors.pid
nodaemon=false
minfds=1024
minprocs=200
[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface
[supervisorctl]
serverurl=unix:///tmp/supervisor_mksensors.sock
[include]
files = $destdir/datas/supervisord.d/*.conf
EOF
    fi

    # Check systemd init script
    result=$(checkToInstall systemctl systemctl)
    if [ "$result" == "" ]; then
        filename="/etc/systemd/system/mksensors.service"
        cat << EOF > "$filename"
[Unit]
Description=Supervisor process control system for UNIX
Documentation=http://supervisord.org
After=network.target

[Service]
ExecStart=$destdir/bin/supervisorctl -n -c $destdir/datas/conf/supervisord.conf
ExecStop=$destdir/bin/supervisorctl shutdown
ExecReload=$destdir/bin/supervisorctl reload
KillMode=process
Restart=on-failure
RestartSec=50s

[Install]
WantedBy=multi-user.target
EOF
    fi

    # Create mksensors alias
    if [ ! -L /usr/local/bin/mksensors ]; then
        ln -s "$destdir/bin/mksensors" /usr/local/bin/mksensors
    fi

    # Create supervisorctl alias
    filename="/usr/local/bin/mksensorsctl"
    cat << EOF > "$filename"
#!/bin/bash
$destdir/bin/supervisorctl-c $destdir/datas/conf/supervisord.conf \$*
EOF
    chmod 755 $filename

}

install_debian_req() {
    toinstall=""
    toinstall="$toinstall $(checkToInstall git git)"
    toinstall="$toinstall $(checkToInstall pip python-pip)"
    toinstall="$toinstall $(checkToInstall virtualenv python-virtualenv)"
    toinstall=$(echo "$toinstall" | xargs)

    if [ "$toinstall" != "" ]; then
        apt-get update
        apt-get install -y $toinstall
    fi
}

install_archlinux_req() {

    toinstall=""
    toinstall="$toinstall $(checkToInstall /usr/bin/git git)"
    toinstall="$toinstall $(checkToInstall /usr/bin/pip2 python-pip)"
    toinstall="$toinstall $(checkToInstall /usr/bin/virtualenv python-virtualenv)"
    toinstall=$(echo "$toinstall" | xargs)

    if [ "$toinstall" != "" ]; then
        pacman -Sy
        pacman -S --noconfirm $toinstall
    fi
}


# Install requirements packages with
# Linux type package manager
install_requirements() {
    os=$1
    case $os in
        debian)
            install_debian_req
            ;;
        archlinux)
            install_archlinux_req
            ;;
        undefined)
            echo "Please install git python-pip"
    esac

}

# Verify if run with root account
checkRootUser

# Install
OS=$(getLinuxType)
install_requirements "$OS"
install_pip
install_mksensors
check_mksensors_configuration
echo "done"