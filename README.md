# 文件传输工具(file_transfer_tool)

高效解决文件传输问题，支持普通文件和文件夹的传输

### 通信协议设计

1. 基于TCP协议，服务器默认端口号为9999；

2. 客户端连接服务器成功后，客户端将用户名和密码信息（15字节定长包头 + JSON数据）发送给服务器端，服务器端校验用户名和密码，如果校验不通过，就给客户端发送一个响应数据（15字节定长包头 + JSON数据），然后断开连接，如果校验成功，先给客户端发送一个响应数据（15字节定长包头 + JSON数据），然后以文件为单位将所有数据依次发送给客户端，在发送单个文件时，首先将该文件的描述信息（定长包头，长度为347B）发送给客户端，紧接着发送文件数据给客户端，这样就完成了一个文件的发送，当发送完所有文件数据后就断开连接；

3. 文件描述信息结构为：文件名(300B，右边填充空格，UTF-8编码，如果发送的是一个普通文件，该字段的值为其文件名，如果发送的是一个文件夹，该字段的值为文件的相对路径，即相对要发送的文件夹的路径，没有斜线前缀) + 文件大小(15B，右边填充空格，如果为空文件夹，该字段的值为-1) + 文件MD5值(32B，大写形式，如果是空文件夹，该字段的值为32个空格)

4. 对于客户端用户注册功能，客户端连接服务器成功后，客户端将用户注册信息（15字节定长包头 + JSON数据）发送给服务器端，服务器端校验用户注册信息，如果成功，就将用户注册信息保存到数据库，并给客户端发送一个响应数据（15字节定长包头 + JSON数据），然后断开连接，如果失败就直接给客户端发送一个响应数据（15字节定长包头 + JSON数据）并断开连接

5. 对于客户端注册时校验用户名是否存在的功能，客户端连接服务器成功后，客户端将用户名信息（15字节定长包头 + JSON数据）发送给服务器端，服务器端校验用户名是否存在，并将校验结果信息（15字节定长包头 + JSON数据）发送给客户端，然后断开连接

6. 不同情况下的JSON数据格式定义如下：

   用户登录请求：

   {

   ​	"op": 1, 

   ​	"args": 

   ​		{

   ​			"uname": "dengjun",

   ​			"passwd": "A24314FBECDFDASFD4143241",   # 真实密码的MD5值，使用大写表示

   ​		}

   }

   用户登录响应：

   {

   ​	"op": 1,

   ​	"error_code": 0  # 0表示登录成功，1表示登录失败

   }

   用户注册请求：

   {

   ​	"op": 2,

   ​	"args": 

   ​		{

   ​			"uname": "dengjun",

   ​			"passwd": "A24314FBECDFDASFD4143241",   # 真实密码的MD5值，使用大写表示

   ​			"phone": "18574315251",  # 手机号

   ​			"emai": "dj@itmojun.com"  # 邮箱

   ​		}

   }

   用户注册响应：

   {

   ​	"op": 2,

   ​	"error_code": 0  # 0表示注册成功，1表示注册失败

   }

   客户端校验用户名是否存在请求：

   {

   ​	"op": 3,

   ​	"args": 

   ​		{

   ​			"uname": "dengjun"

   ​		}

   }

   客户端校验用户名是否存在响应：

   {

   ​	"op": 3,

   ​	"error_code": 0  # 0表示不存在，1表示存在

   }