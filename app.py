import os
from flask import Flask, request,jsonify,render_template
import pandas as pd
import webview
import requests
from dotenv import load_dotenv
load_dotenv()
import sys

from data_access import read_data, save_data as save_excel, FILE_PATH

if getattr(sys, 'frozen', False):
    app_path = sys._MEIPASS  # For bundled app
else:
    app_path = os.path.dirname(__file__)  # For development environment

new_file_path = os.path.join(app_path, 'studentdata.xlsx')


app = Flask(__name__, template_folder='template')
window=webview.create_window('Noble Institute of Science and Technology (NIST)',app,width=1920, height=1080,resizable=True,fullscreen=False)

@app.route('/')
def index():
    df = read_data()

    total_students = len(df)
    paid_count = 0
    unpaid_count = 0
    total_collected = 0
    sem_totals = [0, 0, 0, 0]

    def safe_fee(x):
        try:
            val = str(x).replace(',', '').strip()
            if val in ['', 'nan', 'None']:
                return 0.0
            return float(val)
        except:
            return 0.0

    for _, row in df.iterrows():
        sem_fees = []
        for i, sem in enumerate(range(1, 5)):
            fee = safe_fee(row.get(f"Sem {sem} Fee", 0))
            sem_fees.append(fee)
            sem_totals[i] += fee
            total_collected += fee

        if any(f > 0 for f in sem_fees):
            paid_count += 1
        else:
            unpaid_count += 1

    course_counts = {}
    if 'Course Name' in df.columns:
        course_counts = df['Course Name'].value_counts().to_dict()

    return render_template('main.html',
        total_students=total_students,
        paid_count=paid_count,
        unpaid_count=unpaid_count,
        total_collected=round(total_collected, 2),
        sem_totals=[round(s, 2) for s in sem_totals],
        course_labels=list(course_counts.keys()),
        course_data=list(course_counts.values())
    )
@app.route('/student-entry')
def student_entry():
    return render_template('entry.html')

@app.route('/student-search')
def student_search():
    return render_template('index.html')

@app.route('/update-sem-data', methods=['GET'])
def semester_data():
    return render_template('sem.html')

@app.route('/send-fee-alert')
def fee_alert():
    return render_template('fee_alert.html')
#//////////////////////////////////////////////////////dashboard/////////////////////////////////




#////////////////////////////////////// Save Student Data in Doc section Starts \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

@app.route('/save-data', methods=['POST'])
def save_data():
    try:
        data = request.get_json()
        roll_no = data.get("rollNo")
        admission_no = data.get("admissionNo")
        full_name = data.get("fullName")
        gender = data.get("gender")
        father_name = data.get("fatherName")
        mother_name = data.get("motherName")
        address = data.get("address")
        email = data.get("email")
        phone = data.get("phone")
        aadhaar_no = data.get("aadhaarNo")
        dob = data.get("dob")
        course_name = data.get("courseName")
        admission_date = data.get("admissionDate")

        if not all([roll_no, admission_no, full_name, gender, father_name, mother_name,
                    address, email, phone, aadhaar_no, dob, course_name, admission_date]):
            return jsonify({"error": "All fields are required"}), 400

        columns = [
            "Roll No", "Admission No", "Full Name", "Gender",
            "Father Name", "Mother Name", "Address", "Email", "Phone",
            "Aadhaar No", "Date of Birth", "Course Name", "Date of Admission"
        ]
        new_row = pd.DataFrame([{
            "Roll No": roll_no,
            "Admission No": admission_no,
            "Full Name": full_name,
            "Gender": gender,
            "Father Name": father_name,
            "Mother Name": mother_name,
            "Address": address,
            "Email": email,
            "Phone": phone,
            "Aadhaar No": aadhaar_no,
            "Date of Birth": dob,
            "Course Name": course_name,
            "Date of Admission": admission_date
        }])
        if os.path.exists(FILE_PATH):
            existing_df = read_data()
            df = pd.concat([existing_df, new_row], ignore_index=True)
        else:
            df = new_row

        df = df[columns]

        try:
            save_excel(df)
            return jsonify({"message": "Data saved successfully!"})
        except Exception as e:
            print(f"Error saving Excel file: {e}")
            return jsonify({"error": f"Error saving data. Please try again. {str(e)}"}), 500

    except Exception as e:
        print(f"Error in save_data: {e}")
        return jsonify({"error": f"Error in saving data. {str(e)}"}), 500
    
#////////////////////////////////////// Save Student Data in Doc section Ends \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\



#////////////////////////////////////// get Student form Doc section Starts \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

@app.route('/get-details', methods=['POST'])
def get_details():
    try:
        data = request.get_json()
        roll_no = data.get("rollNo")
        
        df = read_data()

        # Find the student row
        student_row = df[df["Roll No"] == roll_no]

        if not student_row.empty:
            student_data = student_row.iloc[0]

            return render_template('student.html',
                n = "Student Found!",
                na = student_data["Full Name"],
                roll = student_data["Roll No"],
                admission_no = student_data["Admission No"],
                gender = student_data["Gender"],
                father_name = student_data["Father Name"],
                mother_name = student_data["Mother Name"],
                address = student_data["Address"],
                email = student_data["Email"],
                phone = student_data["Phone"],
                aadhaar_no = student_data["Aadhaar No"],
                dob = student_data["Date of Birth"],
                course_name = student_data["Course Name"],
                admission_date = student_data["Date of Admission"],
                sem1_fee = student_data.get("Sem 1 Fee", ""),
                sem1_result = student_data.get("Sem 1 Result", ""),
                sem2_fee = student_data.get("Sem 2 Fee", ""),
                sem2_result = student_data.get("Sem 2 Result", ""),
                sem3_fee = student_data.get("Sem 3 Fee", ""),
                sem3_result = student_data.get("Sem 3 Result", ""),
                sem4_fee = student_data.get("Sem 4 Fee", ""),
                sem4_result = student_data.get("Sem 4 Result", "")
            )
        else:
            return "Student Not Found", 404
    except Exception as e:
        return str(e), 500
    
#////////////////////////////////////// get Student Details Doc section Ends \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\



#////////////////////////////////////// Update semister data section Starts \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

@app.route('/update-sem-data', methods=['POST'])
def update_semester_data():
    try:
        data = request.get_json()
        roll_no_raw = data.get("rollNo")

        if isinstance(roll_no_raw, float):
            roll_no = int(roll_no_raw)
        elif isinstance(roll_no_raw, str):
            roll_no = int(roll_no_raw.strip())
        else:
            roll_no = int(roll_no_raw)

        semester = data.get("semester")
        fee = data.get("fee")
        result = data.get("result")

        if not all([roll_no, semester, fee, result]):
            return jsonify({"error": "All fields are required"}), 400

        if not os.path.exists(FILE_PATH):
            return jsonify({"error": "Student file not found."}), 404

        df = read_data()
        df["Roll No"] = pd.to_numeric(df["Roll No"], errors='coerce')
        df = df.dropna(subset=["Roll No"])
        df["Roll No"] = df["Roll No"].astype(int)

        match = df["Roll No"] == roll_no

        if not match.any():
            return jsonify({"error": "Roll No not found."}), 404

        fee_col = f"Sem {semester} Fee"
        result_col = f"Sem {semester} Result"
        df.loc[match, fee_col] = fee
        df.loc[match, result_col] = result
        save_excel(df)

        return jsonify({"message": f"Semester {semester} data updated successfully!"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500    

#////////////////////////////////////// Update semister data section Ends \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\



#/////////////////////// getting value from form and posting values to the pass section strats \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
        
def safe_get(row, column_name):
    return row[column_name] if column_name in row and pd.notnull(row[column_name]) else "0"

@app.route('/', methods=['POST'])
def getvalue():
    name = request.form['name']  # Get the field from form
    df = read_data()
    
    try:
        df = read_data()

        match = (
            (df['Roll No'].astype(str).str.strip() == str(name).strip()) |
            (df['Admission No'].astype(str).str.strip() == str(name).strip()) |
            (df['Full Name'].str.strip().str.lower() == name.strip().lower())
        )

        student_details = df[match]

        if not student_details.empty:
            student = student_details.iloc[0]              

            # get all fields from the form
            student_name = safe_get(student, "Full Name")
            student_roll_no = safe_get(student, "Roll No")
            student_admission_no = safe_get(student, "Admission No")
            student_gender = safe_get(student, "Gender")
            student_father_name = safe_get(student, "Father Name")
            student_mother_name = safe_get(student, "Mother Name")
            student_address = safe_get(student, "Address")
            student_email = safe_get(student, "Email")
            student_phone = safe_get(student, "Phone")
            student_aadhaar_no = safe_get(student, "Aadhaar No") # 🆕 added
            student_dob = safe_get(student, "Date of Birth")     # 🆕 added
            student_course_name = safe_get(student, "Course Name")  # 🆕 added
            student_admission_date = safe_get(student, "Date of Admission")  # 🆕 added

            student_sem1_fee = safe_get(student, "Sem 1 Fee")
            student_sem1_result = safe_get(student, "Sem 1 Result")
            student_sem2_fee = safe_get(student, "Sem 2 Fee")
            student_sem2_result = safe_get(student, "Sem 2 Result")
            student_sem3_fee = safe_get(student, "Sem 3 Fee")
            student_sem3_result = safe_get(student, "Sem 3 Result")
            student_sem4_fee = safe_get(student, "Sem 4 Fee")
            student_sem4_result = safe_get(student, "Sem 4 Result")

            # Pass everything to the template
            return render_template('pass.html', 
                                   n="Student Found", 
                                   na=student_name, 
                                   roll=student_roll_no,
                                   admission_no=student_admission_no,
                                   gender=student_gender, 
                                   father_name=student_father_name, 
                                   mother_name=student_mother_name, 
                                   address=student_address, 
                                   email=student_email,
                                   phone=student_phone,
                                   aadhaar_no=student_aadhaar_no,   
                                   dob=student_dob,               
                                   course_name=student_course_name,  
                                   admission_date=student_admission_date,
                                   sem1_fee=student_sem1_fee,
                                   sem1_result=student_sem1_result,
                                   sem2_fee=student_sem2_fee,
                                   sem2_result=student_sem2_result,
                                   sem3_fee=student_sem3_fee,
                                   sem3_result=student_sem3_result,
                                   sem4_fee=student_sem4_fee,
                                   sem4_result=student_sem4_result)
        
        else:
            return render_template('passno.html', z="Student not found")

    except Exception as e:
        return render_template('passno.html', n="Error Occurred", z=name)
    
#/////////////////////// getting value from form and posting values to the pass section Ends \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\



#////////////////////////////////////////////// fee Alert section strats \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    
MAX_RETRIES = 3
failed_numbers = {}
pending_numbers = []

# SMS sending function
def send_sms(number, message):
    try:
        api_key = os.getenv("FAST2SMS_API_KEY")
        url = "https://www.fast2sms.com/dev/bulkV2"
        payload = {
            "route": "q",
            "message": message,
            "language": "english",
            "flash": 0,
            "numbers": number
        }
        headers = {
            "authorization": api_key
        }
        response = requests.post(url, json=payload, headers=headers)
        result = response.json()
        print(f"SMS API Response: {result}")
        if result.get("return") == True:
            return True
        else:
            return False
    except Exception as e:
        print(f"SMS error: {e}")
        return False


@app.route('/send-fee-alert', methods=['POST'])
def send_fee_alert():
    pending_numbers = []
    semester = request.form.get('semester')
    fee_amount = request.form.get('fee')
    due_date = request.form.get('due_date')

    try:
        semester = int(semester.strip())
        fee_amount = float(fee_amount.strip())
    except ValueError:
        return "Invalid semester or fee amount.", 400

    if semester < 1 or semester > 4:
        return "Invalid semester. Please enter a semester between 1 and 4.", 400

    if not os.path.exists(FILE_PATH):
        return "Student data file not found.", 404

    df = read_data()

    fee_column = f"Sem {semester} Fee"

    if fee_column not in df.columns:
        return f"No data available for Semester {semester}.", 404

    for index, row in df.iterrows():
        paid_fee = row.get(fee_column)
        std_name = row.get("Full Name")
        phone = str(row.get("Phone"))

        if pd.isna(paid_fee) or str(paid_fee).strip() == "":
            paid_fee = 0.0

        if pd.notna(paid_fee) and pd.notna(phone):
            try:
                paid_fee = float(str(paid_fee).replace(',', '').strip())
                if paid_fee < fee_amount:
                    balance_due = fee_amount - paid_fee
                    pending_numbers.append((phone, paid_fee, balance_due, std_name))
            except ValueError:
                continue

    alert_count = 0
    while pending_numbers:
        next_pending = []
        for number, paid_fee, balance_due, std_name in pending_numbers:
            message = (
                f"Hello! Dear {std_name}, "
                f"This is a fee due alert from NOBEL INSTITUTE OF SCIENCE AND TECHNOLOGY. "
                f"You have paid Rs.{paid_fee} of SEMESTER-{semester} fee. "
                f"Your due balance is Rs.{balance_due}. "
                f"Please make the payment before {due_date}. "
                f"This is an automated message, please do not reply."
            )

            success = send_sms(number, message)
            if not success:
                failed_numbers[number] = failed_numbers.get(number, 0) + 1
                if failed_numbers[number] < MAX_RETRIES:
                    next_pending.append((number, paid_fee, balance_due, std_name))
            else:
                alert_count += 1
        pending_numbers = next_pending

    return f"Alert sent to {alert_count} students, {len(failed_numbers)} failed after retries."

#////////////////////////////////////////////// fee Alert section Ends \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\



if __name__=='__main__':
    webview.start()
    
