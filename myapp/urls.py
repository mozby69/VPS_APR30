from django.urls import path
from . import views
from .views import index,display_qr_list,webcam_qr_code_scanner,fetch_messages,display_current_time
# from .app_views.qr_generator import generate_qr_code,user_profile
from django.conf.urls.static import static
from django.conf import settings
from .app_views.export import export,export_data_afternoon,view_attendance
from django.contrib.auth import views as auth_views
from django.views.generic.base import TemplateView
from .app_views.addemployee import addemployee
from .app_views.serviamus_six import serviamus_main_page,webcam_qr_code_scanner_serviamus_six,fetch_messages_serviamus
from .app_views.serviamus_seven import webcam_qr_code_scanner_serviamus_seven
from .app_views.utility_10 import fetch_messages_utility_ten,webcam_qr_code_scanner_serviamus_utility_10
from .app_views.utility_12 import utility_mh_render_page,fetch_messages_utility_twelve,webcam_qr_code_scanner_serviamus_utility_12
from .app_views.hpc import hpc_main_page,fetch_messages_hpc,webcam_qr_code_scanner_hpc
from .app_views.list import list,fetch_edit_successfully
from .app_views.temp import main_temp 
from .app_views.check_late import check_late_mainpage,display_table_checklate, generate_pdf
# SGI/NAZARETH
from .app_views.sgi import main_sgi_page,display_qr_list_sgi,fetch_messages_sgi,webcam_qr_code_scanner_sgi_09pm_06am, webcam_qr_code_scanner_sgi_12pm_09pm,webcam_qr_code_scanner_sgi_06am_03pm,webcam_qr_code_scanner_sgi_730am_430pm
from .app_views.NAZARETH import main_nazareth_page, fetch_messages_nazareth,webcam_qr_code_scanner_nazareth_8am_5pm,display_qr_list_nazareth,webcam_qr_code_scanner_nazareth_12pm_09pm,webcam_qr_code_scanner_nazareth_10am_07pm,webcam_qr_code_scanner_nazareth_11am_08pm

urlpatterns = [
    path('', views.login_view, name='login'),
    path('home/', views.home, name='home'),
    #path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('logout/', views.custom_logout, name='logout'),
    path('index/', index, name="index"),
    path('display_qr_list/', display_qr_list, name='display_qr_list'),
    path('webcam_qr_code_scanner/',webcam_qr_code_scanner,name='webcam_qr_code_scanner'),
    path('fetch_messages/', fetch_messages, name='fetch_messages'),
    # path('QR_list/', generate_qr_code, name='generate_qr_code'),
    # path('user_profile/<int:pk>/', user_profile, name='user_profile'),
    path('export/', export, name='export'),
    path('export_all/', export_data_afternoon, name='export_data_afternoon'),
    path('addemployee/', addemployee, name='addemployee'),
    path('view_attendance/', view_attendance, name='view_attendance'),
    path('display_current_time/', display_current_time, name='display_current_time'),

    path('dtr_serviamus/', serviamus_main_page, name="serviamus_main_page"),
    path('webcam_qr_code_scanner_serviamus_six/', webcam_qr_code_scanner_serviamus_six, name="webcam_qr_code_scanner_serviamus_six"),
    path('webcam_qr_code_scanner_serviamus_seven/', webcam_qr_code_scanner_serviamus_seven, name="webcam_qr_code_scanner_serviamus_seven"),
    path("utility_mh/", utility_mh_render_page, name="utility_mh_render_page"),
    path("fetch_messages_utility_ten/", fetch_messages_utility_ten, name="fetch_messages_utility_ten"),
    path("fetch_messages_serviamus/", fetch_messages_serviamus, name="fetch_messages_serviamus"),
    path("webcam_qr_code_scanner_serviamus_utility_12/", webcam_qr_code_scanner_serviamus_utility_12, name="webcam_qr_code_scanner_serviamus_utility_12"),
    path("webcam_qr_code_scanner_serviamus_utility_10/", webcam_qr_code_scanner_serviamus_utility_10, name="webcam_qr_code_scanner_serviamus_utility_10"),
    path("hpc_main_page/", hpc_main_page, name="hpc_main_page"),
    path("fetch_messages_hpc/",fetch_messages_hpc,name="fetch_messages_hpc"),
    path("webcam_qr_code_scanner_hpc/", webcam_qr_code_scanner_hpc, name="webcam_qr_code_scanner_hpc"),
    path("list/", list,name="list"),
    path("main_temp/", main_temp, name="main_temp"),
    path("fetch_messages_utility_twelve/",fetch_messages_utility_twelve, name="fetch_messages_utility_twelve"),
    #late
    path('check_late_mainpage/', check_late_mainpage, name="check_late_mainpage"),
    path('display_table_checklate/', display_table_checklate, name="display_table_checklate"),
    path('generate_pdf/', generate_pdf, name="generate_pdf"),
    path('fetch_edit_successfully/', fetch_edit_successfully, name="fetch_edit_successfully"),
     #sgi
    path("main_sgi_page/", main_sgi_page, name="main_sgi_page"),
    path('display_qr_list_sgi/', display_qr_list_sgi, name='display_qr_list_sgi'),
    path('webcam_qr_code_scanner_sgi_09pm_06am/',webcam_qr_code_scanner_sgi_09pm_06am, name="webcam_qr_code_scanner_sgi_09pm_06am"),
    path('webcam_qr_code_scanner_sgi_12pm_09pm/', webcam_qr_code_scanner_sgi_12pm_09pm, name="webcam_qr_code_scanner_sgi_12pm_09pm"),
    path('webcam_qr_code_scanner_sgi_06am_03pm/',webcam_qr_code_scanner_sgi_06am_03pm, name="webcam_qr_code_scanner_sgi_06am_03pm"),
    path('webcam_qr_code_scanner_sgi_730am_430pm/', webcam_qr_code_scanner_sgi_730am_430pm, name="webcam_qr_code_scanner_sgi_730am_430pm"),
    path('fetch_messages_sgi/',fetch_messages_sgi, name="fetch_messages_sgi"),
    #nazareth
    path('nazareth/', main_nazareth_page, name="main_nazareth_page"),
    path('display_qr_list_nazareth/', display_qr_list_nazareth, name="display_qr_list_nazareth"),
    path('webcam_qr_code_scanner_nazareth_8am_5pm/', webcam_qr_code_scanner_nazareth_8am_5pm, name="webcam_qr_code_scanner_nazareth_8am_5pm"),
    path('webcam_qr_code_scanner_nazareth_12pm_09pm/', webcam_qr_code_scanner_nazareth_12pm_09pm, name="webcam_qr_code_scanner_nazareth_12pm_09pm"),
    path('webcam_qr_code_scanner_nazareth_10am_07pm/', webcam_qr_code_scanner_nazareth_10am_07pm, name="webcam_qr_code_scanner_nazareth_10am_07pm"),
    path('webcam_qr_code_scanner_nazareth_11am_08pm/', webcam_qr_code_scanner_nazareth_11am_08pm, name="webcam_qr_code_scanner_nazareth_11am_08pm"),
    path('fetch_messages_nazareth/',fetch_messages_nazareth, name="fetch_messages_nazareth"),
]




urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)