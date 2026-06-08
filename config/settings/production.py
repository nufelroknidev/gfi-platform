from .base import *

DEBUG = False

# SSL terminates at nginx; trust the X-Forwarded-Proto header it sets
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = False  # nginx handles the redirect, not Django
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# S3 media storage
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME', default='ap-southeast-1')
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
AWS_S3_CUSTOM_DOMAIN = env('AWS_CLOUDFRONT_DOMAIN', default=None)
AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}

STORAGES = {
    'default': {
        'BACKEND': 'apps.utils.storage.MediaS3Storage',
    },
    'staticfiles': {
        'BACKEND': 'apps.utils.storage.StaticS3Storage',
    },
}
