from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class LocationRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    location_name = models.CharField(max_length=200, verbose_name='位置名称')
    latitude = models.FloatField(null=True, blank=True, verbose_name='纬度')
    longitude = models.FloatField(null=True, blank=True, verbose_name='经度')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='上报时间')
    
    class Meta:
        verbose_name = '位置记录'
        verbose_name_plural = '位置记录'
