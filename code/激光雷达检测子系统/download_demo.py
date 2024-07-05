# -*- coding: utf-8 -*-
import oss2
from oss2.credentials import EnvironmentVariableCredentialsProvider

# 从环境变量中获取访问凭证。运行本代码示例之前，请确保已设置环境变量OSS_ACCESS_KEY_ID和OSS_ACCESS_KEY_SECRET。
# auth = oss2.ProviderAuth(EnvironmentVariableCredentialsProvider())
auth = oss2.Auth('LTAI5tSdmM7JBcPdEUEiSJH8', 'twudtXOjsndbj57EJsqSjBvaafrbKD')
# yourEndpoint填写Bucket所在地域对应的Endpoint。以华东1（杭州）为例，Endpoint填写为https://oss-cn-hangzhou.aliyuncs.com。
# 填写Bucket名称。
bucket = oss2.Bucket(auth, 'https://oss-cn-beijing.aliyuncs.com', 'my-pcd11')

# 填写Object完整路径，完整路径中不包含Bucket名称，例如testfolder/exampleobject.txt。
# 下载Object到本地文件，并保存到指定的本地路径D:\\localpath\\examplefile.txt。如果指定的本地文件存在会覆盖，不存在则新建。
bucket.get_object_to_file('bag.zip', '/home/pie/桌面/1.zip')     
