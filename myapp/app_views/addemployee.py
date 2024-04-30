from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from myapp.models import Employee
from django.db import IntegrityError
import qrcode
from PIL import Image
from django.conf import settings
import os
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
#from reportlab.pdfgen import canvas
from django.http import FileResponse
import io
from django.db.models.signals import pre_delete
from django.dispatch import receiver
import os
import imghdr
from django.views.decorators.csrf import csrf_exempt



@csrf_exempt
def addemployee(request):
    qr_list = Employee.objects.all()
    if request.method == "POST":

        if "addQR" in request.POST:
            EmpCode = request.POST.get("EmpCode")
            Firstname = request.POST.get("Firstname")
            Middlename = request.POST.get("Middlename")
            Lastname = request.POST.get("Lastname")
            full_name = f"{Firstname} {Middlename} {Lastname}"

            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(EmpCode)
            qr.make(fit=True)
            qr_image = qr.make_image(fill_color="black", back_color="white")

            img_path = f"qrcodes/{EmpCode}-{full_name}.png"
            qr_image.save(os.path.join(settings.MEDIA_ROOT, img_path))

            # img_path = f"static/qrcodes/{EmpCode}.png"
            # qr_image.save(os.path.join(img_path))

 
            try:
                Employee.objects.create(EmpCode=EmpCode,Firstname=Firstname,Middlename=Middlename,Lastname=Lastname, qr_code=img_path)
            except IntegrityError:
                return HttpResponse("Error occurred")
            return HttpResponseRedirect(request.path)


        elif "update" in request.POST:
            EmpCode = request.POST.get("EmpCode")
            Firstname = request.POST.get("Firstname")
            Middlename = request.POST.get("Middlename")
            Lastname = request.POST.get("Lastname")
     
            update_employee_qr = Employee.objects.get(EmpCode=EmpCode)
            update_employee_qr.EmpCode = EmpCode
            update_employee_qr.Firstname = Firstname
            update_employee_qr.Middlename = Middlename
            update_employee_qr.Lastname = Lastname
            update_employee_qr.save()
            return HttpResponseRedirect(request.path)
        

        elif "delete" in request.POST:
            EmpCode = request.POST.get("EmpCode")
            Employee.objects.get(EmpCode=EmpCode).delete()
            return redirect('addemployee')
                


    
    return render(request, 'myapp/addemployee.html', {'qr_list': qr_list})





    



@receiver(pre_delete, sender=Employee)
def delete_qr_code_image(sender, instance, **kwargs):
    # Delete the associated QR code image file
    if instance.qr_code:
        if os.path.isfile(instance.qr_code.path):
            os.remove(instance.qr_code.path)

# def user_profile(request, pk):
#     qr_list = Employee.objects.all().order_by('id')
#     student = get_object_or_404(Employee, EmpCode=pk)
#     return render(request, 'myapp/employee.html', {'student': student, 'qr_list': qr_list}) 


    
