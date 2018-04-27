from django.core.files.storage import FileSystemStorage

# class FdfsStorage(FileSystemStorage):
#     '''自定义文件存储'''
#
#     def _save(self, name, content):
#         '''当用户通过管理后台上传文件时，
#         DJANGO会调用此方法来保存用户上传到DJANGO网站的文件
#         我们可以用此方法保存用户上传的文件到FDFS服务器上'''
#         path = super()._save(name, content)
#         print('name=%s, content=%s, path=%s' % (name, type(content), path))
#         return path
from fdfs_client.client import Fdfs_client


class FdfsStorage(FileSystemStorage):
    '''自定义文件存储'''

    def _save(self, name, content):
        # 默认存储方式
        # path = super()._save(name, content)

        # 自定义存储方式
        client = Fdfs_client('utils/fdfs/client.conf')
        try:
            data = content.read() # 文件内容(二进制)  buffer:缓存
            dict_data = client.upload_by_buffer(data)
            if dict_data.get('Status') != 'Upload successed.':  # 不要漏了后面的点
                raise Exception('上传文件到fdfs失败')

            # 获取文件id
            path = dict_data.get('Remote file_id')
        except Exception as e:
            print(e)
            raise e  #不要直接捕获异常，抛出去由调用者处理
        return path

    def url(self, name):
        '''重写url方法'''
        url = super().url(name)
        return 'http://127.0.0.1:8888/' + url

