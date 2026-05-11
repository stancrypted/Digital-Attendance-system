from . import views
from django.contrib.auth import views as auth_views
from django.urls import path
from .views import CustomLoginView, CustomLogoutView
from django.views.generic import TemplateView

urlpatterns = [
    # path('login/', CustomLoginView.as_view(), name='login'),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('home/', views.home, name='home'),
    path('calendar/', views.calendar, name='calendar'),
    path('results/', views.results, name='results'),
    path("download/", views.download_results, name="download_results"),
    path("upload_result/", views.Upload_result, name="Upload_result"),
    path("view_results/", views.view_results, name="view_results"),
    path("uploaded/", views.uploaded, name="uploaded"),
    path('courses/', views.courses, name='courses'),
    path('M_Chemical_Pathology/', views.M_Chemical_Pathology, name='M_Chemical_Pathology'),
    path('M_Histopathology/', views.M_Histopathology, name='M_Histopathology'),
    path('M_Microbiology/', views.M_Microbiology, name='M_Microbiology'),
    path('M_Pharmacology/', views.M_Pharmacology, name='M_Pharmacology'),
    path('M_Hematology/', views.M_Hematology, name='M_Hematology'),
    path('B_Chemical_Pathology/', views.B_Chemical_Pathology, name='B_Chemical_Pathology'),
    path('B_Histopathology/', views.B_Histopathology, name='B_Histopathology'),
    path('B_Microbiology/', views.B_Microbiology, name='B_Microbiology'),
    path('B_Pharmacology/', views.B_Pharmacology, name='B_Pharmacology'),
    path('B_Hematology/', views.B_Hematology, name='B_Hematology'),
    path('bds_courses/', views.bds_courses, name='bds_courses'),
    path('get_name/', views.get_name, name='get_name'),
    path('submission_success/<int:form_id>/', views.submission_success, name='submission_success'),
    path('debug/templates/', views.debug_template_dirs, name='debug_template_dirs'),
    path('debug/meipass/', views.debug_meipass, name='debug_meipass'),
       
    ]