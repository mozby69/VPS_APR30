from django.shortcuts import render,redirect
from myapp.models import temporay
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from datetime import timedelta,datetime,date,time
from django.http import HttpResponseRedirect
from django.core.exceptions import ValidationError


@csrf_exempt
def main_temp(request):
    employee_list = temporay.objects.values('id','Empname', 'date', 'timein_names', 'breakout_names','breakin_names', 'timeout_names', 'timein_timestamps','breakout_timestamps', 'breakin_timestamps', 'timeout_timestamps', 'login_status').order_by('-date')
    if request.method == "POST": 
        if "delete" in request.POST:
            id = request.POST.get("id")
            temporay.objects.get(id=id).delete()
            return redirect('main_temp')
        
        elif "update" in request.POST:
            id = request.POST.get("id")
            Empname = request.POST.get("Empname")
            timein_names = request.POST.get("timein_names")
            breakout_names = request.POST.get("breakout_names")
            breakin_names = request.POST.get("breakin_names")
            timeout_names = request.POST.get("timeout_names")

            # Get time data from request.POST and check if it's empty
            timein_timestamps_str = request.POST.get("timein_timestamps")
            breakout_timestamps_str = request.POST.get("breakout_timestamps")
            breakin_timestamps_str = request.POST.get("breakin_timestamps")
            timeout_timestamps_str = request.POST.get("timeout_timestamps")

            if timein_timestamps_str:
                timein_timestamps = datetime.strptime(timein_timestamps_str, "%Y-%m-%d %I:%M %p").strftime("%Y-%m-%d %H:%M:%S.%f")
            else:
                timein_timestamps = None

            if breakout_timestamps_str:
                breakout_timestamps = datetime.strptime(breakout_timestamps_str, "%Y-%m-%d %I:%M %p").strftime("%Y-%m-%d %H:%M:%S.%f")
            else:
                breakout_timestamps = None

            if breakin_timestamps_str:
                breakin_timestamps = datetime.strptime(breakin_timestamps_str, "%Y-%m-%d %I:%M %p").strftime("%Y-%m-%d %H:%M:%S.%f")
            else:
                breakin_timestamps = None

            if timeout_timestamps_str:
                timeout_timestamps = datetime.strptime(timeout_timestamps_str, "%Y-%m-%d %I:%M %p").strftime("%Y-%m-%d %H:%M:%S.%f")
            else:
                timeout_timestamps = None

            update_employee_qr = temporay.objects.get(id=id)

            if timein_names == '':
                timein_names = None
            
            if breakout_names == '':
                breakout_names = None
            
            if breakin_names == '':
                breakin_names = None
            
            if timeout_names == '':
                timeout_names = None

            update_employee_qr.Empname = Empname
            update_employee_qr.timein_names = timein_names
            update_employee_qr.breakout_names = breakout_names
            update_employee_qr.breakin_names = breakin_names
            update_employee_qr.timeout_names = timeout_names

            update_employee_qr.timein_timestamps = timein_timestamps
            update_employee_qr.breakout_timestamps = breakout_timestamps
            update_employee_qr.breakin_timestamps = breakin_timestamps
            update_employee_qr.timeout_timestamps = timeout_timestamps

            try:
                update_employee_qr.full_clean()  # Validate model fields
                update_employee_qr.save()
                # messages.success(request, 'Data updated successfully!', extra_tags='updated')
            except ValidationError as e:
                # Handle validation errors
                # You can display error messages or handle them accordingly
                pass

            return redirect('main_temp')
    
    return render(request, "myapp/temp.html",{'employee_list': employee_list})



