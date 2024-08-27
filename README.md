# Config-Radxa-Zero
官方教程地址：[Radxa-Zero3](https://docs.radxa.com/zero/zero3/getting-started)
## 1. 烧录系统

### 1.1 下载系统镜像
[official](https://docs.radxa.com/zero/zero3/getting-started/download)
root 默认没有设置密码，需要自己设置 "sudo passwd root"
### 1.2 安装烧录软件
[Etcher Download](https://etcher.balena.io/#download-etcher/)

### 1.3 【选】烧录失败后的操作
下载低级格式化软件，格式化SD卡。[HDD LLF Low Level Format Tool](https://www.hddguru.com/software/HDD-LLF-Low-Level-Format-Tool/)
### 1.4 修改主机名
echo 'oceanthink' > /etc/hostname
或者
hostnamectl set-hostname oceanthink

sudo reboot

要将 oceanthink 添加到 /etc/hosts 文件中，你可以按照以下步骤操作：

打开 /etc/hosts 文件:

使用 sudo 打开 /etc/hosts 文件进行编辑：
bash
复制代码
sudo vim /etc/hosts
添加 oceanthink 主机名:

在文件中找到类似以下内容的行：
复制代码
127.0.0.1   localhost

127.0.1.1   radxa-zero3

在这些行之后添加一行，将 oceanthink 添加为一个主机名。例如：
复制代码
127.0.1.1   oceanthink

这会告诉系统 oceanthink 这个主机名对应的是 127.0.1.1。


现在 /etc/hosts 文件可能看起来像这样：

复制代码
127.0.0.1   localhost

127.0.1.1   radxa-zero3

127.0.1.1   oceanthink

或者，如果你想保留所有名称关联在同一 IP 上，你也可以将 oceanthink 添加到现有的 127.0.1.1 行：

复制代码
127.0.1.1   radxa-zero3 oceanthink
保存并退出:

保存文件并退出编辑器。
验证更改:

你可以使用以下命令来验证 oceanthink 是否被正确解析：
bash
复制代码
ping oceanthink

### 1.5 创建oceanthink用户
root 默认没有设置密码，需要自己设置 "sudo passwd root"
使用管理员账号：
sudo adduser oceanthink

账号：oceanthink

密码：123456

### 1.6 自动登录系统
sudo gedit /etc/lightdm/lightdm.conf
找到 [Seat:*] 下的 #autologin-user= ，将这个配置修改为你需要登录的用户

[Seat:*]
...
autologin-user=oceanthink
autologin-user-timeout=0
...

## 2. 配置远程服务【不用这个】

### 2.1 登录系统
用户名：oceanthink  
密码：123456

### 2.2 查看radxa的ip
```
ip a
```
### 2.3 安装ssh并启动服务
```
sudo apt-get update
sudo apt-get install ssh
sudo service ssh restart
```
### 2.4 安装x11vnc并启动服务【不用这个】
(亲测-原教程里面的tigerVNC配置成功但是VNCviewer连接不上)

教程：https://blog.csdn.net/weixin_43878078/article/details/122137067

注意：x11vnc.conf配置文件可以放到自定义的路径下，服务密码可以设置成123456

我的路径：/etc/x11vnc.conf

我的密码：123456

启动服务指令：
```
source /etc/x11vnc.conf
```

亲测vnc远程速度有点慢。

## 3. 安装Flir相机的SDK
### 3.1 下载sdk，并通过xftp传到radxa中
下载地址：https://www.flir.com/products/spinnaker-sdk/?vertical=machine+vision&segment=iis

下载版本：spinnaker-2.7.0.128

选用版本：arm64_focal

![image](https://github.com/Xinzhe99/Config-Radxa-Zero/assets/113503163/a5d7a177-b823-4b4f-9eb8-161aa0b0298f)

安装完sdk后，还要安装对应的python版本spinnaker！！！
### 3.2 安装gedit
便于后面注释操作
```
sudo apt install gedit
```
### 3.3 安装spinnaker sdk

注释掉install_spinnaker_arm.sh中spinview qt相关的代码

![image](https://github.com/Xinzhe99/Config-Radxa-Zero/assets/113503163/fee0799d-9eb0-4826-9e71-cdb9a1cb5071)


接下来，完全按照README_ARM文件中的一步步操作即可。

打开教程：

```
sudo gedit README_ARM
```


If using multiple USB3 cameras, the USB-FS memory limit may need to exceed 1000.
More information on these changes can be found at:
<https://www.flir.com/support-center/iis/machine-vision/application-note/understanding-usbfs-on-linux>

### 3.4. 确保USB权限(添加给oceanthink用户)】

安装sdk过程中，会询问是否要加用户到权限群中，键入oceanthink即可

### 3.5. 【选】修复sd卡
若sd卡出现损坏，按照以下网站中方法2来进行格式化
<https://tw.easeus.com/partition-manager-tips/restore-or-format-sd-card-to-full-capacity.html>
```
cmd
diskpart
list disk
select disk X
clean
create partition primary
format fs=ntfs（或 format fs=exfat）
assign
```

### 4. 设置自动登录
开启自启程序需要设置桌面自动登录,修改 /etc/lightdm/lightdm.conf 文件
```
sudo vim /etc/lightdm/lightdm.conf
```

找到 [Seat:*] 下的 #autologin-user= ，将这个配置修改为你需要登录的用户
```
[Seat:*]
...
autologin-user=oceanthink
autologin-user-timeout=0
...
```

### 5. 降级python版本到3.8
<https://blog.csdn.net/gaoxiangfei/article/details/131242117>

### 6. 开启开机自启
创建服务
```
sudo nano /etc/systemd/system/imgcap.service
```
输入，逐一nohup和python3.8的路径需要对
```
[Unit]
Description=Image Capture Service
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/nohup /usr/local/bin/python3.8 /home/oceanthink/Documents/code/imgCap.py &
User=oceanthink
Restart=always

[Install]
WantedBy=multi-user.target
```
保存更改后,运行以下命令重新加载systemd并重启服务:
```
sudo systemctl daemon-reload
sudo systemctl restart imgcap
sudo systemctl status imgcap
```
这样imgCap.py 程序就由 systemd 服务以 Python 3.8 解释器在系统后台运行了,不受用户注销影响。后续可用 systemctl 的其他命令如 stop、start 等来控制这个服务。

### 7. 关闭系统自动息屏，以及休眠
在powermanagement应用里面全关掉


### 8. 建立完局域网，互联网上不了的解决办法

1. 界面中删除添加的ip地址
2. 重启网络服务
...
sudo systemctl restart NetworkManager
...

### 9. 制作镜像
要用u盘或者移动硬盘，挂载，ext的能被识别

### 10. 烧录
1. 刷机
2. 调整ip
3. 开启服务
```
sudo systemctl restart imgcap
```
   
