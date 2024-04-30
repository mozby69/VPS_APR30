from django.shortcuts import render, redirect
from myapp.models import DailyRecord
from django.http import JsonResponse
from datetime import datetime, time,date
from django.conf import settings
from django.http import HttpResponse


def check_late_mainpage(request):
    return render(request, "myapp/check_late.html")




def display_table_checklate(request):
    selected_date = request.GET.get('selected_date')
    current_date = date.today()
    if selected_date:
        # Convert the selected date string to datetime object
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        # Filter records where date is equal to selected date
        attendances = DailyRecord.objects.filter(date=selected_date, late='Late AM').values('user_branchname', 'Empname', 'timein', 'latecount')
    else:
        # If no date is selected, return all records
        attendances = DailyRecord.objects.filter(date=current_date, late='Late AM').values('user_branchname', 'Empname', 'timein', 'latecount')

    data = [
        {
            'user_branchname': attendance['user_branchname'],
            'Empname': attendance['Empname'],
            'timein': attendance['timein'].strftime('%H:%M:%S'),  # Format timein as string
            'latecount': attendance['latecount'],
        }
        for attendance in attendances
    ]

    return JsonResponse({'attendances': data})



def generate_pdf(request):
    selected_date = request.GET.get('selected_date')
    current_date = date.today()
    if selected_date:
        # Convert the selected date string to datetime object
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        # Filter records where date is equal to selected date
        attendances = DailyRecord.objects.filter(date=selected_date, late='Late AM').values('user_branchname', 'Empname', 'timein', 'latecount')
    else:
        # If no date is selected, return all records
        attendances = DailyRecord.objects.filter(date=current_date, late='Late AM').values('user_branchname', 'Empname', 'timein', 'latecount')

    context = {'attendances': attendances, 'selected_date': selected_date}
    return render(request, 'myapp/print_late.html', context)
