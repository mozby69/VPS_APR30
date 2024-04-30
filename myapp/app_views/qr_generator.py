# from django.shortcuts import render,redirect,get_object_or_404
# from django.http import HttpResponseRedirect, HttpResponse
# from myapp.models import QRList
# from django.db import IntegrityError
# import qrcode
# from PIL import Image
# from django.conf import settings
# import os
# from django.db.models import Q
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# #from reportlab.pdfgen import canvas
# from django.http import FileResponse
# import io




# def generate_qr_code(request):
#     qr_list = QRList.objects.all().order_by('id')
#     query = request.POST.get("searchquery", "")

#     if query:
#         qr_list = QRList.objects.filter(Q(name__icontains=query))

#     # Paginate the result
#     page = request.GET.get('page', 1)
#     paginator = Paginator(qr_list, 10)

#     try:
#         qr_list = paginator.page(page)
#     except PageNotAnInteger:
#         qr_list = paginator.page(1)
#     except EmptyPage:
#         qr_list = paginator.page(paginator.num_pages)
        
#     if request.method == "POST":

#         if "addQR" in request.POST:
#             name = request.POST.get("firstname")

#             # Generate QR code using the entered name
#             qr = qrcode.QRCode(
#                 version=1,
#                 error_correction=qrcode.constants.ERROR_CORRECT_L,
#                 box_size=10,
#                 border=4,
#             )
#             qr.add_data(name)
#             qr.make(fit=True)
#             qr_image = qr.make_image(fill_color="black", back_color="white")

#             # Save generated QR code image
#             img_path = f"qrcodes/{name}_qr.png"
#             qr_image.save(os.path.join(settings.MEDIA_ROOT, img_path))

#             # Save record with QR code image path
#             try:
#                 QRList.objects.create(name=name, qr_code=img_path)
#             except IntegrityError:
#                 return HttpResponse("Error occurred")
#             return HttpResponseRedirect(request.path)

#         # elif "addQRExisting" in request.POST:
#         #     name_existing = request.POST.get("firstname")
#         #     qr_image = request.FILES.get("qrimage")

#         #     # Save uploaded QR code image for existing record
#         #     img_path_existing = f"qrcodes_existing/{name_existing}.png"
#         #     with open(f"media/{img_path_existing}", "wb") as img_file:
#         #         for chunk in qr_image.chunks():
#         #             img_file.write(chunk)

#         #     # Save record with QR code image path for existing record
#         #     try:
#         #         QRList.objects.create(name=name_existing, qr_code=img_path_existing)
#         #     except IntegrityError:
#         #         return HttpResponse("Error occurred")
#         #     return HttpResponseRedirect(request.path)


#         # elif "print" in request.POST:
#         #     # Create a PDF document
#         #     buffer = io.BytesIO()
#         #     p = canvas.Canvas(buffer)
#         #     QR = QRList.objects.all()
#         #     p.drawString(50,820, " QR CODE")

           
#         #     y_position = 700  
#         #     for qr_record in QR:
#         #         name = qr_record.name
#         #         p.drawString(50, y_position, f" Name: {name}")
#         #         y_position -= 20

#         #     p.showPage()
#         #     p.save()
#         #     buffer.seek(0)

#         #     response = FileResponse(buffer, content_type='application/pdf')

    
#         #     response['Content-Disposition'] = 'inline; filename="qr_code.pdf"'

#         #     return response


#         elif "update" in request.POST:
#             id = request.POST.get("id")
#             name = request.POST.get("name")
      

#             update_employee_qr = QRList.objects.get(id=id)
#             update_employee_qr.name = name
#             update_employee_qr.save()
#             #messages.success(request, 'Data updated successfully!',extra_tags='updated')
#             return HttpResponseRedirect(request.path)

#         elif "delete" in request.POST:
#             id = request.POST.get("id")
#             QRList.objects.get(id=id).delete()
#             # Redirect after the form is successfully submitted
#             return redirect('generate_qr_code')





                
                
#             #return render(request, 'myapp/generate_qr_code.html', {'qr_list': qr_list, 'query': query})

#     #qr_list = QRList.objects.all()
    
#     return render(request, 'myapp/generate_qr_code.html', {'qr_list': qr_list, 'query': query})




# def user_profile(request, pk):
#     qr_list = QRList.objects.all().order_by('id')
#     student = get_object_or_404(QRList, id=pk)
#     return render(request, 'myapp/employee.html', {'student': student, 'qr_list': qr_list}) 


    
