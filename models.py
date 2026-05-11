from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.

class TodoItem(models.Model):
    text = models.CharField(max_length=255)
    due_date = models.DateField()

class Student(models.Model):
    no = models.CharField(max_length=100, default='DEFAULT VALUE', blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, default="")
    department = models.CharField(max_length=100, blank=True, default="")
    shift = models.CharField(max_length=100, default='DEFAULT VALUE', blank=True, null=True)


class Student_record(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True, default="")
    course = models.CharField(max_length=100, blank=True)  # If you want to store course
    # month_id = models.CharField(max_length=20, blank=True, null=True, default="")    
    DAY_1 = models.CharField(max_length=100, default='DEFAULT VALUE', blank=True, null=True)
    DAY_2 = models.CharField(max_length=100, default='DEFAULT VALUE', blank=True, null=True)
    DAY_3 = models.CharField(max_length=100, default='DEFAULT VALUE', blank=True, null=True)
    DAY_4 = models.CharField(max_length=100, default='DEFAULT VALUE', blank=True, null=True)
    DAY_5 = models.CharField(max_length=100, default='DEFAULT VALUE', blank=True, null=True)
    DAY_6 = models.CharField(max_length=100, default='DEFAULT VALUE', blank=True, null=True)
    DAY_7 = models.CharField(max_length=100, default='DEFAULT VALUE', blank=True, null=True)
    DAY_8 = models.CharField(max_length=100, default='DEFAULT VALUE', blank=True, null=True)
    DAY_9 = models.CharField(max_length=100, default='DEFAULT VALUE', blank=True, null=True)
    DAY_10 = models.CharField(max_length=100, default='DEFAULT VALUE', blank=True, null=True)
    DAY_11 = models.CharField(max_length=100, default='DEFAULT VALUE', blank=True, null=True)
    DAY_12 = models.CharField(max_length=100, default='DEFAULT VALUE', blank=True, null=True)
    DAY_13 = models.CharField(max_length=100, default='DEFAULT VALUE', blank=True, null=True)
    DAY_14 = models.CharField(max_length=100, default='DEFAULT VALUE', blank=True, null=True)
    DAY_15 = models.CharField(max_length=100, default='DEFAULT VALUE', blank=True, null=True)
    DAY_16 = models.CharField(max_length=100, default='DEFAULT VALUE', blank=True, null=True)
    DAY_17 = models.CharField(max_length=100, default='DEFAULT VALUE', blank=True, null=True)
    DAY_18 = models.CharField(max_length=100, default='DEFAULT VALUE', blank=True, null=True)
    DAY_19 = models.CharField(max_length=100, default='DEFAULT VALUE', blank=True, null=True)
    DAY_20 = models.CharField(max_length=100, default='DEFAULT VALUE', blank=True, null=True)
    DAY_21 = models.CharField(max_length=100, default='DEFAULT VALUE', blank=True, null=True)
    DAY_22 = models.CharField(max_length=100, default='DEFAULT VALUE', blank=True, null=True)
    DAY_23 = models.CharField(max_length=100, default='DEFAULT VALUE', blank=True, null=True)
    DAY_24 = models.CharField(max_length=100, default='DEFAULT VALUE', blank=True, null=True)
    DAY_25 = models.CharField(max_length=100, default='DEFAULT VALUE', blank=True, null=True)
    DAY_26 = models.CharField(max_length=100, default='DEFAULT VALUE', blank=True, null=True)
    DAY_27 = models.CharField(max_length=100, default='DEFAULT VALUE', blank=True, null=True)
    DAY_27 = models.CharField(max_length=100, default='DEFAULT VALUE', blank=True, null=True)
    DAY_28 = models.CharField(max_length=100, default='DEFAULT VALUE', blank=True, null=True)
    DAY_29 = models.CharField(max_length=100, default='DEFAULT VALUE', blank=True, null=True)
    DAY_30 = models.CharField(max_length=100, default='DEFAULT VALUE', blank=True, null=True)
    DAY_31 = models.CharField(max_length=100, default='DEFAULT VALUE', blank=True, null=True)




class Course(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()

class Students_Result(models.Model):
    name = models.CharField(max_length=100)
    # department = models.CharField(max_length=50)
    pathology_class = models.CharField(max_length=100)
    pathology_practical = models.CharField(max_length=100)
    chemical_pathology = models.CharField(max_length=100)
    chemical_pathology_practical = models.CharField(max_length=100)
    microbiology = models.CharField(max_length=100)
    microbiology_practical = models.CharField(max_length=100)
    pharmacology = models.CharField(max_length=100)
    pharmacology_practical= models.CharField(max_length=100)
    hematology=    models.CharField(max_length=100)
    hematology_practical = models.CharField(max_length=100)
    # Add other fields as needed

    def __str__(self):
        return f"{self.name} ({self.department})"


class FormResponse(models.Model):
    student_name = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    message = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    c_myself = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)  # Tracks submission time

    def __str__(self):
        return f"{self.user_name} - {self.subject}"