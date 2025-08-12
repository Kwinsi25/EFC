from rest_framework import serializers
from .models import *

class SystemLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemLog
        fields = ['id', 'type', 'remark', 'created_date']


class ReportLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportLog
        fields = '__all__'
        read_only_fields = ['generated_by', 'export_by', 'created_date', 'updated_date']