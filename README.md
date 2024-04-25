# Config-Radxa-Zero

## 1. 烧录系统

### 1.1 下载系统镜像
[Radxa-Zero3 Releases](https://github.com/radxa-build/radxa-zero3/releases)

![image](https://github.com/Xinzhe99/Config-Radxa-Zero/assets/113503163/24b2a545-1474-4326-8620-c2f19561d010)

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
sudo service sshd restart
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
【1：确保buffer_size从16MB改到1000MB，2：确保USB权限(添加给radxa用户即可)】
