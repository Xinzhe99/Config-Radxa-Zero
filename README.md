# Config-Radxa-Zero
官方教程地址：[Radxa-Zero3](https://docs.radxa.com/zero/zero3/getting-started)
## 1. 烧录系统

### 1.1 下载系统镜像
[official](https://docs.radxa.com/zero/zero3/getting-started/download)

### 1.2 安装烧录软件
[Etcher Download](https://etcher.balena.io/#download-etcher/)

### 1.3 【选】烧录失败后的操作
下载低级格式化软件，格式化SD卡。[HDD LLF Low Level Format Tool](https://www.hddguru.com/software/HDD-LLF-Low-Level-Format-Tool/)

## 2. 配置远程服务

### 2.1 登录系统
用户名：radxa  
密码：radxa

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
### 2.4 安装x11vnc并启动服务
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
### 3.4. 【选】确保buffer_size从16MB改到1000MB
The Spinnaker installer asks to automatically set the appropriate USB-FS memory
settings, but you can also run the configuration script at any time:
```
$ sudo sh configure_usbfs.sh
```
To manually configure the USB-FS memory:

1. If the /etc/rc.local file does NOT already exist on your system, run the
   following commands to create and make it executable
```
$ sudo touch /etc/rc.local
$ sudo chmod 744 /etc/rc.local
```
2. Open the /etc/rc.local file in any text editor,
   
```
$ sudo nano /etc/rc.local
```
and paste the following command at the end of the file:
```
sh -c 'echo 1000 > /sys/module/usbcore/parameters/usbfs_memory_mb'
```

3. Save your changes and close the file.

4. Restart the machine.

To confirm that the memory limit has been updated, run the command:
```
$ cat /sys/module/usbcore/parameters/usbfs_memory_mb
```
If this fails to set the memory limit, one can TEMPORARILY modify the
USB-FS memory until the next restart by running the following command:
```
$ sudo sh -c 'echo 1000 > /sys/module/usbcore/parameters/usbfs_memory_mb'
```

If using multiple USB3 cameras, the USB-FS memory limit may need to exceed 1000.
More information on these changes can be found at:
<https://www.flir.com/support-center/iis/machine-vision/application-note/understanding-usbfs-on-linux>

### 3.5. 【选】确保USB权限(添加给radxa用户即可)】

安装sdk过程中，会询问是否要加用户到权限群中，键入radxa即可

### 3.6. 【选】修复sd卡
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
autologin-user=radxa
autologin-user-timeout=0
...
```
### 5. 编写自启程序sh
```
# 进入程序所在目录
cd /home/radxa/Downloads/code
# 存储 sudo 密码
sudo_pwd="radxa"
# 将 sudo 密码输入至 sudo 环境，运行Acquisition
echo "${sudo_pwd}" | sudo -S nohup ./Start_capture &

```
### 6. 开启开机自启sh文件
桌面中，找到系统应用里面的start application，把sh脚本添加进去即可

### 7. 关闭系统自动息屏休眠
