from django import forms 
from .models import Student, Student_record
from django.contrib.auth.forms import AuthenticationForm

class CustomAuthenticationForm(AuthenticationForm):
    remember_me = forms.BooleanField(required=False, initial=False, label='Remember me')

class StudentForm(forms.Form):
    class Meta:
        model = Student
        fields = '__all__'

class RecordForm(forms.Form):
    class Meta:
        model = Student_record
        fields = '__all__'