from django.shortcuts import render, redirect
from myapp.models import DailyRecord
from django.http import HttpResponseRedirect, HttpResponse
from datetime import datetime,date
from datetime import timedelta,datetime,date,time
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.messages import get_messages
from django.http import JsonResponse


def convert_to_24_hour_format(time_str):
    if time_str.lower() == 'noon':
        return '12:00:00'
    elif time_str.lower() == 'midnight':
        return '00:00:00'
    elif time_str == 'None':
        return None
    else:

        # Check if the time string follows the format "5 p.m"
        if len(time_str.split()) == 2 and time_str.split()[1].lower() in ['a.m.', 'p.m.']:
            # Convert the time string to the format "5:00 p.m."
            time_str = time_str.split()[0] + ':00 ' + time_str.split()[1]
        
        # Split the time string by space to separate the time and AM/PM marker
        time_parts = time_str.split()
        
        # Split the time part by ":" to separate hours and minutes
        time_hour_minute = time_parts[0].split(':')
        hours = int(time_hour_minute[0])
        # Check if minutes are available
        minutes = int(time_hour_minute[1]) if len(time_hour_minute) > 1 else 0
        
        # Adjust hours for PM time
        if len(time_parts) > 1 and time_parts[1].lower() == 'p.m.':
            if hours != 12:
                hours += 12
        
        # Adjust hours for AM time if it's not midnight
        if hours == 12 and len(time_parts) > 1 and time_parts[1].lower() == 'a.m.':
            hours = 0
        
        # Format hours and minutes with leading zeros
        return '{:02d}:{:02d}:00'.format(hours, minutes)


@csrf_exempt
def list(request):
    #employee_list = DailyRecord.objects.filter().values('EmpCode','Empname', 'date', 'timein', 'timeout', 'breakout','breakin', 'totallateness', 'latecount', 'totalundertime', 'totalovertime', 'late', 'absent', 'remarks','user_branchname') # Extract only EmpCode
    selected_date = request.GET.get('selected_date')

    if selected_date:
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        employee_list = DailyRecord.objects.filter(date=selected_date).values('EmpCode', 'Empname', 'date', 'timein', 'timeout', 'breakout', 'breakin', 'totallateness', 'latecount', 'totalundertime', 'totalovertime', 'late', 'absent', 'remarks', 'user_branchname','flex_time')
    else:
        employee_list = DailyRecord.objects.none()

    if request.method == "POST":
        if "update" in request.POST:
            EmpCode = request.POST.get("EmpCode")
            Empname = request.POST.get("Empname")
            date = request.POST.get("date")
            try:
                date_object = datetime.strptime(date, "%B %d, %Y")  # Parse user-submitted format
                date = date_object.strftime("%Y-%m-%d")  # Convert to YYYY-MM-DD
            except ValueError:
                print("error in date")

            try:
                update_employee = DailyRecord.objects.get(EmpCode=EmpCode, date=date)
            except DailyRecord.DoesNotExist:
                print("Record not found for update")
                return HttpResponseRedirect(request.path)  # 


            timein = request.POST.get("timein")
            timeout = request.POST.get("timeout")
            timein = request.POST.get("timein")
            breakout = request.POST.get("breakout")
            breakin = request.POST.get("breakin")
            totallateness = request.POST.get("totallateness")
            late = request.POST.get("late")
            absent = request.POST.get("absent")

            # Check if fields should be set to null
            if timein == "":
                update_employee.timein = None
            else:
                update_employee.timein = convert_to_24_hour_format(timein)

            if timeout == "":
                update_employee.timeout = None
            else:
                update_employee.timeout = convert_to_24_hour_format(timeout)

            if breakout == "":
                update_employee.breakout = None
            else:
                update_employee.breakout = convert_to_24_hour_format(breakout)

            if breakin == "":
                update_employee.breakin = None
            else:
                update_employee.breakin = convert_to_24_hour_format(breakin)

            if totallateness == "None" or totallateness == "none":
                update_employee.totallateness = None
            else:
                update_employee.totallateness = "00:00:00"
            
            if absent == "None" or absent == "none":
                update_employee.absent = None
            else:
                update_employee.absent = "None"

            
            update_employee.late = late
            update_employee.Empname = Empname
            update_employee.save()
            messages.success(request, f'EDIT SUCCESSFULLY!<br>{Empname}<br>{date}', extra_tags='edit')
            return HttpResponseRedirect(request.path)
        

        

        elif "delete" in request.POST:
            EmpCode = request.POST.get("EmpCode")
            date_to_delete = request.POST.get("date")
            date_to_delete_obj = datetime.strptime(date_to_delete, "%B %d, %Y")
            DailyRecord.objects.filter(EmpCode=EmpCode, date=date_to_delete_obj).delete()
            return redirect('list')
    

            
    return render(request, "myapp/list.html", {'employee_list': employee_list})





@csrf_exempt
def fetch_edit_successfully(request):
    messages = get_messages(request)
    filtered_messages = [
        {'text': message.message, 'tags': message.tags} for message in messages if 'edit' in message.tags

    ]

    return JsonResponse({'messages': filtered_messages})

 





