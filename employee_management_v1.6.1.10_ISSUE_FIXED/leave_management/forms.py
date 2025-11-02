"""
请假管理表单
"""
from django import forms
from .models import LeaveApplication, FlightSegment


class LeaveApplicationForm(forms.ModelForm):
    """
    请假申请表单
    """
    
    class Meta:
        model = LeaveApplication
        fields = [
            'leave_start_date',
            'leave_end_date',
            'leave_location',
            'leave_latitude',
            'leave_longitude',
            'leave_reason',
        ]
        widgets = {
            'leave_start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'leave_end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'leave_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入休假地点'
            }),
            'leave_latitude': forms.HiddenInput(),
            'leave_longitude': forms.HiddenInput(),
            'leave_reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': '请说明休假原因'
            }),
        }


class FlightSegmentForm(forms.ModelForm):
    """
    机票行程段表单
    """
    
    class Meta:
        model = FlightSegment
        fields = [
            'segment_type',
            'sequence',
            'departure',
            'destination',
            'flight_number',
            'flight_date',
            'flight_time',
        ]
        widgets = {
            'segment_type': forms.Select(attrs={'class': 'form-select'}),
            'sequence': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'departure': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '出发地'}),
            'destination': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '目的地'}),
            'flight_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '例：CA123'}),
            'flight_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'flight_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }


class ApprovalForm(forms.Form):
    """
    审批表单
    """
    action = forms.ChoiceField(
        choices=[
            ('approve', '批准'),
            ('reject', '拒绝'),
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='审批决定'
    )
    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': '请填写审批意见（可选）'
        }),
        label='审批意见'
    )


class CancellationForm(forms.Form):
    """
    取消休假表单
    """
    cancellation_reason = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': '请说明取消休假的原因'
        }),
        label='取消原因'
    )
