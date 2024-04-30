from django.db import models
from django.utils import timezone
from datetime import date,datetime




#New Models
class Branches(models.Model):
    BranchCode = models.CharField(max_length=20,unique=True,primary_key=True)
    Company = models.CharField(max_length=50)
    Location = models.CharField(max_length=50)
    Employees = models.CharField(max_length=10)
    BranchImage = models.ImageField(upload_to='branch_image/', null=True, blank=True)


class Employee(models.Model):
    EmpCode = models.CharField(max_length=20,unique=True,primary_key=True)
    BranchCode = models.ForeignKey(Branches, on_delete = models.CASCADE, to_field = 'BranchCode', null = True)
    Firstname = models.CharField(max_length=20)
    Middlename = models.CharField(max_length=20)
    Lastname = models.CharField(max_length=20)
    DateofBirth = models.DateField(default=date(2000, 1, 1), null=True)
    BloodType = models.CharField(max_length=3, default="N/D")
    Gender = models.CharField(max_length=8, default="Male")
    CivilStatus = models.CharField(max_length=10, default="N/A")
    Address = models.CharField(max_length=50, default="N/D")
    Position = models.CharField(max_length=50)
    Department = models.CharField(max_length=50, default="N/A", null=True, blank=True)
    EmployementDate = models.DateField(default=date(2000, 1, 1))
    EmploymentStatus = models.CharField(max_length=15,default="Regular")
    EmpImage = models.ImageField(upload_to='emp_image/', null=True, blank=True)
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)



class DailyRecord(models.Model):
    ID = models.AutoField(primary_key=True, default=None)
    EmpCode = models.ForeignKey(Employee, on_delete=models.CASCADE, to_field='EmpCode', null=True)
    Empname = models.CharField(max_length=50, default = 'Unknown')
    date = models.DateField(null=True)
    timein = models.TimeField(blank=True, null=True)
    timeout = models.TimeField(blank=True, null=True)
    breakout = models.TimeField(blank=True, null=True)
    breakin = models.TimeField(blank=True, null=True)
    totallateness = models.CharField(default='00:00:00', max_length=50,null=True)
    latecount = models.CharField(default = '0', max_length = 6,null=True)
    totalundertime = models.CharField(default='00:00',max_length= 8,null=True)
    totalovertime = models.CharField(default='00:00:00', max_length= 8, null=True)
    created_at = models.DateTimeField(default=timezone.now)  
    approveOT = models.BooleanField(default=False)
    late = models.CharField(default = "None", max_length = 10,null=True)
    absent = models.CharField(default = "None", max_length = 10,null=True)
    remarks =models.CharField(default = "None", max_length = 400,null=True)
    user_branchname = models.CharField(max_length=50, null=True, blank=True)
    flex_time = models.CharField(max_length=15, null=True,blank=True,default= "None")
   
    class Meta:
        db_table = 'attendance'
        get_latest_by = 'date'


    def to_sql(self):
        Empname = f"'{self.Empname}'" if self.Empname is not None else 'NULL'
        EmpCode_id = f"'{self.EmpCode.EmpCode}'" if self.EmpCode is not None else 'NULL'
        date = f"'{self.date}'" if self.date is not None else 'NULL'
        timein = f"'{self.timein.strftime('%H:%M:%S')}'" if self.timein is not None else 'NULL'
        timeout = f"'{self.timeout.strftime('%H:%M:%S')}'" if self.timeout is not None else 'NULL'
        breakout = f"'{self.breakout.strftime('%H:%M:%S')}'" if self.breakout is not None else 'NULL'
        breakin = f"'{self.breakin.strftime('%H:%M:%S')}'" if self.breakin is not None else 'NULL'
        totallateness = f"'{self.totallateness}'" if self.totallateness is not None else 'NULL'
        latecount = f"'{self.latecount}'" if self.latecount is not None else 'NULL'
        totalundertime = f"'{self.totalundertime}'" if self.totalundertime is not None else 'NULL'
        totalovertime = f"'{self.totalovertime}'" if self.totalovertime is not None else 'NULL'
        created_at = f"'{self.created_at.strftime('%Y-%m-%d %H:%M:%S')}'"
        approveOT = int(self.approveOT) if self.absent is not None else 'NULL'
        absent = f"'{self.absent}'" if self.absent is not None else 'NULL'
        late = f"'{self.late}'" if self.late is not None else 'NULL'
        remarks = f"'{self.remarks}'" if self.remarks is not None else 'NULL'
        user_branchname = f"'{self.user_branchname}'" if self.user_branchname is not None else 'NULL'
        flex_time = f"'{self.flex_time}'" if self.flex_time is not None else 'NULL'

       
        return f"INSERT INTO attendance (Empname, EmpCode_id, date, timein, timeout, breakout, breakin, totallateness, latecount, totalundertime, totalovertime, created_at, approveOT, absent, late, remarks,user_branchname,flex_time) " \
           f"VALUES ({Empname}, {EmpCode_id}, {date}, {timein}, {timeout}, {breakout}, {breakin}, {totallateness}, {latecount}, {totalundertime}, {totalovertime}, {created_at}, {approveOT}, {absent}, {late}, {remarks}, {user_branchname}, {flex_time});"
      
    def to_sql_all(self):
        timein = f"'{self.timein.strftime('%H:%M:%S')}'" if self.timein is not None else 'NULL'
        Empname = f"'{self.Empname}'" if self.Empname is not None else 'NULL'
        EmpCode_id = f"'{self.EmpCode.EmpCode}'" if self.EmpCode is not None else 'NULL'
        date = f"'{self.date}'" if self.date is not None else 'NULL'
        timeout = f"'{self.timeout}'" if self.timeout is not None else 'NULL'
        breakout = f"'{self.breakout}'" if self.breakout is not None else 'NULL'
        breakin = f"'{self.breakin}'" if self.breakin is not None else 'NULL'
        totallateness = f"'{self.totallateness}'" if self.totallateness is not None else 'NULL'
        latecount = f"'{self.latecount}'" if self.latecount is not None else 'NULL'
        totalundertime = f"'{self.totalundertime}'" if self.totalundertime is not None else 'NULL'
        totalovertime = f"'{self.totalovertime}'" if self.totalovertime is not None else 'NULL'
        approveOT = int(self.approveOT) if self.absent is not None else 'NULL'
        absent = f"'{self.absent}'" if self.absent is not None else 'NULL'
        late = f"'{self.late}'" if self.late is not None else 'NULL'
        remarks = f"'{self.remarks}'" if self.remarks is not None else 'NULL'
        created_at = f"'{self.created_at.strftime('%Y-%m-%d %H:%M:%S')}'"
        user_branchname = f"'{self.user_branchname}'" if self.user_branchname is not None else 'NULL'

        if timein == "'00:00:00'":
        # If timein is '00:00:00', it means the record doesn't exist, so insert
            
            return f"INSERT INTO attendance (Empname, EmpCode_id, date, timein, timeout, breakout, breakin, totallateness, latecount, totalundertime, totalovertime, created_at, approveOT, absent, late, remarks,user_branchname) " \
                    f"VALUES ({Empname}, {EmpCode_id}, {date}, {timein}, {timeout}, {breakout}, {breakin}, {totallateness}, {latecount}, {totalundertime}, {totalovertime}, {created_at}, {approveOT}, {absent}, {late}, {remarks}, {user_branchname});"
        else:
            return f"UPDATE attendance SET " \
                f"timeout = {timeout}, " \
                f"breakout = {breakout}, " \
                f"breakin = {breakin}, " \
                f"totallateness = {totallateness}, " \
                f"latecount = {latecount}, " \
                f"totalundertime = {totalundertime}, " \
                f"totalovertime = {totalovertime}, " \
                f"approveOT = {approveOT}, " \
                f"absent = {absent}, " \
                f"late = {late}, " \
                f"remarks = {remarks} " \
                f"WHERE Empname = {Empname} AND EmpCode_id = {EmpCode_id} AND date = {date};"


    class Meta:
        db_table = 'attendance'





class temporay(models.Model):
    EmpCode = models.ForeignKey(Employee, on_delete=models.CASCADE, to_field='EmpCode', null=True)
    Empname = models.CharField(max_length=50, default = 'Unknown')
    date = models.DateField(default=date.today)
    timein_names = models.CharField(max_length=100,null=True,blank=True)
    timeout_names = models.CharField(max_length=100,null=True,blank=True)
    breakout_names = models.CharField(max_length=100,null=True,blank=True)
    breakin_names = models.CharField(max_length=100,null=True,blank=True)
    timein_timestamps = models.DateTimeField(null=True,blank=True)
    breakout_timestamps = models.DateTimeField(null=True,blank=True)
    breakin_timestamps = models.DateTimeField(null=True,blank=True)
    timeout_timestamps = models.DateTimeField(null=True,blank=True)
    afternoonBreakin_timestamps = models.DateTimeField(null=True,blank=True)
    afternoonTimeout_timestramps = models.DateTimeField(null=True,blank=True)
    login_status = models.CharField(max_length=100,null=True,blank=True)

    class Meta:
        db_table = 'temporay'





  

# class QRList(models.Model):
#     name = models.CharField(max_length=100,null=True)
#     qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)
    
#     class Meta:
#         db_table = 'qr_list'    
    
    

class RequestForm(models.Model):
    FormID = models.AutoField(primary_key=True)
    EmpCode = models.ForeignKey(Employee, on_delete = models.CASCADE, to_field = 'EmpCode', null = True)
    SelectRequest = models.CharField(max_length = 30)
    BeginTimeOff = models.DateTimeField()
    ConcludeTimeOff = models.DateTimeField()
    Range = models.CharField(max_length = 10,default='N/A')
    isApproved = models.BooleanField(default=False)
    Remarks = models.CharField(max_length = 100)
    created_at = models.DateTimeField(default=timezone.now)  
    date = models.DateField(default=date(2000, 1, 1))



class AttendanceCount(models.Model):
    EmpCode = models.ForeignKey(Employee, on_delete=models.CASCADE, to_field='EmpCode', null=True)
    Vacation = models.FloatField(default= 0)
    Sick = models.FloatField(default = 0)
    GracePeriod = models.IntegerField(default=15)
    last_grace_period_month  = models.DateTimeField(default=date(2024, 1, 1))
    last_leaves_year = models.DateField(default=date(2024, 1, 1))


class EmployeeStatus(models.Model):
    RequestForm = models.ForeignKey(RequestForm, on_delete=models.CASCADE, to_field= 'FormID', null=True) 
    RequestDate = models.DateField(default=date(2000, 1, 1))

