import datetime
import email
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pickle import GET

from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpResponse, JsonResponse, request
from django.shortcuts import render, redirect
from django.contrib.auth.models import User,Group






# Create your views here.
from pip._vendor.requests import post

from myapp.allcoursescrap import fetch_all_courses_by_department, get_cached_career_data, get_hod_cached_career_data
from myapp.models import *


def admin_home(request):
    return render(request,'home.html')

def logout(request):
    return render(request,'login.html')




# def login_get(request):
#     return render(request,'login.html')

def login_get(request):
    """Login page - triggers background data refresh"""
    # Refresh career data when user visits login page
    get_cached_career_data(refresh=False)  # Force refresh

    return render(request, 'login.html')


def trending_skill(request):


    """View trending skills from cached JSON file"""
    try:
        # Get data from cache (very fast)
        data = get_cached_career_data(refresh=False)

        context = {
            'career_data': data,
            'total_courses': data.get('total_courses', 0),
        }

        print(context,"context")

        return render(request, 'placementcell/indstry_trending.html', context)

    except Exception as e:
        context = {
            'error': f"Failed to load career data: {str(e)}",
            'career_data': None
        }

        return render(request, 'placementcell/indstry_trending.html', context)

def  admin_trending_skill(request):


        try:
            # Get data from cache (very fast)
            data = get_cached_career_data(refresh=False)

            context = {
                'career_data': data,
                'total_courses': data.get('total_courses', 0),
            }

            print(context, "context")

            return render(request, 'admin/admin_indstrytrends.html', context)

        except Exception as e:
            context = {
                'error': f"Failed to load career data: {str(e)}",
                'career_data': None
            }

            return render(request, 'admin/admin_indstrytrends.html', context)


#
# def view_industyreport(request):
#     """View trending skills for HOD's department"""
#     try:
#         # Get HOD's department
#         allocation = ALLOCATION_table.objects.get(HOD__LOGIN_id=request.user.id)
#         hod_department = allocation.department.department
#
#         print(hod_department,"aaaaaa")# Adjust field name if needed
#
#         # Get filtered data
#         data = get_hod_cached_career_data(refresh=False, department=hod_department)
#
#         print(data,"dataaaa")
#
#         context = {
#             'career_data': data,
#             'total_courses': data.get('total_courses', 0),
#             'hod_department': hod_department,
#         }
#
#         return render(request, 'Hod/viewindustry_reports.html', context)
#
#     except ALLOCATION_table.DoesNotExist:
#         context = {
#             'error': "Department allocation not found for this HOD.",
#             'career_data': None
#         }
#         return render(request, 'Hod/viewindustry_reports.html', context)
#
#     except Exception as e:
#         context = {
#             'error': f"Failed to load career data: {str(e)}",
#             'career_data': None
#         }
#         return render(request, 'Hod/viewindustry_reports.html', context)
#
#



def view_industyreport(request):
    """View trending skills for HOD's department only"""
    try:
        # Get HOD's department
        allocation = ALLOCATION_table.objects.select_related('department').get(
            HOD__LOGIN_id=request.user.id
        )
        hod_department = allocation.department.department
        print(hod_department,"viewwwww")
        # Get filtered data (Only this department)
        data = get_hod_cached_career_data(refresh=False, department=hod_department)

        context = {
            'career_data': data,
            'total_courses': data.get('total_courses', 0),
            'hod_department': hod_department,
        }

        return render(request, 'Hod/viewindustry_reports.html', context)

    except ALLOCATION_table.DoesNotExist:
        context = {
            'error': "Your department allocation was not found.",
            'career_data': None,
            'hod_department': None
        }
        return render(request, 'Hod/viewindustry_reports.html', context)

    except Exception as e:
        context = {
            'error': f"Failed to load industry trends: {str(e)}",
            'career_data': None,
            'hod_department': None
        }
        return render(request, 'Hod/viewindustry_reports.html', context)








def login_post(request):
    if request.method == "POST":
        username=request.POST["name"]
        password=request.POST["password"]
        user=authenticate(request,username=username,password=password)
        if user is not None:
            if user.groups.filter(name="admin").exists():
                login(request,user)
                return redirect('/myapp/admin_home/')
            elif user.groups.filter(name="placementcell").exists():
                ob=PLACEMENTCELL_table.objects.get(LOGIN__id=user.id)
                if ob.status == 'Accepted':
                    # request.session['name']=ob.name
                    # request.session['photo']=ob.photo.url
                    login(request,user)
                    return redirect('/myapp/placementcellhome/')
                # else:
                #     return HttpResponse('''<script>alert("not verified");window.location="/myapp/login_get/"</script>''')
            elif user.groups.filter(name="hod").exists():
                login(request,user)
                return redirect('/myapp/hod_home')
            else:
                messages.warning(request, 'Invalid User')

                return redirect('/myapp/login_get/')
        messages.warning(request, 'invalid username and password')

        return render(request,'login.html')

def add_department(request):
    return render(request, 'admin/adddepartment.html')

def add_department_post(request):
    department=request.POST['department']
    details=request.POST['details']

    ab=DEPARTMENT_table()
    ab.department=department
    ab.details=details
    ab.save()
    return redirect('/myapp/view_department/')


def view_department(request):
    ab=DEPARTMENT_table.objects.all()
    return render(request, 'admin/viewdepartment.html',{'data':ab})

def delete_department(request,id):
    ab=DEPARTMENT_table.objects.get(id=id).delete()
    return redirect('/myapp/view_department/')



def edit_department(request,id):
    request.session['did'] = id
    data = DEPARTMENT_table.objects.get(id=id)
    return render(request,'admin/editdepartment.html',{'data':data})


def edit_departmentpost(request):
    department=request.POST['department']
    details=request.POST['details']
    ac=DEPARTMENT_table.objects.get(id=request.session['did'])
    ac.details=details
    ac.department=department
    ac.save()
    return redirect(f'/myapp/view_department/')




def delete_course(request,id):
    ab=COUSE_table.objects.get(id=id).delete()
    return redirect('/myapp/view_course/'+str(request.session['did']))

def view_course(request,id):
    request.session['did']=id
    ab=COUSE_table.objects.filter(Department_id=id)
    return render(request, 'admin/viewcourse.html',{'data':ab})


def add_course(request):
    ab = COUSE_table.objects.all()
    return render(request,'admin/addcourse.html',{'data':ab})



def add_course_post(request):
    department=request.session['did']
    course=request.POST['course']
    details=request.POST['details']
    ac=COUSE_table()
    ac.course=course
    ac.details=details
    ac.Department_id=department
    ac.save()
    return redirect(f'/myapp/view_course/{department}')



def add_hod(request):
    return render(request,'admin/addhod.html')


def add_hod_post(request):
    name=request.POST['namee']
    place=request.POST['place']
    post=request.POST['post']
    pin=request.POST['pin']
    phone=request.POST['phone']
    email=request.POST['email']
    photo=request.FILES['photo']
    gender=request.POST['gender']
    qualification=request.POST['qualification']
    username=request.POST['username']
    password=request.POST['password']


    user=User.objects.create( username=username,password= make_password(password))
    user.save()
    user.groups.add(Group.objects.get(name='hod'))


    obj=HOD_table()
    obj.LOGIN= user
    obj.name= name
    obj.place= place
    obj.post= post
    obj.pin= pin
    obj.phone= phone
    obj.email= email
    obj.gender= gender
    obj.qualification= qualification
    obj.photo= photo
    obj.save()
    messages.success(request,'added')
    return redirect('/myapp/view_hod/')






def add_student(request):
    ab=COUSE_table.objects.all()
    return render(request, 'admin/addstudent.html',{'data':ab})




def add_student_post(request):
    name = request.POST['name']
    place = request.POST['place']
    district = request.POST['district']
    post = request.POST['post']
    pin = request.POST['pin']
    phone = request.POST['phone']
    email = request.POST['email']
    course = request.POST['course']
    photo = request.FILES['photo']
    gender = request.POST['gender']
    qualification = request.POST['qualification']
    skill=request.POST['skill']
    username = request.POST['username']
    password = request.POST['password']

    user = User.objects.create(username=username, password=make_password(password))
    user.save()
    user.groups.add(Group.objects.get(name='student'))


    obj = STUDENT_table()
    obj.LOGIN = user
    obj.name = name
    obj.place = place
    obj.district = district
    obj.post = post
    obj.pin = pin
    obj.phone = phone
    obj.COURSE_id = course
    obj.email = email
    obj.gender = gender
    obj.skill = skill
    obj.qualification = qualification
    obj.photo = photo
    obj.save()
    messages.success(request, 'added')
    return redirect('/myapp/view_student/')






def view_student(request):
    ab = STUDENT_table.objects.all()
    return render(request, 'admin/viewstudent.html',{'data':ab})



def view_hod(request):
    ab=HOD_table.objects.all()
    return render(request, 'admin/viewhod.html',{'data':ab})


def view_workshop_request(request):
    ab=ATTENDWORKSHOP_REQUEST_table.objects.all()
    return render(request, 'admin/view_request.html',{'data':ab})

def accept_request(request,id):
    ab = ATTENDWORKSHOP_REQUEST_table.objects.get(id=id)
    ab.status="Accepted"
    ab.save()
    messages.success(request,"Approved")
    return redirect('/myapp/view_workshop_request/')

def reject_workshp_request(request,id):
    ab = ATTENDWORKSHOP_REQUEST_table.objects.get(id=id)
    ab.status="Rejected"
    ab.save()
    messages.error(request,"Rejected")

    return redirect('/myapp/view_workshop_request/')


def view_allocation(request,id):
    department=request.session['hid']=id
    ab=ALLOCATION_table.objects.all()
    return render(request,'admin/viewallocatedhod.html',{'data':ab,'depart':department})



def block_unblock_hod(request,id,status):
    ab=HOD_table.objects.get(id=id)
    ab.status=status
    ab.save()
    return redirect('/myapp/view_hod/')



def allocatehod(request):
    ab=DEPARTMENT_table.objects.all()
    hods = HOD_table.objects.all()
    return render(request, 'admin/allocatehod.html',{'data':ab,'hods':hods})



def allocate_post(request):
    department = request.POST['department']
    hid = request.session['hid']

    if ALLOCATION_table.objects.filter(HOD_id=hid).exists():

        messages.success(request, 'This HOD is already allocated to a department')
        return redirect('/myapp/view_hod/')

    else:

        ab = ALLOCATION_table()

        ab.HOD = HOD_table.objects.get(id=hid)
        ab.department_id=department
        ab.date = datetime.date.today()
        ab.status = "pending"

        ab.save()

        messages.success(request, 'Allocated successfully')
        return redirect('/myapp/view_hod/')


def edit_course(request,id):
    request.session['id']=id
    data = COUSE_table.objects.get(id=id)
    return render(request,'Admin/editcourse.html',{'data':data})


def edit_coursepost(request):
    department=request.session['did']
    course=request.POST['course']
    details=request.POST['details']
    ac=COUSE_table.objects.get(id=request.session['id'])
    ac.course=course
    ac.details=details
    ac.Department_id=department
    ac.save()
    return redirect(f'/myapp/view_course/{department}')



def edit_hod(request,id):
    request.session['id'] = id
    ob = HOD_table.objects.get(id=id)
    return render(request, 'admin/edithod.html',{'data':ob})


def edit_hod_post(request):
    name=request.POST['name']
    place=request.POST['place']
    post=request.POST['post']
    pin=request.POST['pin']
    phone=request.POST['phone']
    email=request.POST['email']
    gender=request.POST['gender']
    qualification=request.POST['qualification']



    obj=HOD_table.objects.get(id=request.session['id'])
    if'photo' in request.FILES:
        photo=request.FILES['photo']
        obj.photo= photo
        obj.save()

    obj.name = name
    obj.place = place
    obj.post = post
    obj.pin = pin
    obj.phone = phone
    obj.email = email
    obj.gender = gender
    obj.qualification = qualification
    obj.save()

    messages.success(request, 'Hod added successfully')
    return redirect('/myapp/view_hod/')


def edit_student(request,id):
    request.session['id']=id
    data = STUDENT_table.objects.get(id=id)
    course = COUSE_table.objects.all()
    return render(request,'admin/editstudent.html',{'data':data,'course':course})

def edit_student_post(request):
    name = request.POST['name']
    course = request.POST['course']
    place = request.POST['place']
    district = request.POST['district']
    post = request.POST['post']
    pin = request.POST['pin']
    phone = request.POST['phone']
    email = request.POST['email']
    gender = request.POST['gender']
    skill = request.POST['skill']
    qualification = request.POST['qualification']

    student = STUDENT_table.objects.get(id=request.session['id'])

    student.name = name
    student.COURSE_id = course
    student.place = place
    student.district = district
    student.post = post
    student.pin = pin
    student.phone = phone
    student.email = email
    student.gender = gender
    student.skill = skill
    student.qualification = qualification

    if 'photo' in request.FILES:
        photo = request.FILES['photo']
        student.photo = photo

    student.save()
    messages.success(request, 'student added successfully')
    return redirect('/myapp/view_student/')

def block_unblock_student(request,id,status):
    ab=STUDENT_table.objects.get(id=id)
    ab.status=status
    ab.save()
    return redirect('/myapp/view_student/')



def view_allocatedhod(request):
    ab = ALLOCATION_table.objects.all()
    return render(request, 'admin/viewallocatedhod.html',{'data':ab})

# def view_carriculamupdates(request):
#     ab = .objects.all()
#     return render(request, 'admin/viewcarriculamupdates.html',{'data':ab})

# def view_complaint(request):
#     ab = COMPLAINT_table.objects.all()
#     return render(request, 'admin/viewcomplaint.html',{'data':ab})

def viewcurriculumupdate(request,id):
    ab = REQUEST_TO_PLACEMENTCELL_table.objects.filter(PLACEMENTCELL_id=id)
    return render(request, 'admin/viewcarriculamupdates.html',{'data':ab})


def accept_curriculumupdate(request,id):
  ob=REQUEST_TO_PLACEMENTCELL_table.objects.get(id=id)
  ob.status="Accepted"
  ob.save()
  messages.success(request, "Approved")
  return redirect('/myapp/viewcurriculumupdate/')

def reject_curriculumupdate(request,id):
    ob = REQUEST_TO_PLACEMENTCELL_table.objects.get(id=id)
    ob.status = "Rejected"
    ob.save()
    return redirect('/myapp/viewcurriculumupdate/')





def admin_view_feedback(request):
    ab = FEEDBACK_table.objects.all()
    return render(request, 'admin/viewfeedback.html',{'data':ab})

def view_placementofficer(request):
    ab = PLACEMENTCELL_table.objects.all()
    return render(request, 'admin/viewplacementofficer.html',{'data':ab})

def accept_placementofficer(request,id):
  ob=PLACEMENTCELL_table.objects.get(id=id)
  ob.status="Accepted"
  ob.save()
  messages.success(request, "Approved")
  return redirect('/myapp/view_placementofficer/')

def reject_placementofficer(request,id):
    ob = PLACEMENTCELL_table.objects.get(id=id)
    ob.status = "Rejected"
    ob.save()
    return redirect('/myapp/view_placementofficer/')

def view_complaint(request):
    ab = COMPLAINT_table.objects.all()
    return render(request, 'admin/viewcomplaint.html', {'data': ab})

def send_reply(request,id):
    request.session['rid']=id
    return render(request, 'admin/sendreply.html')


def send_reply_post(request):
    reply=request.POST["reply"]
    COMPLAINT_table.objects.filter(id=request.session['rid']).update(reply=reply)
    return redirect('/myapp/view_complaint/')


def send_score(request,id):
    request.session['rid']=id
    return render(request, 'admin/sendperfomancescore.html')



def send_score_post(request):
    score=request.POST["score"]
    ATTENDWORKSHOP_REQUEST_table.objects.filter(id=request.session['rid']).update(score=score)
    return redirect('/myapp/view_workshop_request/')



def organize_workshop(request):
    return render(request, 'admin/organizeworkshop.html')



def organiz_workshop_post(request):
    workshop_name=request.POST["workshop_name"]
    details=request.POST["details"]
    ab=WORKSHOP_table()
    ab.workshop_name=workshop_name
    ab.details=details
    ab.date= datetime.datetime.today()
    ab.time= datetime.datetime.today()
    ab.LOGIN=request.user
    ab.save()
    return redirect('/myapp/vieworganizeworkshop/')



def vieworganizeworkshop(request):
    ab=WORKSHOP_table.objects.all()
    return render(request,'admin/vieworganizeworkshop.html',{'data':ab})


def changepassword_admin(request):
    return render(request,'admin/changepassword.html')



def change_password_post(request):
    if not request.user.is_authenticated:
        messages.error(request,"you must be logged in to change your password.")
        return redirect('/myapp/changepassword_admin/')

    current_password=request.POST['current_password']
    new_password=request.POST['new_password']
    confirm_password=request.POST['confirm_password']


    if check_password(current_password,request.user.password):
        if new_password==confirm_password:
            user=request.user
            user.set_password(confirm_password)
            user.save()
            messages.success(request,"Password Changed Successfully")
            return redirect('/myapp/changepassword_admin/')
        else:
            messages.error(request,"New Password And Confirm Password Do Not Match ")
            return redirect('/myapp/changepassword_admin/')
    else:
        messages.error(request, "Current Password is Incorrect")
        return redirect('/myapp/changepassword_admin/')

def View_certificate(request,id):
     obj = CERTIFICATE_table.objects.filter(STUDENT_id=id)
     return render(request, 'admin/viewcetificate.html', {'data': obj})


#########################################placementcel###################################




def placementcellhome(request):
    res=PLACEMENTCELL_table.objects.get(LOGIN=request.user.id)
    request.session['user_data'] = res.photo.url  # example field

    return render(request, 'placementcell/placementhome.html',{'user_data':res})

def changepassword_placement(request):
    res = PLACEMENTCELL_table.objects.get(LOGIN=request.user.id)
    return render(request,'placementcell/change_password.html',{'user_data':res})

def changepassword_post(request):
    if not request.user.is_authenticated:
        messages.error(request,"you must be logged in to change your password.")
        return redirect('/myapp/changepassword_placement/')

    current_password=request.POST['current_password']
    new_password=request.POST['new_password']
    confirm_password=request.POST['confirm_password']


    if check_password(current_password,request.user.password):
        if new_password==confirm_password:
            user=request.user
            user.set_password(confirm_password)
            user.save()
            messages.success(request,"Password Changed Successfully")
            return redirect('/myapp/changepassword_placement/')
        else:
            messages.error(request,"New Password And Confirm Password Do Not Match ")
            return redirect('/myapp/changepassword_placement/')
    else:
        messages.error(request, "Current Password is Incorrect")
        return redirect('/myapp/changepassword_placement/')
#
# def trending_skill(request):
#     print("aaaaaaa")
#     ab=fetch_all_courses_by_department()
#     res = PLACEMENTCELL_table.objects.get(LOGIN=request.user.id)
#     print(ab,"aaaaaaaaaaaaaaaa")
#     return render(request,'placementcell/indstry_trending.html',{'user_data':res})
#
# Optional: import print_result if you want to debug
def register(request):
    return render(request,'placementcell/register.html')


def registerpost(request):
    name=request.POST['name']
    place=request.POST['place']
    phone=request.POST['phone']
    email=request.POST['email']
    photo=request.FILES['photo']
    username=request.POST['username']
    password=request.POST['password']


    user= User.objects.create(username= username,password= make_password(password))
    user.save()

    user.groups.add(Group.objects.get(name='placementcell'))
    obj=PLACEMENTCELL_table()
    obj.LOGIN=user
    obj.name=name
    obj.place=place
    obj.photo=photo
    obj.phone=phone
    obj.email=email
    obj.status="pending"
    obj.save()
    return redirect('/myapp/login_get/')


def viewcarriculam_updates(request):
    res = PLACEMENTCELL_table.objects.get(LOGIN=request.user.id)
    ab = REQUEST_TO_PLACEMENTCELL_table.objects.all()
    return render(request, 'placementcell/viewcarriculam_updates.html', {'data': ab,'user_data':res})


def sendcarriculam_updates(request):
    return render(request, 'placementcell/sendcarriculamupdate.html')


def sendcarriculam_update_post(request):
    subject = request.POST['subject']
    date = request.POST['date']
    need = request.POST['need']



    obj=REQUEST_TO_PLACEMENTCELL_table()
    obj.PLACEMENTCELL = PLACEMENTCELL_table.objects.get(LOGIN=request.user.id)

    obj.subject = subject
    obj.date = datetime.datetime.today()
    obj.need = need
    obj.status = "pending"
    obj.save()
    return redirect('/myapp/viewcarriculam_updates/')



def viewapplied_student(request):
    obj=APPLICATION_table.objects.all()
    res = PLACEMENTCELL_table.objects.get(LOGIN=request.user.id)
    return render(request, 'placementcell/viewappliedstudent.html',{'data':obj,'user_data':res})


def view_vacancies(request):
    ab = VACCANCY_table.objects.all()
    res = PLACEMENTCELL_table.objects.get(LOGIN=request.user.id)

    return render(request, 'placementcell/view_vaccancy.html', {'data': ab,'user_data':res})

def add_vaccancy(request):
    ab=VACCANCY_table.objects.all()

    return render(request, 'placementcell/add_vaccancy.html',{'data':ab})


def add_vacancy_post(request):
    job = request.POST.get('job')
    company_name = request.POST.get('company_name')
    job_details = request.POST.get('job_details')
    vaccancy = request.POST.get('vaccancy')
    apply_from_date = request.POST.get('apply_from_date')
    apply_to_date = request.POST.get('apply_to_date')
    time_duration = request.POST.get('time_duration')
    post_details = request.POST.get('post_details')

    VACCANCY_table.objects.create(
        job=job,
        company_name=company_name,
        job_details=job_details,
        vaccancy=vaccancy,
        apply_from_date=apply_from_date,
        apply_to_date=apply_to_date,
        time_duration=time_duration,
        post_details=post_details
    )
    # messages.success(request, "Vacancy added successfully!")
    return redirect('/myapp/view_vacancies/')



def delete_vaccancy(request,id):
    ab=VACCANCY_table.objects.get(id=id).delete()
    return redirect('/myapp/view_vacancies/')



def accept_eligibility(request,id):
  ob=APPLICATION_table.objects.get(id=id)
  ob.status="Accepted"
  ob.save()
  return redirect('/myapp/viewapplied_student/')

def reject_eligibility(request,id):
    ob = APPLICATION_table.objects.get(id=id)
    ob.status = "Rejected"
    ob.save()
    return redirect('/myapp/viewapplied_student/')


def viewprofilee(request):
    ab = PLACEMENTCELL_table.objects.get(LOGIN=request.user.id)
    return render(request, 'placementcell/viewprofile_placement.html', {'user_data':ab})



def editprofilee(request):
    ab = PLACEMENTCELL_table.objects.get(LOGIN=request.user.id)
    return render(request, 'placementcell/editprofile.html', {'user_data': ab})


def editprofile_post(request):
    if request.method == "POST":
        ab = PLACEMENTCELL_table.objects.get(LOGIN=request.user)

        ab.name = request.POST['name']

        ab.place = request.POST['place']
        ab.phone = request.POST['phone']
        ab.email = request.POST['email']
        ab.save()

        return redirect('/myapp/viewprofilee/')





def viewsession(request):
    obj=WORKSHOP_table.objects.all()
    res = PLACEMENTCELL_table.objects.get(LOGIN=request.user.id)
    return render(request, 'placementcell/viewsession.html',{"data":obj,'user_data':res})





###########################################HOD#################################################################################################


def hod_home(request):
    return render(request,'Hod/hod_home.html')


def password(request):
    return render(request,'Hod/password.html')

def hod_view_feedback(request):
    ab = FEEDBACK_table.objects.all()
    return render(request, 'Hod/view__feedback.html',{'data':ab})


def view_complaint_hod(request):
    ab = COMPLAINT_hod_table.objects.filter(HOD__LOGIN_id=request.user.id)
    return render(request, 'Hod/view__complaint.html', {'data': ab})


def password_post(request):
    if not request.user.is_authenticated:
        messages.error(request,"you must be logged in to change your password.")
        return redirect('/myapp/password/')

    current_password=request.POST['current_password']
    new_password=request.POST['new_password']
    confirm_password=request.POST['confirm_password']
    print(current_password,new_password,confirm_password)


    if check_password(current_password,request.user.password):
        if new_password==confirm_password:
            user=request.user
            user.set_password(confirm_password)
            user.save()
            messages.success(request,"Password Changed Successfully")
            return redirect('/myapp/login_get/')
        else:
            messages.error(request,"New Password And Confirm Password Do Not Match ")
            return redirect('/myapp/password/')
    else:
        messages.error(request, "Current Password is Incorrect")
        return redirect('/myapp/password/')





def view_hodprofile(request):
    # ab = HOD_table.objects.get(LOGIN=request.user.id)
    # return render(request,'Hod/profile.html',{'data':ab})
    ab = HOD_table.objects.get(LOGIN=request.user.id)
    return render(request, 'Hod/profile.html', {'data': ab})




def edit_profile_hod(request):
     ab =  HOD_table.objects.get(LOGIN=request.user.id)
     return  render(request,'Hod/edit_profilehod.html',{'data':ab})

def editprofi_post(request):
    hod = HOD_table.objects.get(LOGIN=request.user.id)
    user = request.user

    hod.name = request.POST['name']
    hod.place = request.POST['place']
    hod.post = request.POST['post']
    hod.pin = request.POST['pin']
    hod.phone = request.POST['phone']
    hod.email = request.POST['email']
    hod.gender = request.POST['gender']
    hod.qualification = request.POST['qualification']
    user.first_name = request.POST.get('name')
    user.email = request.POST.get('email')

    if 'photo' in request.FILES:
        photo = request.FILES['photo']
        hod.photo = photo

        hod.save()
        user.save()
    messages.success(request, 'Hod added successfully')
    hod.save()

    return redirect('/myapp/view_hodprofile/')




def view_departments(request):
    # obj = DEPARTMENT_table.objects.all()
    # obj = HOD_table.objects.get(LOGIN=request.user.id)

    hod = HOD_table.objects.filter(LOGIN=request.user.id).first()
    allocations = ALLOCATION_table.objects.filter(HOD=hod).select_related('department')
    return render(request,'Hod/viewdepartments.html',{'data':allocations})



def view_students(request):
    dep=ALLOCATION_table.objects.get(HOD__LOGIN_id=request.user.id).department
    print(dep)
    obj = STUDENT_table.objects.filter(COURSE__Department_id=dep)
    return render(request,'Hod/viewstudents.html',{'data':obj})





def addsession_workshop(request):
    return render(request,'Hod/addsession_workshop.html')



def addsessionworkshop_post(request):
    workshop_name = request.POST["workshop_name"]
    details = request.POST["details"]
    ab = WORKSHOP_table()
    ab.workshop_name = workshop_name
    ab.details = details
    ab.date = datetime.datetime.today()
    ab.time = datetime.datetime.today()
    ab.LOGIN = request.user
    ab.save()
    return redirect('/myapp/addsession_workshop/')

def view_sessionworkshop(request):
    obj = WORKSHOP_table.objects.all()
    return render(request,'Hod/viewsession_workshop.html',{'data':obj})


def for_eligiblestudent(request):
    return render(request,'Hod/for_eligible_student.html')



def edit_studentss(request,id):
    request.session['id']=id
    data = STUDENT_table.objects.get(id=id)
    course = COUSE_table.objects.all()
    return render(request,'Hod/edit_studentss.html',{'data':data,'course':course})



def edit_studentss_post(request):
    name = request.POST['name']
    course = request.POST['course']
    place = request.POST['place']
    district = request.POST['district']
    post = request.POST['post']
    pin = request.POST['pin']
    phone = request.POST['phone']
    email = request.POST['email']
    gender = request.POST['gender']
    skill = request.POST['skill']
    qualification = request.POST['qualification']

    student = STUDENT_table.objects.get(id=request.session['id'])

    student.name = name
    student.COURSE_id = course
    student.place = place
    student.district = district
    student.post = post
    student.pin = pin
    student.phone = phone
    student.email = email
    student.gender = gender
    student.skill = skill
    student.qualification = qualification

    if 'photo' in request.FILES:
        photo = request.FILES['photo']
        student.photo = photo

    student.save()
    messages.success(request, 'student added successfully')
    return redirect('/myapp/view_students/')



##########################flutter##################################

def flutter_login(request):
    username = request.POST["username"]
    print(username)
    password = request.POST["password"]
    print(password)
    user = authenticate(request,username=username,password=password)
    if user is not None:
        login(request,user)
        if user.groups.filter(name="student").exists():
            if STUDENT_table.objects.filter(LOGIN=user.id,status='student'):
                print(user.id,'llllllllllllllll')
                return  JsonResponse({"task":"valid","type":"student","lid":user.id})
            else:
                return JsonResponse({'task': 'no'})
        else:
            return JsonResponse({'task':'no'})
    else:
        return JsonResponse({"task":"invalid",})


def student_send_complaint(request):
    lid=request.POST['lid']
    complaint=request.POST['complaint']
    ob=COMPLAINT_table()
    ob.STUDENT= STUDENT_table.objects.get(LOGIN_id=lid)
    ob.complaint= complaint
    ob.date=datetime.datetime.today()
    ob.reply= 'pending'
    ob.save()
    return JsonResponse({"task":"ok"})

def attendworkshop_request(request):
    lid = request.POST['lid']
    workshop = request.POST['WORKSHOP']
    ob=ATTENDWORKSHOP_REQUEST_table()
    ob.STUDENT = STUDENT_table.objects.get(LOGIN_id=lid)
    ob.date = datetime.datetime.today()
    ob.status = 'pending'
    ob.score=0
    ob.WORKSHOP_id= workshop
    ob.save()
    return JsonResponse({"task": "ok"})


def viewMycomplaints(request):
    lid=request.POST['lid']
    complaint=COMPLAINT_table.objects.filter(STUDENT__LOGIN_id=lid)


    complaints=[]
    for i in complaint:complaints.append({
        'id':str(i.id),
        'complaint':str(i.complaint),
        'reply':str(i.reply),
        'date':str(i.date),

    })
    return JsonResponse({'status':'ok','data':complaints})




def student_view_profile(request):
    lid=request.POST['lid']
    st=STUDENT_table.objects.get(LOGIN=lid)
    return JsonResponse({'status':'ok',
                         'name':st.name,
                         'place':st.place,
                         'post':st.post,
                         'pin':st.pin,
                         'phone':st.phone,
                         'email':st.email,
                         'gender':st.gender,
                         'skill':st.skill,
                         'qualification':st.qualification,
                         'district':st.district,
                         'photo':request.build_absolute_uri(st.photo.url)if st.photo else"",


     })




def student_edit_profile(request):
    lid = request.POST.get('lid')

    print(request.FILES.get('photo'),"hhhhhhhhhhhhhhhhhhh")
    student = STUDENT_table.objects.get(LOGIN_id=lid)

    # try:
    #     student = STUDENT_table.objects.get(LOGIN_id=lid)
    # except:
    #     return JsonResponse({'status': 'error', 'message': 'User not found'})


    student.name = request.POST.get('name')
    student.place = request.POST.get('place')
    student.district = request.POST.get('district')
    student.post = request.POST.get('post')
    student.pin = request.POST.get('pin')
    student.phone = request.POST.get('phone')
    student.email = request.POST.get('email')
    student.gender = request.POST.get('gender')
    student.skill = request.POST.get('skill')
    student.qualification = request.POST.get('qualification')

    if 'photo' in request.FILES:
        student.photo = request.FILES['photo']

    student.save()

    return JsonResponse({'status': 'ok'})


def view_feedback(request):
    lid=request.POST['lid']
    f=FEEDBACK_table.objects.filter(STUDENT_LOGIN_id=lid)
    ab=[]
    for i in f:
        ab.append({
            'id':str(i.id),
            'rating':i.rating,
            "feedback":i.feedback,
            "date":i.date })
        return  JsonResponse({'status':'ok','data':ab})



def send_feedback(request):
    comp=request.POST['feedback']
    lid=request.POST['lid']
    rating=request.POST['rating']
    lob=FEEDBACK_table()
    lob.STUDENT=STUDENT_table.objects.get(LOGIN_id=lid)
    lob.feedback=comp
    lob.rating=rating
    lob.date=datetime.datetime.now().today()
    lob.save()
    return JsonResponse({'task':'ok'})


def student_Forgot_password(request):
    email=request.POST['email']
    us=STUDENT_table.objects.filter(email=email)
    if us.exists():
        lg = STUDENT_table.objects.get(email=email)
        bb = User.objects.get(id=lg.LOGIN_id)
        password = random.randint(00000000, 99999999)
        bb.set_password(str(password))
        bb.save()

        sender_email = "thejaswinirk542@gmail.com"
        sender_password = "ufol tfan limq hmew"
        subject = "Forget Password From SignSpeak"

        body = f"Your New Password Is ({password}).Please Change Password After Login."

        msg = MIMEMultipart()

        msg['From'] = sender_email

        msg['To'] = email

        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(host="smtp.gmail.com", port=587)

        server.starttls()

        server.login(sender_email, sender_password)

        server.sendmail(sender_email, email, msg.as_string())

        server.quit()

        print(f"Email sent successfully to {email}")
        return JsonResponse({"status":"ok"})


    return JsonResponse({"status":"no"})




def view_workshopstudent(request):
    lid=request.POST['lid']
    f=WORKSHOP_table.objects.all()
    ab=[]
    for i in f:
        ab.append({
            'id':str(i.id),
            'workshop_name':i.workshop_name,
            "details":i.details,
            "time":i.time,
            "date":i.date })
    return  JsonResponse({'status':'ok','data':ab})

def view_score(request):
    lid = request.POST['lid']
    f = ATTENDWORKSHOP_REQUEST_table.objects.filter(STUDENT__LOGIN_id=lid)
    print(f,"kkkkkkkkkkkkkkkk")
    ab = []
    for i in f:
        ab.append({
            'id': str(i.id),
            'STUDENT': i.WORKSHOP.workshop_name,
            "status": i.status,
            "score": i.score,
            "date": i.date})
    return JsonResponse({'status': 'ok', 'data': ab})



def view_workshoprequest(request):
    lid = request.POST['lid']
    f = ATTENDWORKSHOP_REQUEST_table.objects.filter(STUDENT__LOGIN_id=lid)
    ab = []
    for i in f:
        ab.append({
            'id': str(i.id),
            'wid': i.WORKSHOP.id,
            'WORKSHOP': i.WORKSHOP.workshop_name,
            'details': i.WORKSHOP.details,
            'WORKSHOP_date': i.WORKSHOP.date,
            "status": i.status,
            "date": i.date})
    return JsonResponse({'status': 'ok', 'data': ab})


def change_passwordpost_student(request):
    try:

        oldpassword = request.POST.get('current_password')
        newpassword = request.POST.get('new_password')
        confirmpassword = request.POST.get('confirm_password')
        lid = request.POST.get('lid')

        # Check empty fields
        if not oldpassword or not newpassword or not confirmpassword:
            return JsonResponse({
                'status': 'error',
                'message': 'All fields are required'
            })

        # Check password match
        if newpassword != confirmpassword:
            return JsonResponse({
                'status': 'error',
                'message': 'Password mismatch'
            })


        try:
            user = User.objects.get(id=lid)
        except User.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'User not found'
            })


        if not check_password(oldpassword, user.password):
            return JsonResponse({
                'status': 'error',
                'message': 'Incorrect current password'
            })


        user.set_password(newpassword)
        user.save()

        return JsonResponse({
            'status': 'ok',
            'message': 'Password changed successfully'
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })




def student_upload_certificate(request):
    lid=request.POST['lid']
    wid=request.POST['wid']
    certificate=request.FILES['certificate']
    lob=CERTIFICATE_table()
    lob.STUDENT=STUDENT_table.objects.get(LOGIN_id=lid)
    lob.WORKSHOP=WORKSHOP_table.objects.get(id=wid)
    lob.certificate=certificate
    lob.date=datetime.datetime.now().today()
    lob.save()
    return JsonResponse({'task':'ok'})




#
# def viewcertificate(request):
#
#     lid = request.POST['lid']
#     wid = request.POST['wid']
#
#     certificate = CERTIFICATE_table.objects.filter(STUDENT__LOGIN_id=lid,WORKSHOP_id=wid )
#
#     certificats = []
#
#     for i in certificate:
#
#         certificats.append({
#
#             'id': str(i.id),
#             'date': str(i.date),
#             'photo': request.build_absolute_uri(certificate.certificate.url) if certificate.certificate else"",
#
#         })
#
#     return JsonResponse({'status': 'ok', 'data': certificats })




def viewcertificate(request):
    lid = request.POST.get('lid')
    wid = request.POST.get('wid')

    certificates = CERTIFICATE_table.objects.filter(STUDENT__LOGIN_id=lid, WORKSHOP_id=wid)

    certificats = []

    for cert in certificates:
        certificats.append({
            'id': str(cert.id),
            'date': str(cert.date),
            'photo': request.build_absolute_uri(cert.certificate.url) if cert.certificate else "",
        })

    return JsonResponse({'status': 'ok', 'data': certificats})




def view_vacancy_api(request):
    data = VACCANCY_table.objects.all()
    temp = []
    for i in data:

        temp.append({
            'id': i.id,  # CRITICAL: Flutter needs this to send 'vid'
            'job': i.job,
            'company_name': i.company_name,
            'job_details': i.job_details,
            'vaccancy': i.vaccancy,
            'apply_from_date': i.apply_from_date,
            'apply_to_date': i.apply_to_date,
            'time_duration': i.time_duration,
            'post_details': i.post_details
        })
    return JsonResponse({'status': 'ok', 'data': temp})


import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import APPLICATION_table, STUDENT_table, VACCANCY_table


@csrf_exempt  # Added this in case you haven't handled CSRF in Flutter
def send_application(request):
    if request.method == "POST":
        lid = request.POST.get('lid')
        vid = request.POST.get('vid')
        file = request.FILES.get('file')

        # Robust validation
        if not lid or not vid or not file:
            return JsonResponse({'task': 'error', 'message': 'All fields (lid, vid, file) are required'})

        try:
            # Getting the student based on the LOGIN_id (Link to User table)
            student = STUDENT_table.objects.get(LOGIN_id=lid)

            # Getting the specific vacancy
            vacancy = VACCANCY_table.objects.get(id=vid)

            # Create and save the application
            application = APPLICATION_table(
                STUDENT=student,
                VACCANCY=vacancy,
                status="pending",
                date=datetime.date.today(),
                file=file
            )
            application.save()

            return JsonResponse({'task': 'ok', 'status': 'ok'})  # Added status for Flutter consistency

        except STUDENT_table.DoesNotExist:
            return JsonResponse({'task': 'error', 'message': 'Student record not found'})
        except VACCANCY_table.DoesNotExist:
            return JsonResponse({'task': 'error', 'message': 'Vacancy no longer exists'})
        except Exception as e:
            return JsonResponse({'task': 'error', 'message': str(e)})

    else:
        return JsonResponse({'task': 'error', 'message': 'Only POST requests are allowed'})


from django.http import JsonResponse
from .models import APPLICATION_table, STUDENT_table


def view_application_status_api(request):
    # We get the lid from the POST request
    lid = request.POST.get('lid')

    if not lid:
        return JsonResponse({'status': 'error', 'message': 'User ID missing'})

    try:
        # Find the student instance associated with this login
        student = STUDENT_table.objects.get(LOGIN_id=lid)

        # Filter applications for this specific student
        # We use select_related to efficiently get job info from the VACCANCY table
        applications = APPLICATION_table.objects.filter(STUDENT=student)

        temp = []
        for app in applications:
            temp.append({
                'id': app.id,
                'job_title': app.VACCANCY.job,  # Fetching title from Vacancy table
                'company': app.VACCANCY.company_name,
                'apply_date': app.date.strftime('%Y-%m-%d'),
                'status': app.status,
                'file_url': app.file.url if app.file else ""
            })

        return JsonResponse({'status': 'ok', 'data': temp})

    except STUDENT_table.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Student record not found'})

# def student_view_industyreport(request):
#     """View trending skills for HOD's department only"""
#     lid=request.POST['lid']
#     try:
#         # Get HOD's department
#         allocation = STUDENT_table.objects.get(LOGIN_id=lid)
#         hod_department = allocation.department.department
#         print(hod_department, "viewwwww")
#         # Get filtered data (Only this department)
#         data = get_hod_cached_career_data(refresh=False, department=hod_department)
#         context = {
#             'career_data': data,
#             'total_courses': data.get('total_courses', 0),
#             'hod_department': hod_department,
#         }
#         return JsonResponse({"status":"ok",context})
#     except ALLOCATION_table.DoesNotExist:
#         context = {
#             'error': "Your department allocation was not found.",
#             'career_data': None,
#             'hod_department': None
#         }
#         return render(request, 'Hod/viewindustry_reports.html', context)
#     except Exception as e:
#         context = {
#             'error': f"Failed to load industry trends: {str(e)}",
#             'career_data': None,
#             'hod_department': None
#         }
#         return render(request, 'Hod/viewindustry_reports.html', context)
#
#



from django.http import JsonResponse

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import STUDENT_table


@csrf_exempt
@require_http_methods(["POST"])
def student_view_industry_report(request):
    """
    Students can view trending industry skills with High Priority Recommendations.
    """
    try:
        lid = request.POST.get('lid')
        if not lid:
            return JsonResponse({'status': 'error', 'message': 'Login ID (lid) is required'}, status=400)

        # Get student
        student = STUDENT_table.objects.get(LOGIN_id=lid)

        # Get Department
        if hasattr(student, 'department') and student.department:
            hod_department = student.department.department
        elif hasattr(student, 'COURSE') and student.COURSE and hasattr(student.COURSE, 'Department'):
            hod_department = student.COURSE.Department.department
        else:
            hod_department = "Unknown Department"

        # Fetch career data
        career_data = get_hod_cached_career_data(
            refresh=False,
            department=hod_department
        )

        # ====================== HIGH PRIORITY SKILLS ======================
        high_priority_skills = extract_high_priority_skills(career_data)

        response_data = {
            'career_data': career_data,
            'total_courses': career_data.get('total_courses', 0) if isinstance(career_data, dict) else 0,
            'hod_department': hod_department,
            'student_name': getattr(student, 'name', getattr(student, 'student_name', 'Student')),
            'high_priority_skills': high_priority_skills,  # ← New Field
        }

        return JsonResponse({
            'status': 'ok',
            'message': 'Success',
            'data': response_data
        }, status=200)

    except STUDENT_table.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Student record not found.'}, status=404)

    except Exception as e:
        print("Error in student_view_industry_report:", str(e))
        return JsonResponse({
            'status': 'error',
            'message': f'Failed to load industry trends: {str(e)}'
        }, status=500)


def extract_high_priority_skills(career_data: dict) -> list:
    """
    Extract recommended high priority skills (Technical + Domain Skills)
    """
    priority_skills = set()  # Using set to avoid duplicates

    try:
        departments = career_data.get('departments', {})

        for courses in departments.values():
            if not isinstance(courses, list):
                continue

            for course in courses:
                skills = course.get('skills', {})

                # High Priority = Technical Skills + Domain Skills
                for category in ['Technical_Skills', 'Domain_Skills']:
                    skill_list = skills.get(category, [])
                    if isinstance(skill_list, list):
                        for skill in skill_list:
                            if skill and isinstance(skill, str):
                                priority_skills.add(skill.strip())
    except:
        pass

    # Convert to list and sort
    return sorted(list(priority_skills))
