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
    path('block_unblock_student/<id>/<status>', views.block_unblock_student),
    # path('view_reviewrating/',views.view_reviewrating),
    path('view_placementofficer/', views.view_placementofficer),
    path('view_hod/', views.view_hod),
    path('admin_trending_skill/', views.admin_trending_skill),

    path('admin_view_feedback/', views.admin_view_feedback),
    path('view_department/', views.view_department),
    path('view_course/<id>', views.view_course),
    path('view_complaint/', views.view_complaint),
    path('viewcurriculumupdate/<id>', views.viewcurriculumupdate),
    path('accept_curriculumupdate/<id>', views.accept_curriculumupdate),
    path('reject_curriculumupdate/<id>', views.reject_curriculumupdate),
    path('view_allocatedhod', views.view_allocatedhod),
    path('send_reply/<id>', views.send_reply),
    path('block_unblock_hod/<id>/<status>', views.block_unblock_hod),
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
    path('send_reply/<id>', views.send_reply),
    path('send_reply_post/', views.send_reply_post),
    path('edit_student_post/', views.edit_student_post),
    path('add_department/', views.add_department),
    path('add_department_post/', views.add_department_post),
    path('add_course/', views.add_course),
    path('add_course_post/', views.add_course_post),
    path('add_hod_post/', views.add_hod_post),
    path('add_student_post/', views.add_student_post),
    path('organize_workshop/', views.organize_workshop),
    path('accept_request/<id>', views.accept_request),
    path('reject_workshp_request/<id>', views.reject_workshp_request),
    path('organiz_workshop_post/', views.organiz_workshop_post),
    path('vieworganizeworkshop/', views.vieworganizeworkshop),
    path('changepassword_admin/', views.changepassword_admin),
    path('change_password_post/', views.change_password_post),
    path('send_score/<id>', views.send_score),
    path('send_score_post/', views.send_score_post),
    path('View_certificate/<id>', views.View_certificate),


    ##################################placement###########################################
    path('register/', views.register),
    path('registerpost/', views.registerpost),
    path('viewprofilee/', views.viewprofilee),
    path('changepassword_post/', views.changepassword_post),
    path('changepassword_placement/', views.changepassword_placement),
    path('editprofilee/', views.editprofilee),
    path('editprofile_post/', views.editprofile_post),
    path('placementcellhome/', views.placementcellhome, name='placementcellhome'),
    path('sendcarriculam_update_post/', views.sendcarriculam_update_post),
    path('sendcarriculam_updates/', views.sendcarriculam_updates),
    path('viewcarriculam_updates/', views.viewcarriculam_updates),
    path('viewapplied_student/', views.viewapplied_student),
    path('trending_skill/', views.trending_skill),
    path('add_vacancy_post/', views.add_vacancy_post),
    path('view_vacancies/', views.view_vacancies),
    path('add_vaccancy/', views.add_vaccancy),
    path('delete_vaccancy/<id>', views.delete_vaccancy),

############################################hod####################################
    path('viewsession/', views.viewsession),
    path('view_sessionworkshop/', views.view_sessionworkshop),
    path('view_industyreport/', views.view_industyreport),
    path('view_students/', views.view_students),
    path('edit_studentss/<id>', views.edit_studentss),
    path('edit_studentss_post/', views.edit_studentss_post),
    path('view_departments/', views.view_departments),
    path('edit_profile_hod/', views.edit_profile_hod),
    path('view_hodprofile/', views.view_hodprofile),
    path('password/', views.password),
    path('hod_home/', views.hod_home),
    path('for_eligiblestudent/', views.for_eligiblestudent),
    path('addsession_workshop/', views.addsession_workshop),
    path('editprofi_post/', views.editprofi_post),
    path('password_post/', views.password_post),
    path('view_complaint_hod/', views.view_complaint_hod),
    path('hod_view_feedback/', views.hod_view_feedback),

    ####################################################################
    path('delete_course/<id>', views.delete_course),
    path('delete_department/<id>', views.delete_department),
    path('edit_department/<id>', views.edit_department),
    path('edit_departmentpost/', views.edit_departmentpost),
    path('accept_placementofficer/<id>', views.accept_placementofficer),
    path('reject_placementofficer/<id>', views.reject_placementofficer),
    path('reject_eligibility/<id>', views.reject_eligibility),
    path('accept_eligibility/<id>', views.accept_eligibility),
    path('view_application_status_api/', views.view_application_status_api),



    ########################################flutter############################



    path('student_view_score/', views.view_score),
    path('student_send_complaint/', views.student_send_complaint),
    path('viewMycomplaints/', views.viewMycomplaints),
    path('student_view_profile/', views.student_view_profile),
    path('flutter_login/', views.flutter_login),
    path('student_edit_profile/', views.student_edit_profile),
    path('student_view_profile/', views.student_view_profile),
    path('send_feedback/', views.send_feedback),
    path('view_feedback/', views.view_feedback),
    path('view_workshopstudent/', views.view_workshopstudent),
    path('change_passwordpost_student/', views.change_passwordpost_student),
    path("user_Forgot_password", views.student_Forgot_password, name="user_Forgot_password"),
    path("attendworkshop_request/", views.attendworkshop_request, name="attendworkshop_request"),
    path("view_workshop_request/", views.view_workshop_request, name="view_workshop_request"),
    path("view_score/", views.view_score, name="view_score"),
    path("view_workshoprequest/", views.view_workshoprequest, name="view_workshoprequest"),
    path("viewcertificate/", views.viewcertificate, name="viewcertificate"),
    path("student_upload_certificate/", views.student_upload_certificate, name="student_upload_certificate"),
    path("view_vacancy_api/", views.view_vacancy_api),
    path("send_application/", views.send_application),
    path("student_view_industry_report/", views.student_view_industry_report),





]
