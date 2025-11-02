"""
自定义密码验证器
"""
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class AlphanumericPasswordValidator:
    """
    验证密码包含字母和数字
    """
    
    def validate(self, password, user=None):
        # 检查密码是否包含字母
        if not re.search(r'[a-zA-Z]', password):
            raise ValidationError(
                _("密码必须包含至少一个字母。"),
                code='password_no_letter',
            )
        
        # 检查密码是否包含数字
        if not re.search(r'\d', password):
            raise ValidationError(
                _("密码必须包含至少一个数字。"),
                code='password_no_number',
            )

    def get_help_text(self):
        return _("您的密码必须包含至少一个字母和一个数字。")
