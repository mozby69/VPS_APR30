from django.shortcuts import render
from django.http import HttpResponse
from myapp.forms import DateSelectionForm
from myapp.models import DailyRecord
from django.http import JsonResponse
from datetime import datetime,date,time
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def export(request):
    if request.method == 'POST':
    
        form = DateSelectionForm(request.POST)
        if form.is_valid():
            selected_date = form.cleaned_data['selected_date']
            data = DailyRecord.objects.filter(date=selected_date)
            sql_content = "\n".join([obj.to_sql() for obj in data])

            response = HttpResponse(sql_content, content_type='application/sql')
            response['Content-Disposition'] = f'attachment; filename=COMPLETE_EXPORT_{selected_date}.sql'
            return response
    else:
        form = DateSelectionForm()

    return render(request, 'myapp/export.html', {'form': form})


@csrf_exempt
def export_data_afternoon(request):
    if request.method == 'POST':
        form = DateSelectionForm(request.POST)
        if form.is_valid():
            selected_date = form.cleaned_data['selected_date']
            data = DailyRecord.objects.filter(date=selected_date)
            sql_content = "\n".join([obj.to_sql_all() for obj in data])

            response = HttpResponse(sql_content, content_type='application/sql')
            response['Content-Disposition'] = f'attachment; filename=export_complete_{selected_date}.sql'
            return response
    else:
        form = DateSelectionForm()

    return render(request, 'myapp/export.html', {'form': form})

def view_attendance(request):
    current_date = timezone.now().date()
    data = DailyRecord.objects.all().order_by('-date')  
    filtered_data = data.filter(date=current_date)
    data = list(filtered_data) + list(data.difference(filtered_data))

    return render(request, 'myapp/view_attendance.html', {'data': data})


