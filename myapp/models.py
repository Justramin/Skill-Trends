from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class DEPARTMENT_table(models.Model):
    department= models.CharField(max_length=100)
    details= models.CharField(max_length=100)


class COUSE_table(models.Model):
    Department= models.ForeignKey(DEPARTMENT_table,on_delete=models.CASCADE)
    course= models.CharField(max_length=100)
    details= models.CharField(max_length=100)


class STUDENT_table(models.Model):
    LOGIN= models.ForeignKey(User,on_delete=models.CASCADE)
    COURSE= models.ForeignKey(COUSE_table,on_delete=models.CASCADE)

    name= models.CharField(max_length=100)
    place= models.CharField(max_length=100)
    post= models.CharField(max_length=100)
    pin= models.IntegerField()
    phone= models.BigIntegerField()
    email= models.CharField(max_length=100)
    photo= models.FileField()
    gender= models.CharField(max_length=100)
    skill= models.CharField(max_length=100)
    qualification = models.CharField(max_length=100)



class FEEDBACK_table(models.Model):
    STUDENT= models.ForeignKey(STUDENT_table,on_delete=models.CASCADE)
    feedback = models.CharField(max_length=100)
    rating= models.FloatField()
    date= models.DateField()


class COMPLAINT_table(models.Model):
    STUDENT= models.ForeignKey(STUDENT_table,on_delete=models.CASCADE)
    complaint= models.CharField(max_length=100)
    date=models.DateField()
    reply= models.CharField(max_length=100)



class JOB_table(models.Model):
    job=  models.CharField(max_length=100)
    company_name=  models.CharField(max_length=100)
    job_details=  models.CharField(max_length=100)



class VACCANCY_table(models.Model):
    JOB= models.ForeignKey(JOB_table,on_delete=models.CASCADE)
    vaccancy= models.CharField(max_length=100)
    apply_from_date=models.TextField()
    apply_to_date= models.DateField()
    time_duration= models.CharField(max_length=100)
    post_details= models.CharField(max_length=100)



class APPLICATION_table(models.Model):
    STUDENT = models.ForeignKey(STUDENT_table, on_delete=models.CASCADE)
    VACCANCY = models.ForeignKey(VACCANCY_table,on_delete=models.CASCADE)
    file=models.FileField()
    date=models.DateField()
    status= models.CharField(max_length=100)


class HOD_table(models.Model):
    LOGIN = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    place = models.CharField(max_length=100)
    post = models.CharField(max_length=100)
    pin = models.IntegerField()
    phone = models.BigIntegerField()
    email = models.CharField(max_length=100)
    gender = models.CharField(max_length=100)
    qualification= models.CharField(max_length=100)
    photo= models.FileField()




class ALLOCATION_table(models.Model):
    HOD= models.ForeignKey(HOD_table, on_delete=models.CASCADE)
    Department = models.ForeignKey(DEPARTMENT_table, on_delete=models.CASCADE)
    date = models.DateField()
    status= models.CharField(max_length=100)



class PLACEMENTCELL_table(models.Model):
    LOGIN = models.ForeignKey(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    place = models.CharField(max_length=100)
    phone = models.BigIntegerField()
    email = models.CharField(max_length=100)
    status= models.CharField(max_length=100)




class REQUEST_TO_PLACEMENTCELL_table(models.Model):
    PLACEMENTCELL= models.ForeignKey(PLACEMENTCELL_table, on_delete=models.CASCADE)
    subject=  models.CharField(max_length=100)
    date = models.DateField()
    need=models.CharField(max_length=100)
    status= models.CharField(max_length=100)




class WORKSHOP_table(models.Model):
    LOGIN = models.ForeignKey(User, on_delete=models.CASCADE)
    workshop_name=  models.CharField(max_length=100)
    details=  models.CharField(max_length=100)
    date = models.DateField()
    time= models.TimeField()



class CHAT_table(models.Model):
    fromid=models.ForeignKey(User,on_delete=models.CASCADE,related_name="fuser")
    toid=models.ForeignKey(User,on_delete=models.CASCADE,related_name="touser")
    date = models.DateField()
    msg=models.CharField(max_length=100)
    status = models.CharField(max_length=100)






