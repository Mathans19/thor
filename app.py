import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from pytz import timezone

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Set the timezone to Indian Standard Time (IST)
IST = timezone('Asia/Kolkata')

# Use IST for datetime operations
current_datetime_ist = datetime.now(IST)

class Attendance(db.Model):
    student_id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    date = db.Column(db.Date, primary_key=True)
    period1 = db.Column(db.Boolean, default=False)
    period2 = db.Column(db.Boolean, default=False)
    period3 = db.Column(db.Boolean, default=False)
    period4 = db.Column(db.Boolean, default=False)
    period5 = db.Column(db.Boolean, default=False)
    period6 = db.Column(db.Boolean, default=False)
    period7 = db.Column(db.Boolean, default=False)

@app.route('/mark-attendance', methods=['POST'])
def mark_attendance():
    data = request.json
    student_id = data['student_id']
    student_name = data['student_name']
    current_date = datetime.now(IST).date()  # Use IST for current date
    
    # Assuming current_time is sent as a string in 12-hour format (e.g., '03:30 PM') from Android
    current_time_str = data['current_time']
    
    # Convert the time string to a datetime object
    current_time = datetime.strptime(current_time_str, '%I:%M %p').time()
    
    periods = [
        {"start_time": datetime.strptime('08:40:00', '%H:%M:%S').time(), "end_time": datetime.strptime('09:35:00', '%H:%M:%S').time()},
        {"start_time": datetime.strptime('09:35:00', '%H:%M:%S').time(), "end_time": datetime.strptime('10:30:00', '%H:%M:%S').time()},
        {"start_time": datetime.strptime('10:30:00', '%H:%M:%S').time(), "end_time": datetime.strptime('11:25:00', '%H:%M:%S').time()},
        {"start_time": datetime.strptime('11:45:00', '%H:%M:%S').time(), "end_time": datetime.strptime('12:40:00', '%H:%M:%S').time()},
        {"start_time": datetime.strptime('13:40:00', '%H:%M:%S').time(), "end_time": datetime.strptime('14:30:00', '%H:%M:%S').time()},
        {"start_time": datetime.strptime('14:30:00', '%H:%M:%S').time(), "end_time": datetime.strptime('15:20:00', '%H:%M:%S').time()},
        {"start_time": datetime.strptime('15:20:00', '%H:%M:%S').time(), "end_time": datetime.strptime('16:00:00', '%H:%M:%S').time()}
    ]
    
    period_found = False
    for i, period in enumerate(periods, start=1):
        if current_time >= period["start_time"] and current_time <= period["end_time"]:
            period_found = True
            break
    
    if not period_found:
        return jsonify({'message': 'No period found for the current time'}), 400
    
    existing_record = Attendance.query.filter_by(student_id=student_id, date=current_date).first()
    if existing_record:
        # Student already marked attendance for the current date, update attendance for the appropriate period
        for i, period in enumerate(periods, start=1):
            if current_time >= period["start_time"] and current_time <= period["end_time"]:
                setattr(existing_record, f"period{i}", True)
                db.session.commit()
                response = jsonify({'message': f'Attendance marked successfully for period {i}'})
                response.headers['Date'] = datetime.now(IST).strftime('%a, %d %b %Y %H:%M:%S %Z')
                return response, 200
        return jsonify({'message': 'Student already marked attendance for the current date'}), 400
    else:
        # Student not marked attendance for the current date, insert new attendance record
        new_attendance = Attendance(student_id=student_id, name=student_name, date=current_date)
        for i, period in enumerate(periods, start=1):
            if current_time >= period["start_time"] and current_time <= period["end_time"]:
                setattr(new_attendance, f"period{i}", True)
                break
        db.session.add(new_attendance)
        db.session.commit()
        response = jsonify({'message': f'Attendance marked successfully for period {i}'})
        response.headers['Date'] = datetime.now(IST).strftime('%a, %d %b %Y %H:%M:%S %Z')
        return response, 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
