"""
URL configuration for curriculum project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from myapp import views

urlpatterns = [

    path('admin_home/',views.admin_home),
    path('login_get/',views.login_get),
    path('logout/',views.logout),
    path('login_post/',views.login_post),
    path('view_student/', views.view_student),
    # path('view_reviewrating/',views.view_reviewrating),
    path('view_placementofficer/', views.view_placementofficer),
    path('view_hod/', views.view_hod),
    path('view_feedback/', views.view_feedback),
    path('view_department/', views.view_department),
    path('view_course/<id>', views.view_course),
    path('view_complaint/', views.view_complaint),
    # path('view_carriculamupdates', views.view_carriculamupdates),
    path('view_allocatedhod', views.view_allocatedhod),
    path('send_reply/<id>', views.send_reply),
    path('edit_student/<id>', views.edit_student),
    path('edit_hod/<id>', views. edit_hod),
    path('edit_course/<id>', views.edit_course),
    path('allocatehod/', views.allocatehod),
    path('view_allocation/<id>', views.view_allocation),
    path('edit_coursepost/', views. edit_coursepost),
    path('add_student/', views.add_student),
    path('allocate_post/', views.allocate_post),
    path('add_hod/', views.add_hod),
    path('edit_hod_post/', views.edit_hod_post),
    path('send_reply_post/', views.send_reply_post),
    path('edit_student_post/', views.edit_student_post),
    path('add_department/', views.add_department),
    path('add_department_post/', views.add_department_post),
    path('add_course/', views.add_course),
    path('add_course_post/', views.add_course_post),
    path('add_hod_post/', views.add_hod_post),
    path('add_student_post/', views.add_student_post),
    path('organize_workshop/', views.organize_workshop),
    path('organiz_workshop_post/', views.organiz_workshop_post),
    path('vieworganizeworkshop/', views.vieworganizeworkshop),
    path('changepassword/', views.changepassword),
    path('change_password_post/', views.change_password_post),


    ##################################placement###########################################
    path('register/', views.register),
    path('registerpost/', views.registerpost),
    path('viewprofilee/', views.viewprofilee),
    path('editprofilee/', views.editprofilee),
    path('editprofile_post/', views.editprofile_post),
    path('placementcellhome/', views.placementcellhome),
    path('sendcarriculam_update_post/', views.sendcarriculam_update_post),
    path('sendcarriculam_updates/', views.sendcarriculam_updates),
    path('viewcarriculam_updates/', views.viewcarriculam_updates),
    path('viewapplied_student/', views.viewapplied_student),

############################################hod####################################
    path('viewsession/', views.viewsession),
    path('view_sessionworkshop/', views.view_sessionworkshop),
    path('view_industyreport/', views.view_industyreport),
    path('view_students/', views.view_students),
    path('view_departments/', views.view_departments),
    path('edit_profile_hod/<id>', views.edit_profile_hod),
    path('view_hodprofile/', views.view_hodprofile),
    path('password/', views.password),
    path('hod_home/', views.hod_home),
    path('for_eligiblestudent/', views.for_eligiblestudent),
    path('addsession_workshop/', views.addsession_workshop),
    path('editprofi_post/', views.editprofi_post),
    path('password_post/', views.password_post),

    ####################################################################
    path('delete_course/<id>', views.delete_course),
    path('delete_department/<id>', views.delete_department),
    path('edit_department/<id>', views.edit_department),
    path('edit_departmentpost/', views.edit_departmentpost),
    path('accept_placementofficer/<id>', views.accept_placementofficer),
    path('reject_placementofficer/<id>', views.reject_placementofficer),
    path('reject_eligibility/<id>', views.reject_eligibility),
    path('accept_eligibility/<id>', views.accept_eligibility),
    path('changepasswordd/', views.changepasswordd),





]
