from django.contrib import admin
from . import models





admin.site.register(models.DailyRecord)
admin.site.register(models.temporay)
admin.site.register(models.Branches)
admin.site.register(models.Employee)
admin.site.register(models.RequestForm)
admin.site.register(models.AttendanceCount)
admin.site.register(models.EmployeeStatus)