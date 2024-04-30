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
def fetch_messages_utility_ten(request):
  
    messages = get_messages(request)
    filtered_messages = [
        {'text': message.message, 'tags': message.tags} for message in messages if 'timein_ten' in message.tags
        or 'breakout_ten' in message.tags or 'breakin_ten' in message.tags or 'timeout_ten' in message.tags
        or 'no_bibo_utility_ten' in message.tags or 'breakin_already_ten' in message.tags or 'timeout_already_ten' in message.tags 
    
    ]
    return JsonResponse({'messages': filtered_messages})


@csrf_exempt
def webcam_qr_code_scanner_serviamus_utility_10(request):
    if request.method == 'POST':
        image_data = request.FILES['webcam_image_utility'].read()
        decoded_objects = scan_qr_code_from_image_data(image_data)
        current_time = request.current_time

        if decoded_objects:
            EmpCode = decoded_objects[0].data.decode('utf-8')
            prac_time = current_time.strftime("%H:%M")
           

            # FOR TIMEIN
            if "04:00" <= prac_time <= "09:59":
                # deleteTable()
                ResetGraceAndLeaves()
            
            
            employee_instance = Employee.objects.get(EmpCode=EmpCode)
            full_name = f"{employee_instance.Firstname} {employee_instance.Middlename} {employee_instance.Lastname}"

            if "04:00" <= prac_time <= "09:59": 
                existing_entry = DailyRecord.objects.filter(EmpCode_id=EmpCode,date=current_time.date()).first()
                if existing_entry is None: 
                    employee_instance = Employee.objects.get(EmpCode=EmpCode)
                    full_name = f"{employee_instance.Firstname} {employee_instance.Middlename} {employee_instance.Lastname}"
                    insertData(EmpCode, current_time,employee_instance,request) 
                    #temporay.objects.filter(EmpCode_id=EmpCode,date=current_time.date()).create(login_status="breakin_10-12",Empname=full_name,EmpCode_id=EmpCode,timein_names=EmpCode,timein_timestamps=current_time)
                    messages.success(request, f'TIME IN SUCCESSFULLY!<br> {full_name}', extra_tags='timein_ten')
                    return HttpResponseRedirect(request.path)

      
            #FOR BREAKOUT
            if "10:00" <= prac_time <= "14:00" and temporay.objects.filter(login_status="breakin_10-12",EmpCode_id=EmpCode, timein_names__isnull=False, breakout_names__isnull=True, date=current_time.date()).exists():
                existing_entry = temporay.objects.filter(EmpCode_id=EmpCode, date=current_time.date()).first()
                
                existing_entry_timein_timestamps = existing_entry.timein_timestamps.replace(tzinfo=timezone.utc)
                current_time = current_time.replace(tzinfo=timezone.utc)

                
                if current_time - existing_entry_timein_timestamps >= timedelta(seconds=5):
                    breakout(EmpCode, current_time)  
                    messages.success(request, f'BREAK OUT SUCCESSFULLY<br>{full_name}', extra_tags='breakout_ten')
                    temporay.objects.filter(EmpCode_id=EmpCode, date=current_time.date()).update(breakout_names=EmpCode,breakout_timestamps=current_time)
                    return HttpResponseRedirect(request.path)
    
             
            
            #FOR BREAKIN
            if "10:00" <= prac_time <= "14:00" and temporay.objects.filter(login_status="breakin_10-12",EmpCode_id=EmpCode, timein_names__isnull=False, breakout_names__isnull=False,breakin_names__isnull=True, date=current_time.date()).exists():
                existing_entry2 = temporay.objects.filter(EmpCode_id=EmpCode, date=current_time.date()).first()
      
                existing_entry_breakout_timestamps = existing_entry2.breakout_timestamps.replace(tzinfo=timezone.utc)
                current_time = current_time.replace(tzinfo=timezone.utc)

                if current_time - existing_entry_breakout_timestamps >= timedelta(seconds=8):
                    employee_instance = Employee.objects.get(EmpCode=EmpCode)
                    breakin(EmpCode, current_time,employee_instance)
                    messages.success(request, f'BREAKIN SUCCESSFULLY!<br> {full_name}', extra_tags='breakin_ten')  
                    temporay.objects.filter(EmpCode_id=EmpCode, date=current_time.date()).update(breakin_names=EmpCode,breakin_timestamps=current_time)
                    return HttpResponseRedirect(request.path)
            

              # IF BREAKIN IS ALREADY INSERTED
            if "10:00" <= prac_time <= "14:00" and temporay.objects.filter(Empname=full_name,
                                                                          timein_names__isnull=False,
                                                                          breakout_names__isnull=False,
                                                                          breakin_names__isnull=False,
                                                                          timeout_names__isnull=True,
                                                                          login_status="breakin_10-12",
                                                                          date=current_time.date()).exists():
                existing_entry3 = temporay.objects.filter(Empname=full_name, date=current_time.date()).first()

                existing_entry_breakin_timestamps = existing_entry3.breakin_timestamps.replace(tzinfo=timezone.utc)
                current_time = current_time.replace(tzinfo=timezone.utc)

                if current_time - existing_entry_breakin_timestamps >= timedelta(seconds=8):
                    messages.success(request, f'BREAK IN ALREADY<br>{full_name}', extra_tags='breakin_already_ten')
                    return HttpResponseRedirect(request.path)


            #FOR TIMEOUT
            if "17:00" <= prac_time <= "23:59" and temporay.objects.filter(login_status="breakin_10-12",EmpCode_id=EmpCode, timein_names__isnull=False, breakout_names__isnull=False,breakin_names__isnull=False, timeout_names__isnull=True,date=current_time.date()).exists():
                existing_entry3 = temporay.objects.filter(EmpCode_id=EmpCode, date=current_time.date()).first()

                existing_entry_breakin_timestamps = existing_entry3.breakin_timestamps.replace(tzinfo=timezone.utc)
                current_time = current_time.replace(tzinfo=timezone.utc)


                if current_time - existing_entry_breakin_timestamps >= timedelta(seconds=5):
                    timeout(EmpCode, current_time)
                    messages.success(request, f'TIME OUT SUCCESSFULLY<br>{full_name}', extra_tags='timeout_ten')    
                    temporay.objects.filter(EmpCode_id=EmpCode, date=current_time.date()).update(timeout_names=EmpCode,timeout_timestamps=current_time)
                    return HttpResponseRedirect(request.path)
            
             # IF TIMEOUT IS ALREADY INSERTED
            if "17:00" <= prac_time <= "23:59" and temporay.objects.filter(Empname=full_name,
                                                                          timein_names__isnull=False,
                                                                          breakout_names__isnull=False,
                                                                          breakin_names__isnull=False,
                                                                          timeout_names__isnull=False,
                                                                          date=current_time.date()).exists():
                existing_entry7 = temporay.objects.filter(Empname=full_name, date=current_time.date()).first()
                existing_entry_breakin_timestamps = existing_entry7.timeout_timestamps.replace(tzinfo=timezone.utc)
                current_time = current_time.replace(tzinfo=timezone.utc)

                if current_time - existing_entry_breakin_timestamps >= timedelta(seconds=6):
                    messages.success(request, f'TIMEOUT ALREADY!<br>{full_name}', extra_tags='timeout_already_ten')
                    return HttpResponseRedirect(request.path)

        
            if "17:01" <= prac_time <= "23:59" and temporay.objects.filter(Q(breakin_names__isnull=True) | Q(breakout_names__isnull=True), EmpCode_id=EmpCode,timein_names__isnull=False, date=current_time.date()).exists():
                nobreak_out_in(EmpCode, current_time)
                messages.success(request, f'NO BREAKIN OR BREAKOUT!<br>{full_name}', extra_tags='no_bibo_utility_ten')
                temporay.objects.filter(EmpCode_id=EmpCode, date=current_time.date()).update(timein_names=EmpCode,timeout_timestamps=current_time)
                return HttpResponseRedirect(request.path)


            #if login afternoon / HALF DAY
            if "10:00" <= prac_time <= "23:59":     
                employee_instance = Employee.objects.get(EmpCode=EmpCode)
                existing_entry = DailyRecord.objects.filter(EmpCode_id=EmpCode,date=current_time.date()).first()
                if existing_entry is None: 
                    afternoonBreakIn(EmpCode, current_time,employee_instance,request)      
                    temporay.objects.filter(EmpCode_id=EmpCode,date=current_time.date()).create(EmpCode_id=EmpCode,Empname=EmpCode,breakin_names=EmpCode,afternoonBreakin_timestamps=current_time)
        
              

            if "17:00" <= prac_time <= "23:59" and temporay.objects.filter(EmpCode_id=EmpCode, timein_names__isnull=True, breakin_names__isnull=False, timeout_names__isnull=True, date=current_time.date()).exists():
                existing_entry = temporay.objects.filter(EmpCode_id=EmpCode, date=current_time.date()).first()
                
                existing_entry_breakin_timestamps = existing_entry.afternoonBreakin_timestamps.replace(tzinfo=timezone.utc)
                current_time = current_time.replace(tzinfo=timezone.utc)

                
                if current_time - existing_entry_breakin_timestamps >= timedelta(seconds=15):
                    afternoonTimeout(EmpCode, current_time)  
                    temporay.objects.filter(EmpCode_id=EmpCode, date=current_time.date()).update(timeout_names=EmpCode,afternoonTimeout_timestramps=current_time)
    

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
def afternoonBreakIn(employee_number,current_time,employee_instance, request):
    branch_names = request.user.username
    formatted_time = current_time.strftime("%H:%M:%S")
    total_lateness = timedelta()

    fixed_time = time(10, 00, 0)
    timein_datetime = current_time.time()
    fullname = f"{employee_instance.Firstname} {employee_instance.Middlename} {employee_instance.Lastname}"


    if timein_datetime > fixed_time:
        time_difference = datetime.combine(current_time.date(), timein_datetime) - datetime.combine(current_time.date(), fixed_time)
        time_difference = max(time_difference, timedelta())
        total_lateness += time_difference

    hours, remainder = divmod(total_lateness.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    lateness_count = count_lateness_intervals(total_lateness)
    total_lateness_str = f"{hours:02d}:{minutes:02d}"
    total_lateness_count_str = lateness_count

    attendance_count, created = AttendanceCount.objects.get_or_create(EmpCode=employee_instance)

    current_grace_period = timedelta(minutes=attendance_count.GracePeriod)

    existing_entry = DailyRecord.objects.filter(EmpCode_id=employee_number,date=current_time.date()).first()
    
    if total_lateness.total_seconds() > current_grace_period.total_seconds():
        # If lateness is 2 hours or more, set formatted_time to "00:00:00"
        if total_lateness >= timedelta(hours=2):
            formatted_time = formatted_time
            total_lateness = timedelta()
            hours, remainder = divmod(total_lateness.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            lateness_count = count_lateness_intervals(total_lateness)
            total_lateness_str = f"{hours:02d}:{minutes:02d}"
            total_lateness_count_str = lateness_count

            if existing_entry: 
                existing_entry.breakin = formatted_time
                existing_entry.timeout = "00:00:00"
                existing_entry.remarks = "Late 2hrs from AM-PM (Absent)"
                existing_entry.absent = "Absent"
                existing_entry.save()

            else:
                # Mark as absent AM
                DailyRecord.objects.create(
                    EmpCode_id=employee_number,
                    Empname=fullname,
                    date=current_time.date(),
                    timein="00:00:00",
                    breakout="00:00:00",
                    absent="Absent",
                    breakin=formatted_time,  # Use formatted_time here
                    timeout="00:00:00",
                    remarks = "Late 2hrs for Breakin",
                    user_branchname = branch_names,
                    flex_time="UTIshiftA",
                )
                temporay.objects.create(
                    EmpCode_id=employee_number,
                    Empname=fullname,
                    date=current_time.date(),
                    breakin_names=employee_number,
                    afternoonBreakin_timestamps=current_time,
                    timeout_names=employee_number,
                    afternoonTimeout_timestramps=current_time,
                    login_status="breakin 10",
                )

        else:
            new_grace_period = timedelta(minutes=0)
            lateness_count = count_lateness_intervals(total_lateness)
            total_lateness_count_str = lateness_count
    else:
        new_grace_period = current_grace_period - total_lateness

    attendance_count.GracePeriod = new_grace_period.total_seconds() // 60
    attendance_count.save()


    if existing_entry is not None and existing_entry.absent == "Absent AM":
    # Update the existing entry's break-in time
        existing_entry.breakin = formatted_time
        existing_entry.remarks = f"Late 2hrs Timein, Grace {new_grace_period}"

        if new_grace_period.total_seconds() == 0 and total_lateness > timedelta(minutes=0):
            existing_entry.late = "Late PM"
            existing_entry.latecount = total_lateness_count_str
            existing_entry.totallateness = total_lateness_str
            existing_entry.breakin = formatted_time
            existing_entry.remarks = f"Late 2hrs Timein, Grace {new_grace_period}"
            
        elif total_lateness > timedelta(minutes= 0):
            existing_entry.late = "Late PM"
            existing_entry.totallateness = total_lateness_str
            existing_entry.breakin = formatted_time
            existing_entry.remarks = f"Late 2hrs Timein, Grace {new_grace_period}"



    else:
        # Create a new entry if the condition is not met
        if new_grace_period.total_seconds() == 0 and total_lateness > timedelta(minutes=0):

            DailyRecord.objects.create(
                EmpCode_id=employee_number,
                Empname=fullname,
                date=current_time.date(),
                timein="00:00:00",
                breakout="00:00:00",
                late="Late PM",
                absent="Absent AM",
                totallateness=total_lateness_str,
                latecount=total_lateness_count_str,
                breakin=formatted_time,
                remarks = f"Remaining Grace {new_grace_period} da",
                user_branchname = branch_names,
                flex_time="UTIshiftA",
            )
            temporay.objects.create(
                EmpCode_id=employee_number,
                Empname=fullname,
                date=current_time.date(),
                timein_names=employee_number,
                timein_timestamps=current_time,
                breakout_names=employee_number,
                breakout_timestamps=current_time,
                breakin_names = employee_number,
                breakin_timestamps = current_time,
                login_status="breakin 10",
            )
        elif total_lateness > timedelta(minutes=0):
            DailyRecord.objects.create(
                EmpCode_id=employee_number,
                Empname=fullname,
                date=current_time.date(),
                timein="00:00:00",
                breakout="00:00:00",
                late="Late PM",
                absent="Absent AM",
                totallateness=total_lateness_str,
                breakin=formatted_time,
                remarks = f"Remaining Grace {new_grace_period} w",
                user_branchname = branch_names,
                flex_time="UTIshiftA",
            )
            temporay.objects.create(
                EmpCode_id=employee_number,
                Empname=fullname,
                date=current_time.date(),
                timein_names=employee_number,
                timein_timestamps=current_time,
                breakout_names=employee_number,
                breakout_timestamps=current_time,
                breakin_names = employee_number,
                breakin_timestamps = current_time,
                login_status="breakin 10",
            )
        else:
            # Deduct from grace period
            DailyRecord.objects.create(
                EmpCode_id=employee_number,
                Empname=fullname,
                date=current_time.date(),
                totallateness=total_lateness_str,
                absent="Absent AM",
                timein="00:00:00",
                breakout="00:00:00",
                breakin=formatted_time,
                remarks = f"Remaining Grace {new_grace_period} e",
                user_branchname = branch_names,
                flex_time="UTIshiftA",
            )
            temporay.objects.create(
                EmpCode_id=employee_number,
                Empname=fullname,
                date=current_time.date(),
                timein_names=employee_number,
                timein_timestamps=current_time,
                breakout_names=employee_number,
                breakout_timestamps=current_time,
                breakin_names = employee_number,
                breakin_timestamps = current_time,
                login_status="breakin 10",
            )
    existing_entry.save()

        


# @csrf_exempt
def afternoonTimeout(employee_number,current_time):
    formatted_time = current_time.strftime("%H:%M:%S")
    DailyRecord.objects.filter(EmpCode_id=employee_number,breakin__isnull=False,date=current_time.date()).update(timeout=formatted_time)


# @csrf_exempt
def breakout(employee_number, current_time):
    formatted_time = current_time.strftime("%H:%M:%S")
    total_undertime = timedelta()

    # Check if there is an existing breakout value
    existing_entry = DailyRecord.objects.filter(
        timein__isnull=False,
        breakout__isnull=False,  # Check if breakout is not null
        EmpCode_id=employee_number,
        date=current_time.date()
    ).first()

    if existing_entry is not None and existing_entry.breakout != "00:00:00":
        # If breakout has a value, skip the update
        return

    breakout_datetime = datetime.combine(current_time.date(), current_time.time())
    upper_bound_breakout = datetime.combine(current_time.date(), time(10, 00, 0))

    if breakout_datetime < upper_bound_breakout:
        time_difference_breakout = upper_bound_breakout - breakout_datetime
        time_difference_breakout = max(time_difference_breakout, timedelta())

        total_undertime += time_difference_breakout

    hours, remainder = divmod(total_undertime.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    total_undertime_str = f"{hours:02d}:{minutes:02d}"

   
    DailyRecord.objects.filter(
        timein__isnull=False,
        breakout__isnull=True,  
        EmpCode_id=employee_number,
        date=current_time.date()
    ).update(breakout=formatted_time, totalundertime=total_undertime_str)

# @csrf_exempt
def count_lateness_intervals(lateness_duration):
    total_minutes = lateness_duration.total_seconds() // 60
    
    if total_minutes % 15 == 0:
        lateness_count = total_minutes // 15
    else:
        lateness_count = total_minutes // 15 + 1
    
    return int(lateness_count)

# @csrf_exempt
def insertData(employee_number, current_time,employee_instance,request):
    branch_names = request.user.username
    formatted_time = current_time.strftime("%H:%M:%S")
    total_lateness = timedelta()
    fullname = f"{employee_instance.Firstname} {employee_instance.Middlename} {employee_instance.Lastname}"
    fixed_time = time(6, 31, 00)
    timein_datetime = current_time.time()

    if timein_datetime > fixed_time:
        time_difference = datetime.combine(current_time.date(), timein_datetime) - datetime.combine(current_time.date(), fixed_time)
        time_difference = max(time_difference, timedelta())
        total_lateness += time_difference

    hours, remainder = divmod(total_lateness.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    total_lateness_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

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
            flex_time="UTIshiftA",
        )
        temporay.objects.create(
        EmpCode_id=employee_number,
        Empname=fullname,
        date=current_time.date(),
        timein_names=employee_number,
        timein_timestamps=current_time,
        login_status="breakin_10-12"
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
            flex_time="UTIshiftA",
        )
        temporay.objects.create(
        EmpCode_id=employee_number,
        Empname=fullname,
        date=current_time.date(),
        timein_names=employee_number,
        timein_timestamps=current_time,
        breakout_names=employee_number,
        breakout_timestamps=current_time,
        login_status="breakin_10-12"
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
            flex_time="UTIshiftA",
        )
        temporay.objects.create(
        EmpCode_id=employee_number,
        Empname=fullname,
        date=current_time.date(),
        timein_names=employee_number,
        timein_timestamps=current_time,
        login_status="breakin_10-12"
        )





# @csrf_exempt
def add_time_strings(time_str1, time_str2):
    h1, m1, s1 = map(int, time_str1.split(':'))
    h2, m2, s2 = map(int, time_str2.split(':'))

    total_seconds = (h1 + h2) * 3600 + (m1 + m2) * 60 + (s1 + s2)
    hours, remaining_seconds = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remaining_seconds, 60)

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"



# @csrf_exempt

def breakin(employee_number, current_time,employee_instance):
    formatted_time = current_time.strftime("%H:%M:%S")
    total_lateness = timedelta()

    if current_time:
        fixed_time = time(12, 00, 0)
        breakin_datetime = datetime.combine(current_time.date(), current_time.time())

        if breakin_datetime > datetime.combine(current_time.date(), fixed_time):
            time_difference = breakin_datetime - datetime.combine(current_time.date(), fixed_time)
            time_difference = max(time_difference, timedelta())
            total_lateness += time_difference

            attendance_record = DailyRecord.objects.filter(
                timein__isnull=False, breakout__isnull=False, breakin__isnull=True, EmpCode_id=employee_number,
                date=current_time.date()
            ).first()

            if attendance_record:
                # Update the 'late' field only when it's "Absent AM"
                if attendance_record.late == "Late AM":
                    attendance_record.late = "Late AM-PM"
                elif attendance_record.late == "None" and attendance_record.absent == "Absent AM":
                    attendance_record.late = None
                else:
                    attendance_record.late = "Late PM"

                # Update the 'absent' field if total lateness is more than 3 hours
                if total_lateness > timedelta(hours=3):
                    if attendance_record.absent == "Absent AM":
                        attendance_record.absent = "Absent"
                    else:
                        attendance_record.absent = "Absent PM"

                attendance_record.save()

        hours, remainder = divmod(total_lateness.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        total_lateness_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"


        existing_record = DailyRecord.objects.filter(
            timein__isnull=False, breakout__isnull=False, breakin__isnull=True,
            EmpCode_id=employee_number, date=current_time.date()
        ).first()

        if existing_record:
            total_lateness_str =add_time_strings(total_lateness_str, existing_record.totallateness)
    

        if existing_record and existing_record.absent == "Absent AM":
            DailyRecord.objects.filter(timein__isnull = False, breakout__isnull = False, breakin__isnull = True, EmpCode_id = employee_number, date=current_time.date()
                                       ).update(breakin = formatted_time, remarks =f"Late 2hrs Timein = Absent AM")
        # Update the record with the new values
        else: 
            DailyRecord.objects.filter(
                timein__isnull=False, breakout__isnull=False, breakin__isnull=True,
                EmpCode_id=employee_number, date=current_time.date()
            ).update(
                breakin=formatted_time, totallateness=total_lateness_str, remarks = f"None"
            )





# @csrf_exempt      
def timeout(employee_number,current_time):
    formatted_time = current_time.strftime("%H:%M:%S")

    total_undertime = timedelta()

    if current_time:
        timeout_datetime = datetime.combine(current_time.date(),current_time.time())
        upper_bound_timeout = datetime.combine(current_time.date(), time(18, 30, 0))

        if timeout_datetime < upper_bound_timeout:
            time_difference_timeout = upper_bound_timeout - timeout_datetime
            time_difference_timeout = max(time_difference_timeout, timedelta())

            total_undertime += time_difference_timeout

        hours, remainder = divmod(total_undertime.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        total_undertime_str = f"{hours:02d}:{minutes:02d}"    
        DailyRecord.objects.filter(timein__isnull=False,breakin__isnull=False,breakout__isnull=False,timeout__isnull=True, EmpCode_id=employee_number, date=current_time.date()).update(timeout=formatted_time,totalundertime=total_undertime_str)


def nobreak_out_in(employee_number, current_time):
    DailyRecord.objects.filter(EmpCode_id=employee_number, date=current_time.date()).update(timeout="00:00:00", absent = "Absent", remarks = "No B-OUT and B-IN" )


# fds

def scan_qr_code_from_image_data(image_data):
    nparr = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    decoded_objects = decode(gray)
    return decoded_objects


