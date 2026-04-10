import datetime
import email
from pickle import GET

from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User,Group




# Create your views here.
from pip._vendor.requests import post

from myapp.models import *


def admin_home(request):
    return render(request,'home.html')

def logout(request):
    return render(request,'login.html')




def login_get(request):
    return render(request,'login.html')


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
                login(request,user)
                return redirect('/myapp/placementcellhome/')
            elif user.groups.filter(name="hod").exists():
                login(request,user)
                return redirect('/myapp/hod_home')
            else:
                return redirect('/myapp/login_get/')
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




def delete_course(request):
    ab=COUSE_table.objects.get(id=id).delete()
    return redirect('/myapp/view_course/')

def view_course(request,id):
    request.session['did']=id
    ab=COUSE_table.objects.all()
    return render(request, 'admin/viewcourse.html',{'data':ab})


def add_course(request):
    return render(request,'admin/addcourse.html')



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

def view_allocation(request,id):
    department=request.session['hid']=id
    ab=ALLOCATION_table.objects.all()
    return render(request,'admin/viewallocatedhod.html',{'data':ab})


def allocatehod(request):
    ab=DEPARTMENT_table.objects.all()
    return render(request, 'admin/allocatehod.html',{'data':ab})



def allocate_post(request):
    department = request.POST['Department']
    hid = request.session['hid']

    if ALLOCATION_table.objects.filter(HOD_id=hid).exists():

        messages.success(request, 'This HOD is already allocated to a department')
        return redirect('/myapp/view_hod/')

    else:

        ab = ALLOCATION_table()

        ab.HOD = HOD_table.objects.get(id=hid)
        ab.department = DEPARTMENT_table.objects.get(id=department)
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



def view_allocatedhod(request):
    ab = ALLOCATION_table.objects.all()
    return render(request, 'admin/viewallocatedhod.html',{'data':ab})

# def view_carriculamupdates(request):
#     ab = .objects.all()
#     return render(request, 'admin/viewcarriculamupdates.html',{'data':ab})

# def view_complaint(request):
#     ab = COMPLAINT_table.objects.all()
#     return render(request, 'admin/viewcomplaint.html',{'data':ab})





def view_feedback(request):
    ab = FEEDBACK_table.objects.all()
    return render(request, 'admin/viewfeedback.html',{'data':ab})

def view_placementofficer(request):
    ab = PLACEMENTCELL_table.objects.all()
    return render(request, 'admin/viewplacementofficer.html',{'data':ab})

def accept_placementofficer(request,id):
  ob=PLACEMENTCELL_table.objects.get(id=id)
  ob.status="Accepted"
  ob.save()
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
    COMPLAINT_table.objects.filter(id=request.session['rid']).update(reply=reply,status='replyed')
    return redirect('/myapp/view_complaint/')



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


def changepasswordd(request):
    return render(request,'admin/changepassword.html')



def change_password_post(request):
    if not request.user.is_authenticated:
        messages.error(request,"you must be logged in to change your password.")
        return redirect('/myapp/changepasswordd/')

    current_password=request.POST['current_password']
    new_password=request.POST['new_password']
    confirm_password=request.POST['confirm_password']


    if check_password(current_password,request.user.password):
        if new_password==confirm_password:
            user=request.user
            user.set_password(confirm_password)
            user.save()
            messages.success(request,"Password Changed Successfully")
            return redirect('/myapp/changepasswordd/')
        else:
            messages.error(request,"New Password And Confirm Password Do Not Match ")
            return redirect('/myapp/changepasswordd/')
    else:
        messages.error(request, "Current Password is Incorrect")
        return redirect('/myapp/changepasswordd/')






#########################################placementcel###################################




def placementcellhome(request):
    return render(request,'placementcell/home.html')

def changepassword(request):
    return render(request,'placementcell/change_password.html')

def changepassword_post(request):
    if not request.user.is_authenticated:
        messages.error(request,"you must be logged in to change your password.")
        return redirect('/myapp/changepassword/')

    current_password=request.POST['current_password']
    new_password=request.POST['new_password']
    confirm_password=request.POST['confirm_password']


    if check_password(current_password,request.user.password):
        if new_password==confirm_password:
            user=request.user
            user.set_password(confirm_password)
            user.save()
            messages.success(request,"Password Changed Successfully")
            return redirect('/myapp/changepassword/')
        else:
            messages.error(request,"New Password And Confirm Password Do Not Match ")
            return redirect('/myapp/changepassword/')
    else:
        messages.error(request, "Current Password is Incorrect")
        return redirect('/myapp/changepassword/')



def register(request):
    return render(request,'placementcell/register.html')


def registerpost(request):
    name=request.POST['name']
    place=request.POST['place']
    phone=request.POST['phone']
    email=request.POST['email']
    username=request.POST['username']
    password=request.POST['password']




    user= User.objects.create(username= username,password= make_password(password))
    user.save()

    user.groups.add(Group.objects.get(name='placementcell'))

    obj=PLACEMENTCELL_table()
    obj.LOGIN=user
    obj.name=name
    obj.place=place
    obj.phone=phone
    obj.email=email
    obj.status="pending"
    obj.save()
    return redirect('/myapp/login_get/')


def viewcarriculam_updates(request):
    ab = REQUEST_TO_PLACEMENTCELL_table.objects.all()
    return render(request, 'placementcell/viewcarriculam_updates.html', {'data': ab})


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
    return render(request, 'placementcell/viewappliedstudent.html',{'data':obj})

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
    return render(request, 'placementcell/viewprofile.html',{'data': ab})



def editprofilee(request):
    ab = PLACEMENTCELL_table.objects.get(LOGIN=request.user.id)
    return render(request, 'placementcell/editprofile.html', {'data': ab})


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
    return render(request, 'placementcell/viewsession.html',{"data":obj})





###########################################HOD#################################################################################################


def hod_home(request):
    return render(request,'Hod/hod_home.html')


def password(request):
    return render(request,'Hod/password.html')




def password_post(request):
    if not request.user.is_authenticated:
        messages.error(request,"you must be logged in to change your password.")
        return redirect('/myapp/password/')

    current_password=request.POST['current_password']
    new_password=request.POST['new_password']
    confirm_password=request.POST['confirm_password']


    if check_password(current_password,request.user.password):
        if new_password==confirm_password:
            user=request.user
            user.set_password(confirm_password)
            user.save()
            messages.success(request,"Password Changed Successfully")
            return redirect('/myapp/password/')
        else:
            messages.error(request,"New Password And Confirm Password Do Not Match ")
            return redirect('/myapp/password/')
    else:
        messages.error(request, "Current Password is Incorrect")
        return redirect('/myapp/password/')





def view_hodprofile(request):
    ab = HOD_table.objects.get(LOGIN=request.user.id)
    return render(request,'Hod/profile.html',{'data':ab})


def edit_profile_hod(request,id):
     ab = HOD_table.objects.get(id=request.session['id'])
     return  render(request,'Hod/edit_profilehod.html',{'data':ab})

def editprofi_post(request):
    if request.method == "POST":
        hod = HOD_table.objects.get(LOGIN=request.user)

        hod.name = request.POST['name']
        hod.place = request.POST['place']
        hod.post = request.POST['post']
        hod.pin = request.POST['pin']
        hod.phone = request.POST['phone']
        hod.email = request.POST['email']
        hod.gender = request.POST['gender']
        hod.qualification = request.POST['qualification']

        if 'photo' in request.FILES:
            photo = request.FILES['photo']
            hod.photo = photo

            hod.save()
        messages.success(request, 'Hod added successfully')

        return redirect('/myapp/view_hodprofile/')




def view_departments(request):
    # obj = DEPARTMENT_table.objects.all()
    obj = HOD_table.objects.get(LOGIN=request.user.id)
    return render(request,'Hod/viewdepartments.html',{'data':obj})



def view_students(request):
    obj = STUDENT_table.objects.all()
    return render(request,'Hod/viewstudents.html',{'data':obj})



def view_industyreport(request):
    return render(request,'Hod/viewindustry_reports.html')

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