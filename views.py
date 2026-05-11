from django.shortcuts import render, redirect, get_object_or_404 
from django.http import HttpResponse
from .code.full_codes import (new_attendance,extract_attendance_times,analyze_attendance, 
                             MBBCH_Pathology, MBBCH_Chemical_Pathology, send_mail_from_df, 
                             send_Chemical_pathology_mail, MBBCH_Microbiology, send_Microbiology_mail, 
                             MBBCH_Pharmacology, send_Pharmacology_mail, MBBCH_Hematology, send_Hematology_mail,
                             BDS_Pathology, send_BDS_Pathology_mail,
                             BDS_Chemical_Pathology, send_BDS_Chemical_pathology_mail,
                             BDS_Microbiology, send_BDS_Microbiology_mail,
                             BDS_Pharmacology, send_BDS_Pharmacology_mail, BDS_Hematology, send_BDS_Hematology_mail
                             )
import pandas as pd
import os
from django.conf import settings
from pathlib import Path
import calendar
import openpyxl
import datetime
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
import datetime, re
import io
from .forms import StudentForm
from tablib import Dataset
from io import StringIO
import tempfile
from .models import Student, Student_record, Students_Result
# accounts/views.py
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from .forms import CustomAuthenticationForm
from django.urls import reverse_lazy
from io import StringIO

def home(request):
    return render(request, 'home.html' )

class CustomLoginView(LoginView):
    # Use the standard registration path so the template under
    # core/templates/registration/login.html is picked up.
    template_name = 'registration/login.html'
    authentication_form = CustomAuthenticationForm
    redirect_authenticated_user = True  # if already logged in redirect to LOGIN_REDIRECT_URL

    def form_valid(self, form):
        # Standard login first
        resp = super().form_valid(form)
        remember = form.cleaned_data.get('remember_me')
        if remember:
            # 2 weeks expiry
            self.request.session.set_expiry(1209600)  # seconds
        else:
            # expire when user closes browser
            self.request.session.set_expiry(0)
        return resp

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')  # or rely on LOGOUT_REDIRECT_URL in settings

def courses(request):
    return render(request, 'temp/courses.html' )

def bds_courses(request):
    return render(request, 'temp/bds_courses.html' )

    
def calendar(request):
    days = range(1, 32)
    hours = range(0, 24)
    minutes = range(0, 60)
    slots = [1, 2, 3]  

    context = {
                "days": days,
                "slots": slots,
                "hours": hours,
                "minutes": minutes,
            }        
    
    
    table_html = None   # default → nothing to show

    if request.method == "POST":
        try:
            dataset = Dataset()

            # Upload Excel files
            new_result = request.FILES["my_file"]
            df_info = pd.read_excel(new_result, sheet_name="Shifts")
            request.session["student_info"] = df_info.to_json(orient="split")

            new_record = request.FILES["my_record"]
            df_record = pd.read_excel(new_record, sheet_name="Logs") # Attendance data
            
            names = df_info["Name"].values
            department = df_info["Department"].values
           

          
            cleaned_df = new_attendance(df_record, department, names)
            print(cleaned_df.head(10))
            
            
            
                       
            # Save students
            imported_data = dataset.load(df_info.to_csv(index=False), format="csv")
            for data in imported_data:
                student = Student(
                    no=data[0],
                    name=data[1],
                    department=data[2],
                    shift=data[3],
                )
                student.save()

            # Save attendance logs
            imported_record = dataset.load(cleaned_df.to_csv(index=False), format="csv")
            for row in imported_record:
                student_data = {}
                for i in range(min(31, len(row))):
                    student_data[f"DAY_{i+1}"] = row[i]
                Student_record.objects.create(
                    **student_data)

            # Collect day conditions         
            day_conditions = []
            for day in days:
                for slot in slots:
                    course = request.POST.get(f"course{slot}_{day}")
                    start_hour = request.POST.get(f"start_hour{slot}_{day}")
                    start_min = request.POST.get(f"start_min{slot}_{day}")
                    end_hour = request.POST.get(f"end_hour{slot}_{day}")
                    end_min = request.POST.get(f"end_min{slot}_{day}")

                    if course and all([start_hour, start_min, end_hour, end_min]):
                        try:
                            start_dt = datetime.time(int(start_hour), int(start_min))
                            end_dt = datetime.time(int(end_hour), int(end_min))
                            day_conditions.append({
                                "day_col": f"DAY{day}",
                                "slot": slot,
                                "course": course,
                                "start": start_dt,
                                "end": end_dt,
                            })
                        except ValueError as e:
                            print(f"⚠️ Time parse error for day {day} slot {slot}: {e}")
                            continue


            # Run analysis
            extracted = extract_attendance_times(cleaned_df, df_info, day_conditions)
            report = analyze_attendance(extracted, df_info)
            request.session["results"] = report.to_json(orient="split")
            # departments= cleaned_df['Department']
            # print(departments.head(10))
            
            bds_result = BDS_Pathology(report, cleaned_df)
            print("DEBUG: MBBCH Pathology rows:", len(bds_result))
            print("DEBUG: BDS pathology result:", bds_result.head(10))
            mail_bds_1=send_BDS_Pathology_mail(bds_result)
            tmp_file6 = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
            bds_result.to_json(tmp_file6, orient="split")
            tmp_file6.close()
            request.session["bds_cleaned"] = tmp_file6.name
            print("DEBUG: Session keys currently stored:", request.session.keys())

            result = MBBCH_Pathology(report, cleaned_df)
            mail_1=send_mail_from_df(result)
            print("DEBUG: pathology result:", result.head(10))
            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
            result.to_json(tmp_file, orient="split")
            tmp_file.close()
            request.session["cleaned_path"] = tmp_file.name
#-----------------------------------------------------------------------------------
            chem_bds_result = BDS_Chemical_Pathology(report, cleaned_df)
            print("DEBUG: MBBCH Pathology rows:", len(bds_result))
            mail_bds_2=send_BDS_Chemical_pathology_mail(chem_bds_result)
            print("DEBUG: pathology result:", chem_bds_result.head(10))
            tmp_file7 = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
            chem_bds_result.to_json(tmp_file7, orient="split")
            tmp_file7.close()
            request.session["chem_bds_cleaned"] = tmp_file7.name
            print("DEBUG: Session keys currently stored:", request.session.keys())
           
            chem_result = MBBCH_Chemical_Pathology(report, cleaned_df)
            mail_2=send_Chemical_pathology_mail(chem_result)
            tmp_file2 = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
            chem_result.to_json(tmp_file2, orient="split")
            tmp_file2.close()
            request.session["chem_cleaned"] = tmp_file2.name
            print("DEBUG: Session keys currently stored:", request.session.keys())
#----------------------------------------------------------------------------------- 
            pharm_bds_result = BDS_Pharmacology(report, cleaned_df)
            mail_bds_4=send_BDS_Pharmacology_mail(pharm_bds_result)
            print("DEBUG: pathology result:", pharm_bds_result.head(10))
            tmp_file9 = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
            pharm_bds_result.to_json(tmp_file9, orient="split")
            tmp_file9.close()
            request.session["pharm_bds_cleaned"] = tmp_file9.name
            print("DEBUG: Session keys currently stored:", request.session.keys())

            pharm_result = MBBCH_Pharmacology(report, cleaned_df)
            mail_4=send_Pharmacology_mail(pharm_result)
            print("DEBUG: pathology result:", pharm_result.head(10))     
            tmp_file4 = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
            pharm_result.to_json(tmp_file4, orient="split")
            tmp_file4.close()
            request.session["pharm_cleaned"] = tmp_file4.name
            print("DEBUG: Session keys currently stored:", request.session.keys())
#-----------------------------------------------------------------------------------    
            micro_bds_result = BDS_Microbiology(report, cleaned_df)
            mail_bds_3=send_BDS_Microbiology_mail(micro_bds_result)
            print("DEBUG: pathology result:", micro_bds_result.head(10))
            tmp_file8 = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
            micro_bds_result.to_json(tmp_file8, orient="split")
            tmp_file8.close()
            request.session["micro_bds_cleaned"] = tmp_file8.name
            print("DEBUG: Session keys currently stored:", request.session.keys())

            micro_result = MBBCH_Microbiology(report, cleaned_df)
            mail_3=send_Microbiology_mail(micro_result)
            print("DEBUG: pathology result:", micro_result.head(10))
            tmp_file3 = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
            micro_result.to_json(tmp_file3, orient="split")
            tmp_file3.close()
            request.session["micro_cleaned"] = tmp_file3.name
            print("DEBUG: Session keys currently stored:", request.session.keys())
#-----------------------------------------------------------------------------------         
            hema_bds_result = BDS_Hematology(report, cleaned_df)
            mail_bds_5=send_BDS_Hematology_mail(hema_bds_result)
            print("DEBUG: pathology result:", hema_bds_result.head(10))
            tmp_file10 = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
            hema_bds_result.to_json(tmp_file10, orient="split")
            tmp_file10.close()
            request.session["hema_bds_cleaned"] = tmp_file10.name
            print("DEBUG: Session keys currently stored:", request.session.keys())

            hema_result = MBBCH_Hematology(report, cleaned_df)
            mail_5=send_Hematology_mail(hema_result)
            print("DEBUG: pathology result:", pharm_result.head(10)) 
            tmp_file5 = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
            hema_result.to_json(tmp_file5, orient="split")
            tmp_file5.close()
            request.session["hema_cleaned"] = tmp_file5.name
            print("DEBUG: Session keys currently stored:", request.session.keys())
#-----------------------------------------------------------------------------------

            # Sending mails
            # For MBBCh students

            # mail_1=send_mail_from_df(result)
            # mail_1
            # mail_2=send_Chemical_pathology_mail(chem_result)
            # mail_2
            # mail_3=send_Microbiology_mail(micro_result)
            # mail_3
            # mail_4=send_Pharmacology_mail(pharm_result)
            # mail_4
            # mail_5=send_Hematology_mail(hema_result)
            # mail_5

            # # Sending mails
            # # For BDS students
            # mail_bds_1=send_BDS_Pathology_mail(bds_result)
            # mail_bds_1
            # mail_bds_2=send_BDS_Chemical_pathology_mail(chem_bds_result)
            # mail_bds_2
            # mail_bds_3=send_BDS_Microbiology_mail(micro_bds_result)
            # mail_bds_3
            # mail_bds_4=send_BDS_Pharmacology_mail(pharm_bds_result)
            # mail_bds_4
            # mail_bds_5=send_BDS_Hematology_mail(hema_bds_result)
            # mail_bds_5

            # Convert to HTML for display
            if not report.empty:
                table_html = report.to_html(classes="table table-bordered", index=False)

        except Exception as e:
            table_html = f"<p style='color:red;'>Error while processing: {e}</p>"

    # Always render the same template and include dropdown data
    return render(request, "temp/calendar.html", {
        "days": days,
        "slots": slots,
        "hours": hours,
        "minutes": minutes,
        "table": table_html,
    })

#-----------------------------------------------------------------------------------------------------

def results(request):
    
    report_json = request.session.get("results")

    if not report_json:
        return render(request, "temp/results_view.html", {
            "message": "No results available. Please upload files first."
        })

    # Rebuild DataFrame from stored JSON string. Wrap in StringIO to avoid
    # FutureWarning about passing literal JSON to pandas.read_json.
    from io import StringIO
    report = pd.read_json(StringIO(report_json), orient="split")

    print("DEBUG: Report shape =", report.shape)  # <--- Debug line
    print(report.head())  # <--- Debug line

    if report.empty:
        return render(request, "temp/results_view.html", {
            "message": "Report generated but has no rows. Check your input files."
        })

    # Convert to HTML for display
    table_html = report.to_html(classes="table table-bordered", index=False)

    return render(request, "temp/results_view.html", {
        "table": table_html
    })


#-----------------------------------------------------------------------------------------------------
def download_results(request):
    report_json = request.session.get("results")

    if not report_json:
        return HttpResponse("No results to download.", status=400)

    from io import StringIO
    report = pd.read_json(StringIO(report_json), orient="split")

    # Save to in-memory buffer
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        report.to_excel(writer, index=False, sheet_name="Attendance Report")
    buffer.seek(0)

    # Send as downloadable response
    response = HttpResponse(
        buffer,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="attendance_report.xlsx"'
    return response

#-----------------------------------------------------------------------------------------------------
def M_Histopathology(request):
    report_json = request.session.get("cleaned_path")

    if not report_json:
        return render(request, "temp/M_Histopathology.html", {
            "message": "No results available. Please upload files."
        })

    from io import StringIO
    import os
    try:
        if isinstance(report_json, str) and os.path.exists(report_json):
            report = pd.read_json(report_json, orient="split")
        else:
            report = pd.read_json(StringIO(report_json), orient="split")
    except Exception as e:
        print(f"Error loading B pharm report: {e}")
        return render(request, "temp/M_Histopathology.html", {"message": f"Error loading report: {e}"})

    print("DEBUG: Report shape =", report.shape)

    if report.empty:
        return render(request, "temp/M_Histopathology.html", {
            "message": "Report generated but has no rows. Check your input files."
        })

    # Optionally send email once per session
    try:
        if not request.session.get('histo_bds_emailed'):
            try:
                send_BDS_Microbiology_mail(report)
                request.session['histo_bds_emailed'] = True
            except Exception as e:
                print('Failed to send MBBCH Histopathology email:', e)
    except Exception:
        pass

    table_html = report.to_html(classes="table table-bordered", index=False)
    return render(request, "temp/M_Histopathology.html", {"table": table_html})
#-----------------------------------------------------------------------------------------------------

def M_Chemical_Pathology(request):
    report_json = request.session.get("chem_cleaned")

    if not report_json:
        return render(request, "temp/M_Chemical_Pathology.html", {
            "message": "No results available. Please upload files."
        })

    from io import StringIO
    import os
    try:
        if isinstance(report_json, str) and os.path.exists(report_json):
            report = pd.read_json(report_json, orient="split")
        else:
            report = pd.read_json(StringIO(report_json), orient="split")
    except Exception as e:
        print(f"Error loading B pharm report: {e}")
        return render(request, "temp/M_Chemical_Pathology.html", {"message": f"Error loading report: {e}"})

    print("DEBUG: Report shape =", report.shape)

    if report.empty:
        return render(request, "temp/M_Chemical_Pathology.html", {
            "message": "Report generated but has no rows. Check your input files."
        })

    # Optionally send email once per session
    try:
        if not request.session.get('chem_MBBDS_emailed'):
            try:
                send_BDS_Microbiology_mail(report)
                request.session['chem_MBBDS_emailed'] = True
            except Exception as e:
                print('Failed to send MBBDS Chemical Pathology email:', e)
    except Exception:
        pass

    table_html = report.to_html(classes="table table-bordered", index=False)
    return render(request, "temp/M_Chemical_Pathology.html", {"table": table_html})
#-----------------------------------------------------------------------------------------------------

def M_Microbiology(request):
    report_json = request.session.get("micro_cleaned")

    if not report_json:
        return render(request, "temp/M_Microbiology.html", {
            "message": "No results available. Please upload files."
        })

    from io import StringIO
    import os
    try:
        if isinstance(report_json, str) and os.path.exists(report_json):
            report = pd.read_json(report_json, orient="split")
        else:
            report = pd.read_json(StringIO(report_json), orient="split")
    except Exception as e:
        print(f"Error loading B pharm report: {e}")
        return render(request, "temp/M_Microbiology.html", {"message": f"Error loading report: {e}"})

    print("DEBUG: Report shape =", report.shape)

    if report.empty:
        return render(request, "temp/M_Microbiology.html", {
            "message": "Report generated but has no rows. Check your input files."
        })

    # Optionally send email once per session
    try:
        if not request.session.get('micro_MBBDS_emailed'):
            try:
                send_BDS_Microbiology_mail(report)
                request.session['micro_MBBDS_emailed'] = True
            except Exception as e:
                print('Failed to send MBBDS Microbiology email:', e)
    except Exception:
        pass

    table_html = report.to_html(classes="table table-bordered", index=False)
    return render(request, "temp/M_Microbiology.html", {"table": table_html})
#-----------------------------------------------------------------------------------------------------
def M_Pharmacology(request):
    report_json = request.session.get("pharm_cleaned")

    if not report_json:
        return render(request, "temp/M_Pharmacology.html", {
            "message": "No results available. Please upload files."
        })

    # Rebuild DataFrame: support both a stored filename (temp file) or a JSON string
    from io import StringIO
    import os
    try:
        if isinstance(report_json, str) and os.path.exists(report_json):
            # session contains a filepath
            report = pd.read_json(report_json, orient="split")
        else:
            # session contains a JSON literal
            report = pd.read_json(StringIO(report_json), orient="split")
    except Exception as e:
        print(f"Error loading pharm report: {e}")
        return render(request, "temp/M_Pharmacology.html", {"message": f"Error loading report: {e}"})

    print("DEBUG: Report shape =", report.shape)

    if report.empty:
        return render(request, "temp/M_Pharmacology.html", {
            "message": "Report generated but has no rows. Check your input files."
        })

    # Optionally send email once per session
    try:
        email_status = None
        if not request.session.get('pharm_emailed'):
            try:
                send_Pharmacology_mail(report)
                request.session['pharm_emailed'] = True
                email_status = 'Email sent successfully.'
            except Exception as e:
                print('Failed to send Pharmacology email:', e)
                email_status = f'Failed to send email: {e}'
    except Exception:
        pass

    table_html = report.to_html(classes="table table-bordered", index=False)
    context = {"table": table_html}
    if 'email_status' in locals() and email_status:
        context['email_status'] = email_status
    return render(request, "temp/M_Pharmacology.html", context)
#-----------------------------------------------------------------------------------------------------
def M_Hematology(request):
    report_json = request.session.get("hema_cleaned")

    if not report_json:
        return render(request, "temp/M_Hematology.html", {
            "message": "No results available. Please upload files."
        })

    from io import StringIO
    import os
    try:
        if isinstance(report_json, str) and os.path.exists(report_json):
            report = pd.read_json(report_json, orient="split")
        else:
            report = pd.read_json(StringIO(report_json), orient="split")
    except Exception as e:
        print(f"Error loading hema report: {e}")
        return render(request, "temp/M_Hematology.html", {"message": f"Error loading report: {e}"})

    print("DEBUG: Report shape =", report.shape)

    if report.empty:
        return render(request, "temp/M_Hematology.html", {
            "message": "Report generated but has no rows. Check your input files."
        })

    # Optionally send email once per session
    try:
        email_status = None
        if not request.session.get('hema_emailed'):
            try:
                send_Hematology_mail(report)
                request.session['hema_emailed'] = True
                email_status = 'Email sent successfully.'
            except Exception as e:
                print('Failed to send Hematology email:', e)
                email_status = f'Failed to send email: {e}'
    except Exception:
        pass

    table_html = report.to_html(classes="table table-bordered", index=False)
    context = {"table": table_html}
    if 'email_status' in locals() and email_status:
        context['email_status'] = email_status
    return render(request, "temp/M_Hematology.html", context)
    
#-----------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------            
def B_Histopathology(request):
    report_json = request.session.get("bds_cleaned")

    if not report_json:
        return render(request, "temp/B_Histopathology.html", {
            "message": "No results available. Please upload files."
        })

    from io import StringIO
    import os
    try:
        if isinstance(report_json, str) and os.path.exists(report_json):
            report = pd.read_json(report_json, orient="split")
        else:
            report = pd.read_json(StringIO(report_json), orient="split")
    except Exception as e:
        print(f"Error loading B pharm report: {e}")
        return render(request, "temp/B_Histopathology.html", {"message": f"Error loading report: {e}"})

    print("DEBUG: Report shape =", report.shape)

    if report.empty:
        return render(request, "temp/B_Histopathology.html", {
            "message": "Report generated but has no rows. Check your input files."
        })

    # Optionally send email once per session
    try:
        if not request.session.get('histo_bds_emailed'):
            try:
                send_BDS_Microbiology_mail(report)
                request.session['histo_bds_emailed'] = True
            except Exception as e:
                print('Failed to send BDS Histopathology email:', e)
    except Exception:
        pass

    table_html = report.to_html(classes="table table-bordered", index=False)
    return render(request, "temp/B_Histopathology.html", {"table": table_html})
#--------------------------------------------------------------------------------
def B_Chemical_Pathology(request):
    report_json = request.session.get("chem_bds_cleaned")

    if not report_json:
        return render(request, "temp/B_Chemical_Pathology.html", {
            "message": "No results available. Please upload files."
        })

    from io import StringIO
    import os
    try:
        if isinstance(report_json, str) and os.path.exists(report_json):
            report = pd.read_json(report_json, orient="split")
        else:
            report = pd.read_json(StringIO(report_json), orient="split")
    except Exception as e:
        print(f"Error loading B pharm report: {e}")
        return render(request, "temp/B_Chemical_Pathology.html", {"message": f"Error loading report: {e}"})

    print("DEBUG: Report shape =", report.shape)

    if report.empty:
        return render(request, "temp/B_Chemical_Pathology.html", {
            "message": "Report generated but has no rows. Check your input files."
        })

    # Optionally send email once per session
    try:
        if not request.session.get('chem_bds_emailed'):
            try:
                send_BDS_Microbiology_mail(report)
                request.session['chem_bds_emailed'] = True
            except Exception as e:
                print('Failed to send BDS Chemical Pathology email:', e)
    except Exception:
        pass

    table_html = report.to_html(classes="table table-bordered", index=False)
    return render(request, "temp/B_Chemical_Pathology.html", {"table": table_html})
#--------------------------------------------------------------------------------
def B_Microbiology(request):
    report_json = request.session.get("micro_bds_cleaned")

    if not report_json:
        return render(request, "temp/B_Microbiology.html", {
            "message": "No results available. Please upload files."
        })

    from io import StringIO
    import os
    try:
        if isinstance(report_json, str) and os.path.exists(report_json):
            report = pd.read_json(report_json, orient="split")
        else:
            report = pd.read_json(StringIO(report_json), orient="split")
    except Exception as e:
        print(f"Error loading B pharm report: {e}")
        return render(request, "temp/B_Microbiology.html", {"message": f"Error loading report: {e}"})

    print("DEBUG: Report shape =", report.shape)

    if report.empty:
        return render(request, "temp/B_Microbiology.html", {
            "message": "Report generated but has no rows. Check your input files."
        })

    # Optionally send email once per session
    try:
        if not request.session.get('micro_bds_emailed'):
            try:
                send_BDS_Microbiology_mail(report)
                request.session['micro_bds_emailed'] = True
            except Exception as e:
                print('Failed to send BDS Microbiology email:', e)
    except Exception:
        pass

    table_html = report.to_html(classes="table table-bordered", index=False)
    return render(request, "temp/B_Microbiology.html", {"table": table_html})
#--------------------------------------------------------------------------------
def B_Pharmacology(request):
    report_json = request.session.get("pharm_bds_cleaned")

    if not report_json:
        return render(request, "temp/B_Pharmacology.html", {
            "message": "No results available. Please upload files."
        })

    from io import StringIO
    import os
    try:
        if isinstance(report_json, str) and os.path.exists(report_json):
            report = pd.read_json(report_json, orient="split")
        else:
            report = pd.read_json(StringIO(report_json), orient="split")
    except Exception as e:
        print(f"Error loading B pharm report: {e}")
        return render(request, "temp/B_Pharmacology.html", {"message": f"Error loading report: {e}"})

    print("DEBUG: Report shape =", report.shape)

    if report.empty:
        return render(request, "temp/B_Pharmacology.html", {
            "message": "Report generated but has no rows. Check your input files."
        })

    # Optionally send email once per session
    try:
        if not request.session.get('pharm_bds_emailed'):
            try:
                send_BDS_Pharmacology_mail(report)
                request.session['pharm_bds_emailed'] = True
            except Exception as e:
                print('Failed to send BDS Pharmacology email:', e)
    except Exception:
        pass

    table_html = report.to_html(classes="table table-bordered", index=False)
    return render(request, "temp/B_Pharmacology.html", {"table": table_html})
    

def B_Hematology(request):
    report_json = request.session.get("hema_bds_cleaned")

    if not report_json:
        return render(request, "temp/B_Hematology.html", {
            "message": "No results available. Please upload files."
        })

    from io import StringIO
    import os
    try:
        if isinstance(report_json, str) and os.path.exists(report_json):
            report = pd.read_json(report_json, orient="split")
        else:
            report = pd.read_json(StringIO(report_json), orient="split")
    except Exception as e:
        print(f"Error loading B hema report: {e}")
        return render(request, "temp/B_Hematology.html", {"message": f"Error loading report: {e}"})

    print("DEBUG: Report shape =", report.shape)

    if report.empty:
        return render(request, "temp/B_Hematology.html", {
            "message": "Report generated but has no rows. Check your input files."
        })

    # Optionally send email once per session
    try:
        if not request.session.get('hema_bds_emailed'):
            try:
                send_BDS_Hematology_mail(report)
                request.session['hema_bds_emailed'] = True
            except Exception as e:
                print('Failed to send BDS Hematology email:', e)
    except Exception:
        pass

    table_html = report.to_html(classes="table table-bordered", index=False)
    return render(request, "temp/B_Hematology.html", {"table": table_html})
#-----------------------------------------------------------------------------------------------------



def Upload_result(request):
    upload_result = request.session.get("results")  # Use the full calendar result

    if not upload_result:
        return HttpResponse("No results available. Please upload files first.", status=400)
    if request.method == "POST":
        month_id = request.POST.get("month_id")
        print("Request method:", request.method)
        print("POST data:", request.POST)
        if not month_id:
            return HttpResponse("Please provide a month ID.", status=400)
        try:
            df_info = pd.read_json(upload_result, orient="split")
            count_created = 0
            count_updated = 0
            for _, row in df_info.iterrows():
                name = row.get("Name") or row.get("STUDENT NAME", "")
                if not name:
                    continue  # Skip rows with no name
                obj, created = Students_Result.objects.update_or_create(
                    name=name,
                    month_id=month_id,
                    defaults={
                        **{f"DAY_{i+1}": row.get(f"DAY{i+1}", "") for i in range(31)},
                        # Add other fields as needed, e.g.:
                        # "department": row.get("Department", ""),
                    }
                )
                if created:
                    count_created += 1
                else:
                    count_updated += 1
            msg = f"Results uploaded for month '{month_id}'. Created: {count_created}, Updated: {count_updated}."
            return HttpResponse(msg, status=200)
        except Exception as e:
            return HttpResponse(f"Error while uploading results: {e}", status=500)
    else:
        return HttpResponse("Invalid request method.", status=405)





# class PostListView(ListView):
#     model = Student
#     template_name = 'temp/student_list.html'
#     context_object_name = 'posts'
#     ordering = ['date_posted']
#     paginate_by = 10  # Number of students per page

# class PostDetailView(DetailView):
#     model = Student

def view_results(request):
    month_id = request.GET.get("month_id")
    if not month_id:
        return HttpResponse("Please provide a month ID in the query string.", status=400)
    results = Students_Result.objects.filter(month_id=month_id).order_by('name')
    if not results.exists():
        return HttpResponse(f"No results found for month '{month_id}'.", status=404)
    return render(request, "temp/view_results.html", {
        "results": results,
        "month_id": month_id,
        "range": range(1, 32)
    })


def uploaded(request):
    mon=input("Enter month ID: ")
    return render(request, "temp/uploaded.html", mon)

from .login import NameForm
from .models import FormResponse
def get_name(request):
    detail = None  # Initialize detail to avoid reference errors

    if request.method == 'POST':
        form = NameForm(request.POST)  # Validate submitted data
        if form.is_valid():
            detail = {
                'student_name': form.cleaned_data['student_name'],  # Ensure lowercase field names
                'registration_number': form.cleaned_data['registration_number'],
                'department': form.cleaned_data['department'],
                'sender': form.cleaned_data['sender'],
                'c_myself': form.cleaned_data['c_myself'],
            }

            # Save data in the database
            response = FormResponse(
                student_name=detail['student_name'],  # Ensure consistency with model field
                registration_number=detail['registration_number'],
                department=detail['department'],
                sender=detail['sender'],
                c_myself=detail['c_myself']
            )
            response.save()

            # Redirect to avoid resubmission issues
            return redirect('submission_success', form_id=response.id)  

    else:
        form = NameForm()  # Empty form for GET request

    return render(request, 'temp/logins.html', {'form': form, 'detail': detail})

def submission_success(request, form_id):
    response = FormResponse.objects.get(id=form_id)
    return render(request, 'temp/success.html', {'response': response})


def debug_template_dirs(request):
    """Debug endpoint: shows which template directories Django will search.
    Useful for verifying the runtime template search path (especially in bundled EXE runs).
    """
    tpl_settings = settings.TEMPLATES[0]
    dirs = tpl_settings.get('DIRS', [])
    app_dirs = tpl_settings.get('APP_DIRS', False)
    body = [f"APP_DIRS: {app_dirs}"]
    body.append("TEMPLATE DIRS:")
    for d in dirs:
        body.append(f" - {d}")
    return HttpResponse('<br>'.join(body))


def debug_meipass(request):
    """When running from a PyInstaller bundle, list files under sys._MEIPASS
    so we can see what resources were extracted into the temp folder.
    """
    import sys
    out = []
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        meip = Path(sys._MEIPASS)
        out.append(f'_MEIPASS: {meip}')
        # list a few levels to avoid huge output
        for p in sorted(meip.rglob('*'))[:200]:
            out.append(str(p.relative_to(meip)))
    else:
        out.append('Not running in a frozen PyInstaller environment.')
    return HttpResponse('<br>'.join(out))