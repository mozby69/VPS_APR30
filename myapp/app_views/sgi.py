from django.shortcuts import render, redirect
import os
import cv2
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
import qrcode
from pyzbar.pyzbar import decode
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import numpy as np
import base64
from io import BytesIO
from myapp.models import DailyRecord
from myapp.models import temporay
from myapp.models import Employee
from myapp.models import AttendanceCount
from django.utils import timezone
import time
from datetime import timedelta,datetime,date,time
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.messages import get_messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LogoutView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse_lazy
from django.db.models import Q
import pytz
from django.contrib.auth import logout


@csrf_exempt
def fetch_messages_sgi(request):
    messages = get_messages(request)
    filtered_messages = [
        {'text': message.message, 'tags': message.tags} for message in messages if 'timein_09pm_06am' in message.tags
        or 'timeout_09pm_06am' in message.tags or 'timein_12pm_09pm' in message.tags or 'timeout_12pm_09pm' in message.tags
        or 'timeout_already_09pm_06am' in message.tags or 'timeout_12pm_09pm_already' in message.tags 
        or 'timein_06am_03pm' in message.tags or 'timeout_06am_03pm' in message.tags or 'timeout_06am_03pm_already' in message.tags
        or 'timein_730am_430pm' in message.tags or 'timeout_730am_430pm' in message.tags or 'timeout_730am_430pm_already' in message.tags
     
    
    ]
    return JsonResponse({'messages': filtered_messages})


#09pm - 06am
@csrf_exempt
def webcam_qr_code_scanner_sgi_09pm_06am(request):
    if request.method == 'POST':
        image_data = request.FILES['webcam_image_sgi'].read()
        decoded_objects = scan_qr_code_from_image_data(image_data)
        current_time = request.current_time
        current_date = date.today()

        if decoded_objects:
            EmpCode = decoded_objects[0].data.decode('utf-8')
            prac_time = current_time.strftime("%H:%M")
           

            if "20:00" <= prac_time <= "06:00":
                ResetGraceAndLeaves()
            
            
            # FOR TIMEIN
            employee_instance = Employee.objects.get(EmpCode=EmpCode)
            full_name = f"{employee_instance.Firstname} {employee_instance.Middlename} {employee_instance.Lastname}"

            if "17:00" <= prac_time <= "23:59": 
                existing_entry = DailyRecord.objects.filter(EmpCode_id=EmpCode,date=current_time.date()).first()
                if existing_entry is None: 
                    employee_instance = Employee.objects.get(EmpCode=EmpCode)
                    full_name = f"{employee_instance.Firstname} {employee_instance.Middlename} {employee_instance.Lastname}"
                    insertData_09pm_06am(EmpCode, current_time,employee_instance,request) 
                    yesterday = current_date - timedelta(days=1)
                    messages.success(request, f'TIME IN SUCCESSFULLY!<br> {full_name}', extra_tags='timein_09pm_06am')
                    return HttpResponseRedirect(request.path)
    
                

            #FOR TIMEOUT
            yesterday = current_date - timedelta(days=1)
            if "05:00" <= prac_time <= "10:00" and temporay.objects.filter(timein_names__isnull=False,EmpCode_id=EmpCode,date=yesterday).exists():
                    timeout_09pm_06am(EmpCode, current_time)   
                    temporay.objects.filter(EmpCode_id=EmpCode, date=yesterday).update(timeout_names=EmpCode,timeout_timestamps=current_time)
                    messages.success(request, f'TIME OUT SUCCESSFULLY <br>{full_name}', extra_tags='timeout_09pm_06am') 
                    return HttpResponseRedirect(request.path)


            return JsonResponse({"success": True, "EmpCode": EmpCode})
    return JsonResponse({"success": False, "error": "QR code not detected"})




@csrf_exempt
def ResetGraceAndLeaves():
        # Get the current date and time
        current_datetime = timezone.now()
        
        # Set the current date to the first day of the month
        current_month = current_datetime.replace(day=1).month
        current_year = current_datetime.year

        for attendance_count in AttendanceCount.objects.all():
            last_month = attendance_count.last_grace_period_month.month
            last_year = attendance_count.last_leaves_year.year

            if last_month != current_month:
                attendance_count.GracePeriod = 15
                attendance_count.last_grace_period_month = current_datetime.date()  # Update only when resetting grace period

            if last_year != current_year:
                internet_time = current_datetime.date()  # Use .date() to get only the date portion
                if attendance_count.EmpCode.EmployementDate is not None:
                    employment_date = attendance_count.EmpCode.EmployementDate
                    employment_years = (internet_time - employment_date).days // 365

                    leave_mapping = {1: 5, 2: 10, 3: 15}
                    vacation_days = leave_mapping.get(employment_years, 0)
                    sick_leave_days = leave_mapping.get(employment_years, 0)

                    attendance_count.Vacation = vacation_days
                    attendance_count.Sick = sick_leave_days

                    attendance_count.last_leaves_year = current_datetime.date()  # Use .date() to get only the date portion
                    attendance_count.save()







# @csrf_exempt
def count_lateness_intervals(lateness_duration):
    total_minutes = lateness_duration.total_seconds() // 60
    
    if total_minutes % 15 == 0:
        lateness_count = total_minutes // 15
    else:
        lateness_count = total_minutes // 15 + 1
    
    return int(lateness_count)


# @csrf_exempt
def insertData_09pm_06am(employee_number, current_time,employee_instance,request):
    branch_names = request.user.username
    formatted_time = current_time.strftime("%H:%M:%S")
    total_lateness = timedelta()
    fullname = f"{employee_instance.Firstname} {employee_instance.Middlename} {employee_instance.Lastname}"
    fixed_time = time(21, 1, 00)
    timein_datetime = current_time.time()

    if timein_datetime > fixed_time:
        time_difference = datetime.combine(current_time.date(), timein_datetime) - datetime.combine(current_time.date(), fixed_time)
        time_difference = max(time_difference, timedelta())
        total_lateness += time_difference

    hours, remainder = divmod(total_lateness.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    total_lateness_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    timein_status = "9PM-6AM"

    if total_lateness.total_seconds() > 0:
        
        DailyRecord.objects.create(
            EmpCode_id=employee_number,
            Empname=fullname,
            date=current_time.date(),
            totallateness=total_lateness_str,
            late = f"Late AM",
            timein=formatted_time,  # Use formatted_time here
            remarks = f"None ",
            user_branchname = branch_names,
            flex_time=timein_status,
        )
        temporay.objects.create(
        EmpCode_id=employee_number,
        Empname=fullname,
        date=current_time.date(),
        timein_names=employee_number,
        timein_timestamps=current_time,
        login_status=timein_status,
        )

    elif total_lateness >= timedelta(hours=2):
        formatted_time = formatted_time
        total_lateness = timedelta()
        hours, remainder = divmod(total_lateness.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        total_lateness_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        DailyRecord.objects.create(
            EmpCode_id=employee_number,
            Empname=fullname,
            date=current_time.date(),
            absent="Absent AM",
            timein=formatted_time,  
            breakout="00:00:00",
            remarks = "Late 2hrs for Timein",
            user_branchname = branch_names,
            flex_time=timein_status,
        )
        temporay.objects.create(
        EmpCode_id=employee_number,
        Empname=fullname,
        date=current_time.date(),
        timein_names=employee_number,
        timein_timestamps=current_time,
        breakout_names=employee_number,
        breakout_timestamps=current_time,
        login_status=timein_status,
        )
    else:
        # Deduct from grace period
        DailyRecord.objects.create(
            EmpCode_id=employee_number,
            Empname=fullname,
            date=current_time.date(),
            totallateness=total_lateness_str,
            timein=formatted_time,  # Use formatted_time here
            remarks = f"None ",
            user_branchname = branch_names,
            flex_time=timein_status,
        )
        temporay.objects.create(
        EmpCode_id=employee_number,
        Empname=fullname,
        date=current_time.date(),
        timein_names=employee_number,
        timein_timestamps=current_time,
        login_status=timein_status,
        )





# @csrf_exempt      
def timeout_09pm_06am(employee_number,current_time):
    formatted_time = current_time.strftime("%H:%M:%S")
    total_undertime = timedelta()

    if current_time:
        timeout_datetime = datetime.combine(current_time.date(),current_time.time())
        upper_bound_timeout = datetime.combine(current_time.date(), time(6, 00, 0))

        if timeout_datetime < upper_bound_timeout:
            time_difference_timeout = upper_bound_timeout - timeout_datetime
            time_difference_timeout = max(time_difference_timeout, timedelta())

            total_undertime += time_difference_timeout

        hours, remainder = divmod(total_undertime.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        total_undertime_str = f"{hours:02d}:{minutes:02d}" 
        current_date = date.today()
        yesterday = current_date - timedelta(days=1) 
   
        DailyRecord.objects.filter(timein__isnull=False,timeout__isnull=True, EmpCode_id=employee_number, date=yesterday).update(timeout=formatted_time,totalundertime=total_undertime_str)




# @csrf_exempt
def add_time_strings(time_str1, time_str2):
    h1, m1, s1 = map(int, time_str1.split(':'))
    h2, m2, s2 = map(int, time_str2.split(':'))

    total_seconds = (h1 + h2) * 3600 + (m1 + m2) * 60 + (s1 + s2)
    hours, remaining_seconds = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remaining_seconds, 60)

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def display_qr_list_sgi(request):
    current_date = date.today()
    yesterday = current_date - timedelta(days=1)
    if request.user.username == 'ADMIN' or request.user.username == 'MIS_XYRYL':
        attendances = DailyRecord.objects.filter(date__in=[current_date, yesterday]).order_by('-timeout', '-timein')
    else:
        user_branchname = request.user.username
        attendances = DailyRecord.objects.filter(date__in=[current_date, yesterday],user_branchname=user_branchname).order_by('-date','-timeout','-timein')
 

    def custom_sort(attendance):
        times = [attendance.timein, attendance.timeout]
        latest_time = max(filter(None, times), default=None)

        if latest_time is not None and isinstance(latest_time, str):
            latest_time = datetime.strptime(latest_time, '%H:%M:%S').time()

        return latest_time or datetime.min.time()

    sorted_attendances = sorted(attendances, key=custom_sort, reverse=True)

    data = [
        {
            'name': attendance.Empname,
            'timein': str(attendance.timein),
            'timeout': str(attendance.timeout),
            'date':str(attendance.date),
            
        } for attendance in sorted_attendances
    ]

    return JsonResponse({'attendances': data})





def scan_qr_code_from_image_data(image_data):
    nparr = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    decoded_objects = decode(gray)
    return decoded_objects



def main_sgi_page(request):
    branch_names = request.user.username
    context = {'branch_names':branch_names}
    return render(request, "myapp/sgi.html",context)






















#----------------------------------------------------------------------------------------------------------- 12PM TO 9PM





@csrf_exempt
def webcam_qr_code_scanner_sgi_12pm_09pm(request):
    if request.method == 'POST':
        image_data = request.FILES['webcam_image_sgi'].read()
        decoded_objects = scan_qr_code_from_image_data(image_data)
        current_time = request.current_time
        current_date = date.today()

        if decoded_objects:
            EmpCode = decoded_objects[0].data.decode('utf-8')
            prac_time = current_time.strftime("%H:%M")
           

            # if "12:00" <= prac_time <= "15:00":
            #     ResetGraceAndLeaves()
                #reset_value_GP(request)
            
            # FOR TIMEIN
            employee_instance = Employee.objects.get(EmpCode=EmpCode)
            full_name = f"{employee_instance.Firstname} {employee_instance.Middlename} {employee_instance.Lastname}"

            if "10:00" <= prac_time <= "15:59": 
                existing_entry = DailyRecord.objects.filter(EmpCode_id=EmpCode,date=current_time.date()).first()
                if existing_entry is None: 
                    employee_instance = Employee.objects.get(EmpCode=EmpCode)
                    full_name = f"{employee_instance.Firstname} {employee_instance.Middlename} {employee_instance.Lastname}"
                    insertData_12pm_09pm(EmpCode, current_time,employee_instance,request) 
                    #temporay.objects.filter(EmpCode_id=EmpCode,date=current_time.date()).create(login_status="timein_12pm_09pm",Empname=full_name,EmpCode_id=EmpCode,timein_names=EmpCode,timein_timestamps=current_time)
                    messages.success(request, f'TIME IN SUCCESSFULLY!<br> {full_name}', extra_tags='timein_12pm_09pm')
                    return HttpResponseRedirect(request.path)



            if "18:00" <= prac_time <= "24:59" and temporay.objects.filter(EmpCode_id=EmpCode, timein_names__isnull=False, timeout_names__isnull=True,date=current_time.date()).exists():
                existing_entry3 = temporay.objects.filter(EmpCode_id=EmpCode, date=current_time.date()).first()

                existing_entry_breakin_timestamps = existing_entry3.timein_timestamps.replace(tzinfo=timezone.utc)
                current_time = current_time.replace(tzinfo=timezone.utc)


                if current_time - existing_entry_breakin_timestamps >= timedelta(seconds=5):
                    timeout_12pm_09pm(EmpCode, current_time)
                    messages.success(request, f'TIME OUT SUCCESSFULLY<br>{full_name}', extra_tags='timeout_12pm_09pm')    
                    temporay.objects.filter(EmpCode_id=EmpCode, date=current_time.date()).update(timeout_names=EmpCode,timeout_timestamps=current_time)
                    return HttpResponseRedirect(request.path)
            
            if "18:00" <= prac_time <= "24:59" and temporay.objects.filter(Empname=full_name,
                                                                          timein_names__isnull=False,
                                                                          timeout_names__isnull=False,
                                                                          date=current_time.date()).exists():
                
                existing_entry7 = temporay.objects.filter(Empname=full_name, date=current_time.date()).first()
                existing_entry_breakin_timestamps = existing_entry7.timeout_timestamps.replace(tzinfo=timezone.utc)
                current_time = current_time.replace(tzinfo=timezone.utc)

                if current_time - existing_entry_breakin_timestamps >= timedelta(seconds=6):
                    messages.error(request, f'TIMEOUT ALREADY!<br>{full_name}', extra_tags='timeout_12pm_09pm_already')
                    return HttpResponseRedirect(request.path)

            return JsonResponse({"success": True, "EmpCode": EmpCode})
    return JsonResponse({"success": False, "error": "QR code not detected"})



# def reset_value_GP(request):
#     current_day = datetime.now().day
#     current_month = datetime.now().month
#     first_day_of_month = datetime(datetime.now().year, current_month, 1)
    
#     if first_day_of_month.weekday() >= 5: 
#         first_day_of_month += timedelta(days=(7 - first_day_of_month.weekday()))

#     if datetime.now().day == first_day_of_month.day:
#         AttendanceCount.objects.update(GracePeriod=15)
#         print("SUCCESS RESET GRACE PERIOD ********************")


@csrf_exempt
def insertData_12pm_09pm(employee_number, current_time,employee_instance,request):
    branch_names = request.user.username
    formatted_time = current_time.strftime("%H:%M:%S")
    total_lateness = timedelta()
    fullname = f"{employee_instance.Firstname} {employee_instance.Middlename} {employee_instance.Lastname}"
    fixed_time = time(12, 1, 00)
    timein_datetime = current_time.time()

    if timein_datetime > fixed_time:
        time_difference = datetime.combine(current_time.date(), timein_datetime) - datetime.combine(current_time.date(), fixed_time)
        time_difference = max(time_difference, timedelta())
        total_lateness += time_difference

    hours, remainder = divmod(total_lateness.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    total_lateness_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    timein_status = "12PM-9PM"

    if total_lateness.total_seconds() > 0:
        DailyRecord.objects.create(
            EmpCode_id=employee_number,
            Empname=fullname,
            date=current_time.date(),
            totallateness=total_lateness_str,
            late = f"Late AM",
            timein=formatted_time,  # Use formatted_time here
            remarks = f"None ",
            user_branchname = branch_names,
            flex_time = timein_status,
        )
        temporay.objects.create(
        EmpCode_id=employee_number,
        Empname=fullname,
        date=current_time.date(),
        timein_names=employee_number,
        timein_timestamps=current_time,
        login_status=timein_status,
   
        )

    elif total_lateness >= timedelta(hours=2):
        formatted_time = formatted_time
        total_lateness = timedelta()
        hours, remainder = divmod(total_lateness.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        total_lateness_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        DailyRecord.objects.create(
            EmpCode_id=employee_number,
            Empname=fullname,
            date=current_time.date(),
            absent="Absent AM",
            timein=formatted_time,  
            breakout="00:00:00",
            remarks = "Late 2hrs for Timein",
            user_branchname = branch_names,
            flex_time = timein_status,
        )
        temporay.objects.create(
        EmpCode_id=employee_number,
        Empname=fullname,
        date=current_time.date(),
        timein_names=employee_number,
        timein_timestamps=current_time,
        breakout_names=employee_number,
        breakout_timestamps=current_time,
        login_status=timein_status,
        )
    else:
        # Deduct from grace period
        DailyRecord.objects.create(
            EmpCode_id=employee_number,
            Empname=fullname,
            date=current_time.date(),
            totallateness=total_lateness_str,
            timein=formatted_time,  # Use formatted_time here
            remarks = f"None ",
            user_branchname = branch_names,
            flex_time = timein_status,
        )
        temporay.objects.create(
        EmpCode_id=employee_number,
        Empname=fullname,
        date=current_time.date(),
        timein_names=employee_number,
        timein_timestamps=current_time,
        login_status=timein_status, 
        )




@csrf_exempt      
def timeout_12pm_09pm(employee_number,current_time):
    formatted_time = current_time.strftime("%H:%M:%S")
    total_undertime = timedelta()

    if current_time:
        timeout_datetime = datetime.combine(current_time.date(),current_time.time())
        upper_bound_timeout = datetime.combine(current_time.date(), time(21, 00, 0))

        if timeout_datetime < upper_bound_timeout:
            time_difference_timeout = upper_bound_timeout - timeout_datetime
            time_difference_timeout = max(time_difference_timeout, timedelta())

            total_undertime += time_difference_timeout

        hours, remainder = divmod(total_undertime.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        total_undertime_str = f"{hours:02d}:{minutes:02d}"    
        DailyRecord.objects.filter(timein__isnull=False,timeout__isnull=True, EmpCode_id=employee_number, date=current_time.date()).update(timeout=formatted_time,totalundertime=total_undertime_str)



















        #----------------------------------------------------------------------------------------------------------- 06AM TO 3PM

@csrf_exempt
def webcam_qr_code_scanner_sgi_06am_03pm(request):
    if request.method == 'POST':
        image_data = request.FILES['webcam_image_sgi'].read()
        decoded_objects = scan_qr_code_from_image_data(image_data)
        current_time = request.current_time
        current_date = date.today()

        if decoded_objects:
            EmpCode = decoded_objects[0].data.decode('utf-8')
            prac_time = current_time.strftime("%H:%M")
           
            
            # FOR TIMEIN
            employee_instance = Employee.objects.get(EmpCode=EmpCode)
            full_name = f"{employee_instance.Firstname} {employee_instance.Middlename} {employee_instance.Lastname}"

            if "04:00" <= prac_time <= "12:00": 
                existing_entry = DailyRecord.objects.filter(EmpCode_id=EmpCode,date=current_time.date()).first()
                if existing_entry is None: 
                    employee_instance = Employee.objects.get(EmpCode=EmpCode)
                    full_name = f"{employee_instance.Firstname} {employee_instance.Middlename} {employee_instance.Lastname}"
                    insertData_06am_03pm(EmpCode, current_time,employee_instance,request) 
                    #temporay.objects.filter(EmpCode_id=EmpCode,date=current_time.date()).create(login_status="timein_12pm_09pm",Empname=full_name,EmpCode_id=EmpCode,timein_names=EmpCode,timein_timestamps=current_time)
                    messages.success(request, f'TIME IN SUCCESSFULLY!<br> {full_name}', extra_tags='timein_06am_03pm')
                    return HttpResponseRedirect(request.path)



            if "13:00" <= prac_time <= "22:59" and temporay.objects.filter(login_status="6AM-3PM",EmpCode_id=EmpCode, timein_names__isnull=False, timeout_names__isnull=True,date=current_time.date()).exists():
                existing_entry3 = temporay.objects.filter(EmpCode_id=EmpCode, date=current_time.date()).first()

                existing_entry_breakin_timestamps = existing_entry3.timein_timestamps.replace(tzinfo=timezone.utc)
                current_time = current_time.replace(tzinfo=timezone.utc)


                if current_time - existing_entry_breakin_timestamps >= timedelta(seconds=2):
                    timeout_06am_03pm(EmpCode, current_time)
                    messages.success(request, f'TIME OUT SUCCESSFULLY<br>{full_name}', extra_tags='timeout_06am_03pm')    
                    temporay.objects.filter(EmpCode_id=EmpCode, date=current_time.date()).update(timeout_names=EmpCode,timeout_timestamps=current_time)
                    return HttpResponseRedirect(request.path)
            
            if "13:00" <= prac_time <= "22:59" and temporay.objects.filter(Empname=full_name,
                                                                          timein_names__isnull=False,
                                                                          timeout_names__isnull=False,
                                                                          date=current_time.date()).exists():
                
                existing_entry7 = temporay.objects.filter(Empname=full_name, date=current_time.date()).first()
                existing_entry_breakin_timestamps = existing_entry7.timeout_timestamps.replace(tzinfo=timezone.utc)
                current_time = current_time.replace(tzinfo=timezone.utc)

                if current_time - existing_entry_breakin_timestamps >= timedelta(seconds=2):
                    messages.error(request, f'TIMEOUT ALREADY!<br>{full_name}', extra_tags='timeout_06am_03pm_already')
                    return HttpResponseRedirect(request.path)

            return JsonResponse({"success": True, "EmpCode": EmpCode})
    return JsonResponse({"success": False, "error": "QR code not detected"})




@csrf_exempt
def insertData_06am_03pm(employee_number, current_time,employee_instance,request):
    branch_names = request.user.username
    formatted_time = current_time.strftime("%H:%M:%S")
    total_lateness = timedelta()
    fullname = f"{employee_instance.Firstname} {employee_instance.Middlename} {employee_instance.Lastname}"
    fixed_time = time(6, 1, 00)
    timein_datetime = current_time.time()

    if timein_datetime > fixed_time:
        time_difference = datetime.combine(current_time.date(), timein_datetime) - datetime.combine(current_time.date(), fixed_time)
        time_difference = max(time_difference, timedelta())
        total_lateness += time_difference

    hours, remainder = divmod(total_lateness.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    total_lateness_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    timein_status = "6AM-3PM"

    if total_lateness.total_seconds() > 0:
        DailyRecord.objects.create(
            EmpCode_id=employee_number,
            Empname=fullname,
            date=current_time.date(),
            totallateness=total_lateness_str,
            late = f"Late AM",
            timein=formatted_time,  # Use formatted_time here
            remarks = f"None ",
            user_branchname = branch_names,
            flex_time = timein_status,
        )
        temporay.objects.create(
        EmpCode_id=employee_number,
        Empname=fullname,
        date=current_time.date(),
        timein_names=employee_number,
        timein_timestamps=current_time,
        login_status=timein_status,
        )

    elif total_lateness >= timedelta(hours=2):
        formatted_time = formatted_time
        total_lateness = timedelta()
        hours, remainder = divmod(total_lateness.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        total_lateness_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        DailyRecord.objects.create(
            EmpCode_id=employee_number,
            Empname=fullname,
            date=current_time.date(),
            absent="Absent AM",
            timein=formatted_time,  
            breakout="00:00:00",
            remarks = "Late 2hrs for Timein",
            user_branchname = branch_names,
            flex_time = timein_status,

        )
        temporay.objects.create(
        EmpCode_id=employee_number,
        Empname=fullname,
        date=current_time.date(),
        timein_names=employee_number,
        timein_timestamps=current_time,
        breakout_names=employee_number,
        breakout_timestamps=current_time,
        login_status=timein_status,
        )
    else:
        # Deduct from grace period
        DailyRecord.objects.create(
            EmpCode_id=employee_number,
            Empname=fullname,
            date=current_time.date(),
            totallateness=total_lateness_str,
            timein=formatted_time,  # Use formatted_time here
            remarks = f"None ",
            user_branchname = branch_names,
            flex_time = timein_status,
        )
        temporay.objects.create(
        EmpCode_id=employee_number,
        Empname=fullname,
        date=current_time.date(),
        timein_names=employee_number,
        timein_timestamps=current_time,
        login_status=timein_status,
        )




@csrf_exempt      
def timeout_06am_03pm(employee_number,current_time):
    formatted_time = current_time.strftime("%H:%M:%S")
    total_undertime = timedelta()

    if current_time:
        timeout_datetime = datetime.combine(current_time.date(),current_time.time())
        upper_bound_timeout = datetime.combine(current_time.date(), time(15, 00, 0))

        if timeout_datetime < upper_bound_timeout:
            time_difference_timeout = upper_bound_timeout - timeout_datetime
            time_difference_timeout = max(time_difference_timeout, timedelta())

            total_undertime += time_difference_timeout

        hours, remainder = divmod(total_undertime.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        total_undertime_str = f"{hours:02d}:{minutes:02d}"    
        DailyRecord.objects.filter(timein__isnull=False,timeout__isnull=True, EmpCode_id=employee_number, date=current_time.date()).update(timeout=formatted_time,totalundertime=total_undertime_str)


























        #--------------------------------------------------------------------------------------------------------7:30AM TO 4:30PM

@csrf_exempt
def webcam_qr_code_scanner_sgi_730am_430pm(request):
    if request.method == 'POST':
        image_data = request.FILES['webcam_image_sgi'].read()
        decoded_objects = scan_qr_code_from_image_data(image_data)
        current_time = request.current_time
        current_date = date.today()

        if decoded_objects:
            EmpCode = decoded_objects[0].data.decode('utf-8')
            prac_time = current_time.strftime("%H:%M")
           
            
            # FOR TIMEIN
            employee_instance = Employee.objects.get(EmpCode=EmpCode)
            full_name = f"{employee_instance.Firstname} {employee_instance.Middlename} {employee_instance.Lastname}"

            if "04:00" <= prac_time <= "12:00": 
                existing_entry = DailyRecord.objects.filter(EmpCode_id=EmpCode,date=current_time.date()).first()
                if existing_entry is None: 
                    employee_instance = Employee.objects.get(EmpCode=EmpCode)
                    full_name = f"{employee_instance.Firstname} {employee_instance.Middlename} {employee_instance.Lastname}"
                    insertData_730am_430pm(EmpCode, current_time,employee_instance,request) 
                    #temporay.objects.filter(EmpCode_id=EmpCode,date=current_time.date()).create(login_status="timein_12pm_09pm",Empname=full_name,EmpCode_id=EmpCode,timein_names=EmpCode,timein_timestamps=current_time)
                    messages.success(request, f'TIME IN SUCCESSFULLY!<br> {full_name}', extra_tags='timein_730am_430pm')
                    return HttpResponseRedirect(request.path)



            if "14:00" <= prac_time <= "22:59" and temporay.objects.filter(login_status="7AM-4PM",EmpCode_id=EmpCode, timein_names__isnull=False, timeout_names__isnull=True,date=current_time.date()).exists():
                existing_entry3 = temporay.objects.filter(EmpCode_id=EmpCode, date=current_time.date()).first()

                existing_entry_breakin_timestamps = existing_entry3.timein_timestamps.replace(tzinfo=timezone.utc)
                current_time = current_time.replace(tzinfo=timezone.utc)


                if current_time - existing_entry_breakin_timestamps >= timedelta(seconds=2):
                    timeout_730am_430pm(EmpCode, current_time)
                    messages.success(request, f'TIME OUT SUCCESSFULLY<br>{full_name}', extra_tags='timeout_730am_430pm') 
                    temporay.objects.filter(EmpCode_id=EmpCode, date=current_time.date()).update(timeout_names=EmpCode,timeout_timestamps=current_time)
                    return HttpResponseRedirect(request.path)
            
            if "13:00" <= prac_time <= "22:59" and temporay.objects.filter(Empname=full_name,
                                                                          timein_names__isnull=False,
                                                                          timeout_names__isnull=False,
                                                                          date=current_time.date()).exists():
                
                existing_entry7 = temporay.objects.filter(Empname=full_name, date=current_time.date()).first()
                existing_entry_breakin_timestamps = existing_entry7.timeout_timestamps.replace(tzinfo=timezone.utc)
                current_time = current_time.replace(tzinfo=timezone.utc)

                if current_time - existing_entry_breakin_timestamps >= timedelta(seconds=2):
                    messages.error(request, f'TIMEOUT ALREADY!<br>{full_name}', extra_tags='timeout_730am_430pm_already')
                    return HttpResponseRedirect(request.path)

            return JsonResponse({"success": True, "EmpCode": EmpCode})
    return JsonResponse({"success": False, "error": "QR code not detected"})




@csrf_exempt
def insertData_730am_430pm(employee_number, current_time,employee_instance,request):
    branch_names = request.user.username
    formatted_time = current_time.strftime("%H:%M:%S")
    total_lateness = timedelta()
    fullname = f"{employee_instance.Firstname} {employee_instance.Middlename} {employee_instance.Lastname}"
    fixed_time = time(7, 31, 00)
    timein_datetime = current_time.time()

    if timein_datetime > fixed_time:
        time_difference = datetime.combine(current_time.date(), timein_datetime) - datetime.combine(current_time.date(), fixed_time)
        time_difference = max(time_difference, timedelta())
        total_lateness += time_difference

    hours, remainder = divmod(total_lateness.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    total_lateness_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    timein_status = "7AM-4PM"
  

    if total_lateness.total_seconds() > 0:
        DailyRecord.objects.create(
            EmpCode_id=employee_number,
            Empname=fullname,
            date=current_time.date(),
            totallateness=total_lateness_str,
            late = f"Late AM",
            timein=formatted_time,  # Use formatted_time here
            remarks = f"None ",
            user_branchname = branch_names,
            flex_time = timein_status,
        )
        temporay.objects.create(
        EmpCode_id=employee_number,
        Empname=fullname,
        date=current_time.date(),
        timein_names=employee_number,
        timein_timestamps=current_time,
        login_status =timein_status,
        )

    elif total_lateness >= timedelta(hours=2):
        formatted_time = formatted_time
        total_lateness = timedelta()
        hours, remainder = divmod(total_lateness.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        total_lateness_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        DailyRecord.objects.create(
            EmpCode_id=employee_number,
            Empname=fullname,
            date=current_time.date(),
            absent="Absent AM",
            timein=formatted_time,  
            breakout="00:00:00",
            remarks = "Late 2hrs for Timein",
            user_branchname = branch_names,
            flex_time = timein_status,
            
        )
        temporay.objects.create(
        EmpCode_id=employee_number,
        Empname=fullname,
        date=current_time.date(),
        timein_names=employee_number,
        timein_timestamps=current_time,
        breakout_names=employee_number,
        breakout_timestamps=current_time,
        login_status =timein_status,
        )
    else:
        # Deduct from grace period
        DailyRecord.objects.create(
            EmpCode_id=employee_number,
            Empname=fullname,
            date=current_time.date(),
            totallateness=total_lateness_str,
            timein=formatted_time,  # Use formatted_time here
            remarks = f"None ",
            user_branchname = branch_names,
            flex_time = timein_status,
        )
        temporay.objects.create(
        EmpCode_id=employee_number,
        Empname=fullname,
        date=current_time.date(),
        timein_names=employee_number,
        timein_timestamps=current_time,
        login_status =timein_status,
        )




@csrf_exempt      
def timeout_730am_430pm(employee_number,current_time):
    formatted_time = current_time.strftime("%H:%M:%S")
    total_undertime = timedelta()

    if current_time:
        timeout_datetime = datetime.combine(current_time.date(),current_time.time())
        upper_bound_timeout = datetime.combine(current_time.date(), time(16, 30, 0))

        if timeout_datetime < upper_bound_timeout:
            time_difference_timeout = upper_bound_timeout - timeout_datetime
            time_difference_timeout = max(time_difference_timeout, timedelta())

            total_undertime += time_difference_timeout

        hours, remainder = divmod(total_undertime.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        total_undertime_str = f"{hours:02d}:{minutes:02d}"    
        DailyRecord.objects.filter(timein__isnull=False,timeout__isnull=True, EmpCode_id=employee_number, date=current_time.date()).update(timeout=formatted_time,totalundertime=total_undertime_str)
