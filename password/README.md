# 本地密码管理器 #
现在各个网站都要注册，密码越来越多，很多时候记不住，只能重置密码，太伤。
用python写了个本地密码管理器，版本2.7。
**功能**：
1.保存密码
2.增加密码（可以指定让程序产生随机密码）
3.删除密码

**安全性**：
1.提供身份认证，一定程度上防止重放攻击
2.加密密码明文文件，一定程度防止攻击者窥探密码
![初始化](http://i.imgur.com/DmAZpBD.png)

**程序初始化**：
运行程序前，需要设置一个16位长度aes加密key（这个key在程序打包成exe文件后就无法更改），还需要设置一对rsa公私钥（可以通过命令`python pwd_manager.py -i`来生成一对），然后就是设置口令发送的邮箱，邮箱目前支持这几个，你也可以自己增加。
![](http://i.imgur.com/tb4QRis.png)
最后要设置好相应文件的文件名，之后程序运行时候，会根据相应文件名去查找内容。
![](http://i.imgur.com/8sE4rPo.png)
明文文件的内容格式可以为：
`网站名 用户名 密码`
每行字符串长度不要超过50

用py2exe将py文件打包成exe文件（执行命令`python setup.py py2exe`生成密码管理exe，执行`python decrypt_setup.py py2exe`生成解密软件exe）。

**程序执行**：
程序初始化成功后，需要将**rsa公钥文件**，**密码密文文件**与**密码管理器**放到同一个目录下，这里假设为a目录，将**保存aes key文件**与**保存rsa私钥文件**以及**解密软件**放在另一个设备中（比如u盘）的同一目录，这里假设为b目录。
程序运行时，会先往设置的邮箱发送一个由aes加密的口令与一个由rsa公钥加密的口令
![](http://i.imgur.com/1s5Gfyr.png)
用户登录邮箱后，用自己保存的aes key与rsa 私钥分别将加密的口令解密还原（通过decrypt文件夹中的decrypt.py），并将rsa私钥文件放入到a目录中，以便程序解密密文文件（不放入程序会报错并退出）。
![](http://i.imgur.com/vxWTEnG.png)
在正确输入两组口令并且放置rsa私钥文件后，用户登录成功：
![](http://i.imgur.com/hZbTcf6.png)

注意：执行更新公钥与私钥操作后，需要将rsa公钥文件与私钥文件内容分别设置成更新后的内容，下次登录依赖更新后的公私钥。


