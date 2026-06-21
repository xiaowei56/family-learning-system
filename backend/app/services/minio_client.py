"""
MinIO 对象存储客户端服务

提供文件上传、下载、删除功能，用于存储用户头像、学习图片等静态资源。
"""

from io import BytesIO
from typing import Optional

from minio import Minio
from minio.error import S3Error

from app.config import settings


class MinioService:
    """
    MinIO 对象存储服务封装。

    使用方式：
        minio_service = MinioService()
        url = minio_service.upload_file(file_bytes, "avatar.jpg")
        data = minio_service.download_file("avatar.jpg")
        minio_service.delete_file("avatar.jpg")
    """

    def __init__(self) -> None:
        self.endpoint: str = settings.minio_endpoint
        self.access_key: str = settings.minio_access_key
        self.secret_key: str = settings.minio_secret_key
        self.bucket_name: str = settings.minio_bucket_name
        self.secure: bool = settings.minio_secure

        self.client = Minio(
            endpoint=self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure,
        )

        self._ensure_bucket()

    def _ensure_bucket(self) -> None:
        """
        确保存储桶存在，不存在则创建。

        内网环境使用默认的 us-east-1 region。
        """
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                print(f"✓ MinIO 存储桶 '{self.bucket_name}' 已创建")
            else:
                print(f"✓ MinIO 存储桶 '{self.bucket_name}' 已存在")
        except S3Error as e:
            print(f"⚠ MinIO 存储桶检查/创建失败: {e}")
            raise

    def upload_file(self, file: bytes, filename: str, content_type: Optional[str] = None) -> str:
        """
        上传文件到 MinIO 存储桶。

        Args:
            file: 文件二进制数据
            filename: 存储在 MinIO 中的对象名称（含路径，如 avatars/user1.jpg）
            content_type: 文件 MIME 类型，不指定则由 MinIO 自动推断

        Returns:
            文件的公开访问 URL
        """
        file_size = len(file)
        file_stream = BytesIO(file)

        result = self.client.put_object(
            bucket_name=self.bucket_name,
            object_name=filename,
            data=file_stream,
            length=file_size,
            content_type=content_type,
        )

        # 构造文件访问 URL
        if self.secure:
            protocol = "https"
        else:
            protocol = "http"

        return f"{protocol}://{self.endpoint}/{self.bucket_name}/{result.object_name}"

    def download_file(self, filename: str) -> bytes:
        """
        从 MinIO 下载文件。

        Args:
            filename: 对象名称

        Returns:
            文件二进制数据
        """
        response = self.client.get_object(
            bucket_name=self.bucket_name,
            object_name=filename,
        )
        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()

    def delete_file(self, filename: str) -> None:
        """
        从 MinIO 删除文件。

        Args:
            filename: 对象名称
        """
        self.client.remove_object(
            bucket_name=self.bucket_name,
            object_name=filename,
        )

    def get_file_url(self, filename: str) -> str:
        """
        获取文件的公开访问 URL（不检查文件是否存在）。

        Args:
            filename: 对象名称

        Returns:
            文件的公开访问 URL
        """
        if self.secure:
            protocol = "https"
        else:
            protocol = "http"

        return f"{protocol}://{self.endpoint}/{self.bucket_name}/{filename}"
