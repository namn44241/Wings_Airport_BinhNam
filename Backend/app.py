from flask import Flask, render_template, request, redirect, url_for, render_template_string, jsonify, session, flash
import pyodbc
import os
from datetime import datetime
from flask_cors import CORS
from flask_mail import Mail, Message

app = Flask(__name__)
CORS(app) 
app.static_folder = 'static' 
app.secret_key = os.urandom(24)

# Thông tin kết nối
dsn = 'QuanLiSanBay'
cnxn = pyodbc.connect(f'DSN={dsn}')
cursor = cnxn.cursor()
                           
@app.route('/test_connection')
def test_connection():
    try:
        query = "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES"
        cursor.execute(query)
        tables = cursor.fetchall()
        return f"Kết nối thành công! Danh sách các bảng: {tables}"
    except Exception as e:
        return f"Kết nối thất bại: {str(e)}"
    
@app.route('/')
def check_login():
    if 'username' in session:
        return redirect(url_for('admin')) 
    else:
        return redirect(url_for('san_bay'))
    
@app.route('/login')
def login():     
    # Hiển thị form đăng nhập nếu chưa đăng nhập
    html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Đăng nhập</title>
            <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
        </head>
        <body onload="showLoginDialog()">
            <script>
                function showLoginDialog() {
                    Swal.fire({
                        title: 'Đăng nhập',
                        html: `
                            <input id="username" class="swal2-input" placeholder="Tài khoản">
                            <input id="password" type="password" class="swal2-input" placeholder="Mật khẩu">
                        `,
                        confirmButtonText: 'Đăng nhập',
                        preConfirm: () => {
                            const username = document.getElementById('username').value;
                            const password = document.getElementById('password').value;
                            if (!username || !password) {
                                Swal.showValidationMessage('Vui lòng nhập tài khoản và mật khẩu.');
                            }
                            return { username, password };
                        },
                        allowOutsideClick: false
                    }).then((result) => {
                        if (result.isConfirmed) {
                            const { username, password } = result.value;
                            window.location.href = `/auth?username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`;
                        }
                    });
                }
            </script>
        </body>
        </html>
    """
    return render_template_string(html)

    
@app.route('/auth')
def auth():
    username = request.args.get('username')
    password = request.args.get('password')
    
    query = "SELECT UserName FROM Admins WHERE UserName = ? AND PasswordHash = dbo.HashPassword(?)"
    cursor.execute(query, (username, password))
    result = cursor.fetchone()

    if result:
        user_name = result[0]
        session['username'] = user_name  
        return redirect(url_for('admin', username=user_name))
    else:
        error_msg = "Tài khoản hoặc mật khẩu không đúng"
        return render_template_string("<script>alert('{}'); window.location.href = '/';</script>".format(error_msg))


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('san_bay'))

@app.route('/san_bay')
def san_bay():
    return render_template('san_bay.html')

@app.route('/admin')
def admin():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session.get('username')

    # Hiển thị nút đăng xuất
    html = f"""
    <h2>Xin chào {username}</h2>
    <a href="{url_for('logout')}">Đăng xuất</a>
    <script>
        var confirmLogout = confirm("Bạn có muốn đăng xuất?");
        if (confirmLogout) {{
            window.location.href = "{url_for('logout')}";
        }}
    </script>
    """

    flight_info = []
    plane_info = []
    booking_info = []
    aircraft_info = []
    customer_info = []
    employee_info = []
    schedule_info = []
    assignment_info = []
    customer_list = []
    flight_list = []


    # Lấy danh sách chuyến bay từ cơ sở dữ liệu
    query = "SELECT MaChuyenBay, TenSanBayDi, TenSanBayDen, GioDi, GioDen FROM ChuyenBay"
    cursor.execute(query)
    flight_info = [row for row in cursor.fetchall()]

    query = "SELECT MAX(MaChuyenBay) FROM ChuyenBay"
    cursor.execute(query)
    max_flight_id = cursor.fetchone()[0]

    if max_flight_id:
        max_id_num = int(max_flight_id[2:])
        next_id_num = max_id_num + 1
        next_flight_id = f"CB{next_id_num:06d}"
    else:
        next_flight_id = "CB000001"

    # Lấy danh sách loại máy bay từ cơ sở dữ liệu
    query = "SELECT MaLoai, HangSanXuat FROM LoaiMayBay"
    cursor.execute(query)
    aircraft_info = [dict(MaLoai=row[0], HangSanXuat=row[1]) for row in cursor.fetchall()]

    query = "SELECT MAX (MaLoai) FROM LoaiMayBay"
    cursor.execute(query)
    max_plane_type_id = cursor.fetchone()[0]

    if max_plane_type_id:
         # Chuyển đổi max_plane_type_id thành chuỗi
        max_plane_type_id_str = str(max_plane_type_id)
        next_id_num = int(max_plane_type_id_str) + 1
        next_plane_type_id = f"{next_id_num:02d}"
    else:
        next_plane_type_id = "01"

    # Lấy danh sách thông tin đặt chỗ và thông tin chuyến bay
    query = """
    SELECT dc.MaKH, kh.HoDem, kh.Ten, kh.SDT, dc.NgayDi, cb.MaChuyenBay, 
        cb.GioDi, cb.GioDen, cb.TenSanBayDi, cb.TenSanBayDen
    FROM DatCho dc
    JOIN ChuyenBay cb ON dc.MaChuyenBay = cb.MaChuyenBay
    JOIN KhachHang kh ON dc.MaKH = kh.MaKH
    """
    cursor.execute(query)
    booking_info = cursor.fetchall()

    # Lấy thông tin đầy đủ về khách hàng từ cơ sở dữ liệu
    query = "SELECT MaKH, SDT, HoDem, Ten, DiaChi FROM KhachHang"
    cursor.execute(query)
    customer_info = [row for row in cursor.fetchall()]

    query = "SELECT MAX(MaKH) FROM KhachHang"
    cursor.execute(query)
    max_customer_id = cursor.fetchone()[0]

    if max_customer_id:
        # Lấy phần số từ ký tự thứ 3 của max_customer_id
        max_id_num = int(max_customer_id[2:])
        next_id_num = max_id_num + 1
        next_customer_id = f"KH{next_id_num:06d}"
    else:
        next_customer_id = "KH000001"

    # Lấy danh sách máy bay từ cơ sở dữ liệu
    query = "SELECT SoHieu, MayBay.MaLoai, SoGheNgoi FROM MayBay JOIN LoaiMayBay ON MayBay.MaLoai = LoaiMayBay.MaLoai"
    cursor.execute(query)
    plane_info = [dict(SoHieu=row[0], MaLoai=row[1], SoGheNgoi=row[2]) for row in cursor.fetchall()]

    # Lấy thông tin đầy đủ về nhân viên từ cơ sở dữ liệu
    query = "SELECT MaNV, HoDem, Ten, SDT, DiaChi, Luong, LoaiNV FROM NhanVien"
    cursor.execute(query)
    employee_info = [row for row in cursor.fetchall()]

    query = "SELECT MAX(MaNV) FROM NhanVien"
    cursor.execute(query)
    max_employee_id = cursor.fetchone()[0]

    if max_employee_id:
        max_id_num = int(max_employee_id[2:])
        next_id_num = max_id_num + 1
        next_employee_id = f"NV{next_id_num:06d}"
    else:
        next_employee_id = "NV000001"

    # Lấy thông tin lịch bay từ cơ sở dữ liệu
    query = "SELECT * FROM LichBay"
    cursor.execute(query)
    schedule_rows = cursor.fetchall()

    # Lấy thông tin phân công từ cơ sở dữ liệu
    query = "SELECT KhachHang.MaKH, DatCho.NgayDi, DatCho.MaChuyenBay FROM DatCho JOIN KhachHang ON DatCho.MaKH = KhachHang.MaKH"
    cursor.execute(query)
    assignment_info = [row for row in cursor.fetchall()]

    query = """
    SELECT p.MaNV, n.HoDem + ' ' + n.Ten AS HoTen, n.SDT, n.LoaiNV, p.MaChuyenBay, c.TenSanBayDi, c.TenSanBayDen, c.GioDi, c.GioDen, p.NgayDi
    FROM PhanCong p
    JOIN NhanVien n ON p.MaNV = n.MaNV
    JOIN ChuyenBay c ON p.MaChuyenBay = c.MaChuyenBay
    """
    cursor.execute(query)
    assignment_info = cursor.fetchall()

    # Chuyển đổi kết quả thành list of dicts để dễ sử dụng trong template
    columns = [column[0] for column in cursor.description]
    assignment_info = [dict(zip(columns, row)) for row in assignment_info]

    # Thống kê số lượng
    stats = {
        'khach_hang': cursor.execute("SELECT COUNT(*) FROM KhachHang").fetchone()[0],
        'nhan_vien': cursor.execute("SELECT COUNT(*) FROM NhanVien").fetchone()[0],
        'loai_may_bay': cursor.execute("SELECT COUNT(*) FROM LoaiMayBay").fetchone()[0],
        'may_bay': cursor.execute("SELECT COUNT(*) FROM MayBay").fetchone()[0],
        'chuyen_bay': cursor.execute("SELECT COUNT(*) FROM ChuyenBay").fetchone()[0],
        'lich_bay': cursor.execute("SELECT COUNT(*) FROM LichBay").fetchone()[0],
        'dat_cho': cursor.execute("SELECT COUNT(*) FROM DatCho").fetchone()[0],
        'phan_cong': cursor.execute("SELECT COUNT(*) FROM PhanCong").fetchone()[0]
    }

    # API loai_may_bay_stats
    cursor.execute("SELECT HangSanXuat, COUNT(*) FROM LoaiMayBay GROUP BY HangSanXuat")
    loai_may_bay_stats = cursor.fetchall()
    stats['loai_may_bay_stats'] = {
        'labels': [s[0] for s in loai_may_bay_stats],
        'data': [s[1] for s in loai_may_bay_stats]
    }

    # API top_chuyen_bay
    query = """
    SELECT TOP 5 ChuyenBay.MaChuyenBay, ChuyenBay.TenSanBayDi, ChuyenBay.TenSanBayDen, COUNT(DatCho.MaKH) as total_bookings
    FROM ChuyenBay 
    JOIN LichBay ON LichBay.MaChuyenBay = ChuyenBay.MaChuyenBay
    JOIN DatCho ON DatCho.MaChuyenBay = LichBay.MaChuyenBay AND DatCho.NgayDi = LichBay.NgayDi
    GROUP BY ChuyenBay.MaChuyenBay, ChuyenBay.TenSanBayDi, ChuyenBay.TenSanBayDen
    ORDER BY total_bookings DESC
    """
    cursor.execute(query)
    top_flights = cursor.fetchall()
    stats['top_chuyen_bay'] = {
        'labels': [f"{f[0]} ({f[1]} -> {f[2]})" for f in top_flights],
        'data': [f[3] for f in top_flights]
    }

    # API nhan_vien_theo_loai
    cursor.execute("SELECT LoaiNV, COUNT(*) FROM NhanVien GROUP BY LoaiNV")
    nhan_vien_stats = cursor.fetchall()
    stats['nhan_vien_theo_loai'] = {
        'labels': [s[0] for s in nhan_vien_stats],
        'data': [s[1] for s in nhan_vien_stats]
    }

    # Thêm code để lấy dữ liệu cho quản lý lịch bay
    flights_query = """
    SELECT CB.MaChuyenBay, CB.TenSanBayDi, CB.TenSanBayDen 
    FROM ChuyenBay CB
    """
    aircrafts_query = "SELECT SoHieu FROM MayBay"

    flights = cursor.execute(flights_query).fetchall()
    aircrafts = cursor.execute(aircrafts_query).fetchall()

    schedules_query = """
    SELECT LB.MaChuyenBay, LB.SoHieu, MB.MaLoai, LMB.HangSanXuat, MB.SoGheNgoi,
            CB.TenSanBayDi, CB.TenSanBayDen, CB.GioDi, CB.GioDen
    FROM LichBay LB
    JOIN MayBay MB ON LB.SoHieu = MB.SoHieu
    JOIN LoaiMayBay LMB ON MB.MaLoai = LMB.MaLoai
    JOIN ChuyenBay CB ON LB.MaChuyenBay = CB.MaChuyenBay
    """
    schedules = cursor.execute(schedules_query).fetchall()

    # Chuyển kết quả thành danh sách các từ điển
    flights = [{"MaChuyenBay": f[0], "TenSanBayDi": f[1], "TenSanBayDen": f[2]} for f in flights]

    return render_template('admin.html',
                           username=username,
                           flight_info=flight_info,
                           plane_info=plane_info,
                           booking_info=booking_info,
                           aircraft_info=aircraft_info,
                           customer_info=customer_info,
                           employee_info=employee_info,
                           schedule_info=schedule_rows,
                           assignment_info=assignment_info,
                           customer_list=customer_list,
                           flight_list=flight_list,
                           next_customer_id=next_customer_id,
                           next_employee_id=next_employee_id,
                           next_plane_type_id=next_plane_type_id,
                           next_flight_id=next_flight_id,
                           stats=stats,
                           flights=flights,
                           aircrafts=aircrafts,
                           schedules=schedules)

# Cấu hình Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'wingsairport73@gmail.com'
app.config['MAIL_PASSWORD'] = 'hhma ernj xofx geks'

mail = Mail(app)

@app.route('/send-email', methods=['POST'])
def send_email():
    data = request.json
    email = data.get('email')
    language = data.get('language')
    full_name = data.get('fullName')

    print(f"Received language: {language}")

    if language == 'tieng-viet':
        subject = 'Xác nhận đăng ký Wings Airport'
        html_body = f'''
        <html>
            <body>
                <h1>Xin chào {full_name},</h1>
                <h3>Đây là Wings Airport, chúc bạn một ngày tốt lành!</h3>
                <img width="480" height="269" src="https://media.giphy.com/media/S2IfEQqgWc0AH4r6Al/giphy.gif" alt="hello">
                <p>Wings Airport tự hào là Sân bay hàng không quốc tế 4 sao.<br>
                    Xin trân trọng cảm ơn sự đồng hành của Quý khách và bạn hàng!</p>
                <p>Trân trọng,<br>Đội ngũ Wings Airport</p>
            </body>
        </html>
        '''
    elif language == 'english':
        subject = 'Wings Airport Subscription Confirmation'
        html_body = f'''
        <html>
            <body>
                <h1>Hello {full_name},</h1>
                <h3>This is Wings Airport, have a great day!</h3>
                <img width="480" height="269" src="https://media.giphy.com/media/S2IfEQqgWc0AH4r6Al/giphy.gif" alt="hello">
                <p>Wings Airport is proud to be a 4-star non-international airport.<br>
                    We sincerely thank our valued customers and partners for their support!</p>
                <p>Best regards,<br>Wings Airport Team</p>
            </body>
        </html>
        '''
    else:
        print(f"Không nhận ra ngôn ngữ: {language}")
        # Xử lý mặc định, ví dụ sử dụng tiếng Anh
        subject = 'Wings Airport Subscription Confirmation'
        html_body = f'''
        <html>
            <body>
                <h1>Hello {full_name},</h1>
                <h3>This is Wings Airport, have a great day!</h3>
                <img width="480" height="269" src="https://media.giphy.com/media/S2IfEQqgWc0AH4r6Al/giphy.gif" alt="hello">
                <p>Wings Airport is proud to be a 4-star non-international airport.<br>
                    We sincerely thank our valued customers and partners for their support!</p>
                <p>Best regards,<br>Wings Airport Team</p>
            </body>
        </html>
        '''

    try:
        msg = Message(subject,
                      sender='wingsairport73@gmail.com',
                      recipients=[email])
        msg.html = html_body
        mail.send(msg)
        return jsonify({"success": True}), 200
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500
    
@app.route('/api/flights', methods=['GET'])
def get_flights():
    try:
        query = """
        SELECT cb.MaChuyenBay, lb.SoHieu AS SoHieuMayBay, lb.MaLoai AS MaLoaiMayBay,
            cb.TenSanBayDi, cb.TenSanBayDen, cb.GioDi, cb.GioDen, lb.NgayDi
        FROM ChuyenBay cb
        INNER JOIN LichBay lb ON cb.MaChuyenBay = lb.MaChuyenBay
        """
        cursor.execute(query)
        flight_info = cursor.fetchall()
        
        flights = []
        for row in flight_info:
            flights.append({
                "MaChuyenBay": row.MaChuyenBay.strip() if row.MaChuyenBay else None,
                "SoHieuMayBay": row.SoHieuMayBay.strip() if row.SoHieuMayBay else None,
                "MaLoaiMayBay": row.MaLoaiMayBay if row.MaLoaiMayBay else None,
                "TenSanBayDi": row.TenSanBayDi,
                "TenSanBayDen": row.TenSanBayDen,
                "GioDi": row.GioDi.strftime("%Y-%m-%d %H:%M:%S") if row.GioDi else None,
                "GioDen": row.GioDen.strftime("%Y-%m-%d %H:%M:%S") if row.GioDen else None,
                "NgayDi": row.NgayDi.strftime("%Y-%m-%d") if row.NgayDi else None
            })
        print(f"Flights data: {flights}")
        return jsonify(flights)
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": "An error occurred while fetching flight data"}), 500
    
@app.route('/api/search', methods=['GET'])
def search_flights():
    query = request.args.get('query')
    search_type = request.args.get('type') 

    try:
        if search_type == 'flight':
            sql_query = "SELECT * FROM ChuyenBay WHERE MaChuyenBay LIKE ?"
            cursor.execute(sql_query, ('%' + query + '%',))
        else:  # airport
            sql_query = "SELECT * FROM ChuyenBay WHERE TenSanBayDi LIKE ? OR TenSanBayDen LIKE ?"
            cursor.execute(sql_query, ('%' + query + '%', '%' + query + '%'))

        results = cursor.fetchall()
        
        flights = []
        for row in results:
            flights.append({
                "MaChuyenBay": row.MaChuyenBay.strip(),
                "TenSanBayDi": row.TenSanBayDi,
                "TenSanBayDen": row.TenSanBayDen,
                "GioDi": row.GioDi.strftime("%Y-%m-%d %H:%M:%S") if row.GioDi else None,
                "GioDen": row.GioDen.strftime("%Y-%m-%d %H:%M:%S") if row.GioDen else None
            })
        
        return jsonify(flights)
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": "An error occurred while searching flights"}), 500
    
@app.route('/api/book', methods=['POST'])
def book_flight():
    data = request.json
    customer_id = data.get('customerId')
    flight_id = data.get('flightId')
    departure_date = data.get('departureDate')

    try:
        # Thực hiện đặt chỗ trong cơ sở dữ liệu
        query = "INSERT INTO DatCho (MaKH, MaChuyenBay, NgayDi) VALUES (?, ?, ?)"
        cursor.execute(query, (customer_id, flight_id, departure_date))
        conn.commit()
        return jsonify({"success": True})
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/them_cb', methods=['POST'])
def them_cb():
    flight_id = request.form['flight-id']
    departure_airport = request.form['departure-airport']
    arrival_airport = request.form['arrival-airport']
    departure_time = datetime.strptime(request.form['departure-time'], "%Y-%m-%dT%H:%M")
    arrival_time = datetime.strptime(request.form['arrival-time'], "%Y-%m-%dT%H:%M")

    query = "INSERT INTO ChuyenBay (MaChuyenBay, TenSanBayDi, TenSanBayDen, GioDi, GioDen) VALUES (?, ?, ?, ?, ?)"
    values = (flight_id, departure_airport, arrival_airport, departure_time, arrival_time)
    cursor.execute(query, values)
    cnxn.commit()
    return redirect(url_for('admin'))

@app.route('/sua_cb', methods=['POST'])
def sua_cb():
    flight_id = request.form['flight-id']
    departure_airport = request.form['departure-airport']
    arrival_airport = request.form['arrival-airport']
    departure_time = datetime.strptime(request.form['departure-time'], "%Y-%m-%dT%H:%M")
    arrival_time = datetime.strptime(request.form['arrival-time'], "%Y-%m-%dT%H:%M")
    query = "UPDATE ChuyenBay SET TenSanBayDi = ?, TenSanBayDen = ?, GioDi = ?, GioDen = ? WHERE MaChuyenBay = ?"
    values = (departure_airport, arrival_airport, departure_time, arrival_time, flight_id)
    cursor.execute(query, values)
    cnxn.commit()
    return redirect(url_for('admin'))

@app.route('/xoa_cb/<flight_id>', methods=['POST'])
def xoa_cb(flight_id):
    query = "DELETE FROM ChuyenBay WHERE MaChuyenBay = ?"
    cursor.execute(query, (flight_id,))
    cnxn.commit()
    return redirect(url_for('admin'))

### Các hàm xử lý cho quản lý LOẠI MÁY BAY

@app.route('/them_loai_mb', methods=['POST'])
def them_loai_mb():
    plane_type_id = request.form['plane-type-id']
    manufacturer = request.form['manufacturer']
    query = "INSERT INTO LoaiMayBay (MaLoai, HangSanXuat) VALUES (?, ?)"
    values = (plane_type_id, manufacturer)
    cursor.execute(query, values)
    cnxn.commit()
    return redirect(url_for('admin', section='aircraft-types'))

@app.route('/sua_loai_mb', methods=['POST'])
def sua_loai_mb():
    plane_type_id = request.form['plane-type-id']
    manufacturer = request.form['manufacturer']
    query = "UPDATE LoaiMayBay SET HangSanXuat = ? WHERE MaLoai = ?"
    values = (manufacturer, plane_type_id)
    cursor.execute(query, values)
    cnxn.commit()
    return redirect(url_for('admin', section='aircraft-types'))

@app.route('/xoa_loai_mb/<plane_type_id>', methods=['POST'])
def xoa_loai_mb(plane_type_id):
    query = "DELETE FROM LoaiMayBay WHERE MaLoai = ?"
    cursor.execute(query, (plane_type_id,))
    cnxn.commit()
    return redirect(url_for('admin', section='aircraft-types'))


### Các hàm xử lý cho quản lý ĐẶT CHỖ

@app.route('/them_dat_cho', methods=['POST'])
def them_dat_cho():
    customer_id = request.form['customer-id']
    flight_id = request.form['flight-id']
    departure_datetime = request.form['departure-datetime']

    try:
        # Chuyển đổi chuỗi ngày tháng thành đối tượng datetime
        departure_date = datetime.strptime(departure_datetime, '%Y-%m-%dT%H:%M')
        # Định dạng lại thành chuỗi YYYY-MM-DD
        ngay_di = departure_date.strftime('%Y-%m-%d')

        # Kiểm tra đặt chỗ đã tồn tại
        check_query = "SELECT COUNT(*) FROM DatCho WHERE MaKH = ? AND MaChuyenBay = ? AND NgayDi = ?"
        cursor.execute(check_query, (customer_id, flight_id, ngay_di))
        if cursor.fetchone()[0] > 0:
            return jsonify({"error": "Đã tồn tại đặt chỗ cho khách hàng này trên chuyến bay này."}), 400

        # Thêm bản ghi mới
        insert_query = "INSERT INTO DatCho (MaKH, NgayDi, MaChuyenBay) VALUES (?, ?, ?)"
        cursor.execute(insert_query, (customer_id, ngay_di, flight_id))
        cnxn.commit()
        
        return jsonify({"success": "Thêm đặt chỗ thành công"}), 200

    except Exception as e:
        cnxn.rollback()
        return jsonify({"error": f"Lỗi khi thêm đặt chỗ: {str(e)}"}), 500

@app.route('/get_flight_details', methods=['GET'])
def get_flight_details():
    flight_id = request.args.get('flight_id')
    query = "SELECT GioDi, GioDen FROM ChuyenBay WHERE MaChuyenBay = ?"
    cursor.execute(query, (flight_id,))
    result = cursor.fetchone()
    if result:
        return jsonify({
            'departure_time': result.GioDi.isoformat(),
            'arrival_time': result.GioDen.isoformat()
        })
    return jsonify({'error': 'Không tìm thấy chuyến bay'}), 404

@app.route('/sua_dat_cho', methods=['POST'])
def sua_dat_cho():
    customer_id = request.form['customer-id']
    new_flight_id = request.form['flight-id']
    new_departure_datetime = request.form['departure-datetime']

    try:
        # Trích xuất NgayDi mới từ departure_datetime
        new_ngay_di = datetime.strptime(new_departure_datetime, '%Y-%m-%dT%H:%M').date()

        # Lấy thông tin đặt chỗ hiện tại
        get_current_booking_query = """
        SELECT NgayDi, MaChuyenBay FROM DatCho 
        WHERE MaKH = ?
        """
        cursor.execute(get_current_booking_query, (customer_id,))
        result = cursor.fetchone()

        if not result:
            return jsonify({"error": "Không tìm thấy đặt chỗ để cập nhật"}), 404

        current_ngay_di, current_flight_id = result.NgayDi, result.MaChuyenBay

        # Cập nhật đặt chỗ
        update_query = """
        UPDATE DatCho 
        SET NgayDi = ?, MaChuyenBay = ?
        WHERE MaKH = ? AND NgayDi = ? AND MaChuyenBay = ?
        """
        cursor.execute(update_query, (new_ngay_di, new_flight_id, customer_id, current_ngay_di, current_flight_id))
        
        if cursor.rowcount == 0:
            return jsonify({"error": "Không thể cập nhật đặt chỗ"}), 400

        cnxn.commit()
        return jsonify({"success": "Cập nhật đặt chỗ thành công"}), 200

    except Exception as e:
        cnxn.rollback()
        return jsonify({"error": f"Lỗi khi cập nhật đặt chỗ: {str(e)}"}), 500

@app.route('/xoa_dat_cho', methods=['POST'])
def xoa_dat_cho():
    customer_id = request.form['customer_id']
    flight_id = request.form['flight_id']
    departure_date = request.form['departure_date']

    try:
        # Thực hiện xóa thông tin đặt chỗ từ cơ sở dữ liệu
        query = "DELETE FROM DatCho WHERE MaKH = ? AND MaChuyenBay = ? AND NgayDi = ?"
        values = (customer_id, flight_id, departure_date)
        cursor.execute(query, values)
        cnxn.commit()

        flash("Xóa đặt chỗ thành công", "success")
    except Exception as e:
        cnxn.rollback()
        flash(f"Lỗi khi xóa đặt chỗ: {str(e)}", "error")

    return redirect(url_for('admin')) 

### Các hàm xử lý cho quản lý MÁY BAY

@app.route('/them_mb', methods=['POST'])
def them_mb():
    try:
        plane_id = request.form['plane-id']
        plane_type_id = request.form['plane-type-id']
        seat_quantity = request.form['seat-quantity']

        # Kiểm tra độ dài của plane_id
        if len(plane_id) > 10:
            return jsonify({'success': False, 'message': 'Số hiệu máy bay không được vượt quá 10 ký tự'}), 400

        # Kiểm tra xem máy bay đã tồn tại chưa
        check_query = "SELECT COUNT(*) FROM MayBay WHERE SoHieu = ?"
        cursor.execute(check_query, (plane_id,))
        if cursor.fetchone()[0] > 0:
            return jsonify({'success': False, 'message': 'Máy bay với số hiệu này đã tồn tại!'}), 400

        # Kiểm tra xem loại máy bay có tồn tại không
        check_type_query = "SELECT COUNT(*) FROM LoaiMayBay WHERE MaLoai = ?"
        cursor.execute(check_type_query, (plane_type_id,))
        if cursor.fetchone()[0] == 0:
            return jsonify({'success': False, 'message': 'Loại máy bay không tồn tại!'}), 400

        query = "INSERT INTO MayBay (SoHieu, MaLoai, SoGheNgoi) VALUES (?, ?, ?)"
        values = (plane_id, plane_type_id, seat_quantity)
        cursor.execute(query, values)
        cnxn.commit()
        return jsonify({'success': True, 'message': 'Thêm máy bay thành công'}), 201
    except Exception as e:
        cnxn.rollback()
        return jsonify({'success': False, 'message': f'Lỗi khi thêm máy bay: {str(e)}'}), 500

@app.route('/sua_mb', methods=['POST'])
def sua_mb():
    try:
        plane_id = request.form['plane-id']
        plane_type_id = request.form['plane-type-id']
        seat_quantity = request.form['seat-quantity']

        # Kiểm tra xem máy bay có tồn tại trong bảng MayBay không
        check_plane_query = "SELECT COUNT(*) FROM MayBay WHERE SoHieu = ?"
        cursor.execute(check_plane_query, (plane_id,))
        if cursor.fetchone()[0] == 0:
            return jsonify({'success': False, 'message': 'Máy bay không tồn tại!'})

        # Kiểm tra xem máy bay có trong LichBay không
        check_schedule_query = "SELECT COUNT(*) FROM LichBay WHERE SoHieu = ?"
        cursor.execute(check_schedule_query, (plane_id,))
        if cursor.fetchone()[0] > 0:
            return jsonify({'success': False, 'message': 'Không thể sửa thông tin máy bay này vì đã được sử dụng trong lịch bay!'})

        # Nếu không có trong LichBay, tiến hành cập nhật
        update_query = "UPDATE MayBay SET MaLoai = ?, SoGheNgoi = ? WHERE SoHieu = ?"
        cursor.execute(update_query, (plane_type_id, seat_quantity, plane_id))
        cnxn.commit()
        
        return jsonify({'success': True, 'message': 'Cập nhật thông tin máy bay thành công'})

    except Exception as e:
        cnxn.rollback()
        return jsonify({'success': False, 'message': f'Lỗi khi cập nhật máy bay: {str(e)}'})

@app.route('/xoa_mb/<plane_id>', methods=['POST'])
def xoa_mb(plane_id):
    try:
        # Kiểm tra xem máy bay có trong LichBay không
        check_query = "SELECT COUNT(*) FROM LichBay WHERE SoHieu = ?"
        cursor.execute(check_query, (plane_id,))
        count = cursor.fetchone()[0]

        if count > 0:
            return jsonify({'success': False, 'message': f'Không thể xóa máy bay {plane_id} vì đã được sử dụng trong lịch bay.'})
        else:
            # Nếu không có trong LichBay, tiến hành xóa
            delete_query = "DELETE FROM MayBay WHERE SoHieu = ?"
            cursor.execute(delete_query, (plane_id,))
            cnxn.commit()
            return jsonify({'success': True, 'message': f'Đã xóa máy bay {plane_id} thành công.'})
    except Exception as e:
        cnxn.rollback()
        return jsonify({'success': False, 'message': f'Lỗi khi xóa máy bay: {str(e)}'})

### Các hàm xử lý cho quản lý KHÁCH HÀNG

@app.route('/them_kh', methods=['POST'])
def them_kh():
    customer_id = request.form['customer-id']
    customer_phone = request.form['customer-phone']
    customer_last_name = request.form['customer-last-name']
    customer_first_name = request.form['customer-first-name']
    customer_address = request.form['customer-address']
    query = "INSERT INTO KhachHang (MaKH, SDT, HoDem, Ten, DiaChi) VALUES (?, ?, ?, ?, ?)"
    values = (customer_id, customer_phone, customer_last_name, customer_first_name, customer_address)
    cursor.execute(query, values)
    cnxn.commit()
    return redirect(url_for('admin'))

@app.route('/next_customer_id', methods=['GET'])
def get_next_customer_id():
    query = "SELECT MAX(MaKH) FROM KhachHang"
    cursor.execute(query)
    max_customer_id = cursor.fetchone()[0]
    
    if max_customer_id:
        max_id_num = int(max_customer_id[2:])
        next_id_num = max_id_num + 1
        next_customer_id = f"KH{next_id_num:06d}"
    else:
        next_customer_id = "KH000001"
    
    return jsonify({"next_customer_id": next_customer_id})

@app.route('/them_kh_fe', methods=['POST'])
def them_kh_fe():
    customer_id = request.form['customer-id']
    customer_phone = request.form['customer-phone']
    customer_last_name = request.form['customer-last-name']
    customer_first_name = request.form['customer-first-name']
    customer_address = request.form['customer-address']
    
    query = "INSERT INTO KhachHang (MaKH, SDT, HoDem, Ten, DiaChi) VALUES (?, ?, ?, ?, ?)"
    values = (customer_id, customer_phone, customer_last_name, customer_first_name, customer_address)
    
    try:
        cursor.execute(query, values)
        cnxn.commit()
        return jsonify({"success": True, "message": "Khách hàng đã được thêm thành công"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    
@app.route('/sua_kh', methods=['POST'])
def sua_kh():
    customer_id = request.form['customer-id']
    customer_phone = request.form['customer-phone']
    customer_last_name = request.form['customer-last-name']
    customer_first_name = request.form['customer-first-name']
    customer_address = request.form['customer-address']
    query = "UPDATE KhachHang SET SDT = ?, HoDem = ?, Ten = ?, DiaChi = ? WHERE MaKH = ?"
    values = (customer_phone, customer_last_name, customer_first_name, customer_address, customer_id)
    cursor.execute(query, values)
    cnxn.commit()
    return redirect(url_for('admin'))

@app.route('/xoa_kh/<customer_id>', methods=['POST'])
def xoa_kh(customer_id):
    try:
        # Kiểm tra xem khách hàng có trong bảng DatCho không
        check_query = "SELECT COUNT(*) FROM DatCho WHERE MaKH = ?"
        cursor.execute(check_query, (customer_id,))
        count = cursor.fetchone()[0]
        
        if count > 0:
            # Nếu có, không xóa và trả về thông báo lỗi
            return jsonify({"status": "error", "message": "Không thể xóa khách hàng này vì khách hàng này đã đặt chỗ!"})
        else:
            # Nếu không, tiến hành xóa
            delete_query = "DELETE FROM KhachHang WHERE MaKH = ?"
            cursor.execute(delete_query, (customer_id,))
            cnxn.commit()
            return jsonify({"status": "success", "message": "Đã xóa khách hàng thành công."})
    
    except Exception as e:
        cnxn.rollback()
        return jsonify({"status": "error", "message": f"Có lỗi xảy ra: {str(e)}"})

### Các hàm xử lý cho quản lý NHÂN VIÊN


@app.route('/them_nv', methods=['POST'])
def them_nv():
    employee_id = request.form['employee-id']
    employee_last_name = request.form['employee-last-name']
    employee_first_name = request.form['employee-first-name']
    employee_phone = request.form['employee-phone']
    employee_address = request.form['employee-address']
    employee_salary = request.form['employee-salary']
    employee_type = request.form['employee-type']

    query = "INSERT INTO NhanVien (MaNV, HoDem, Ten, SDT, DiaChi, Luong, LoaiNV) VALUES (?, ?, ?, ?, ?, ?, ?)"
    values = (employee_id, employee_last_name, employee_first_name, employee_phone, employee_address, employee_salary, employee_type)
    cursor.execute(query, values)
    cnxn.commit()
    return redirect(url_for('admin'))

@app.route('/sua_nv/<employee_id>', methods=['POST'])
def sua_nv(employee_id):
    employee_last_name = request.form['employee-last-name']
    employee_first_name = request.form['employee-first-name']
    employee_phone = request.form['employee-phone']
    employee_address = request.form['employee-address']
    employee_salary = request.form['employee-salary']
    employee_type = request.form['employee-type']

    query = "UPDATE NhanVien SET HoDem = ?, Ten = ?, SDT = ?, DiaChi = ?, Luong = ?, LoaiNV = ? WHERE MaNV = ?"
    values = (employee_last_name, employee_first_name, employee_phone, employee_address, employee_salary, employee_type, employee_id)
    cursor.execute(query, values)
    cnxn.commit()
    return redirect(url_for('admin'))

@app.route('/xoa_nv/<employee_id>', methods=['POST'])
def xoa_nv(employee_id):
    query = "DELETE FROM NhanVien WHERE MaNV = ?"
    cursor.execute(query, (employee_id,))
    cnxn.commit()
    return redirect(url_for('admin')) 


### Các hàm xử lý cho quản lý LỊCH BAY

@app.route('/them_lich', methods=['POST'])
def them_lich():
    flight_id = request.form['flight-id']
    aircraft_id = request.form['aircraft-id']

    try:
        # Truy vấn để lấy GioDi từ bảng ChuyenBay
        query_get_giodi = "SELECT GioDi FROM ChuyenBay WHERE MaChuyenBay = ?"
        cursor.execute(query_get_giodi, (flight_id,))
        result = cursor.fetchone()

        if result:
            gio_di = result[0]
            ngay_di = str(gio_di).split()[0]  # Lấy phần ngày từ datetime

            # Lấy MaLoai từ bảng MayBay
            query_get_maloai = "SELECT MaLoai FROM MayBay WHERE SoHieu = ?"
            cursor.execute(query_get_maloai, (aircraft_id,))
            ma_loai_result = cursor.fetchone()

            if ma_loai_result:
                ma_loai = ma_loai_result[0]

                # Kiểm tra xem NgayDi và MaChuyenBay đã tồn tại chưa
                check_query = "SELECT COUNT(*) FROM LichBay WHERE NgayDi = ? AND MaChuyenBay = ?"
                cursor.execute(check_query, (ngay_di, flight_id))
                if cursor.fetchone()[0] > 0:
                    return jsonify({"error": "NgayDi và MaChuyenBay đã bị trùng lặp"}), 400

                # Thêm lịch bay mới
                query_insert = "INSERT INTO LichBay (NgayDi, MaChuyenBay, SoHieu, MaLoai) VALUES (?, ?, ?, ?)"
                values = (ngay_di, flight_id, aircraft_id, ma_loai)
                cursor.execute(query_insert, values)
                cnxn.commit()
                
                return jsonify({"success": "Thêm lịch bay thành công"}), 200
            else:
                return jsonify({"error": "Không tìm thấy MaLoai cho máy bay này"}), 400

    except Exception as e:
        cnxn.rollback()
        return jsonify({"error": f"Lỗi khi thêm lịch bay: {str(e)}"}), 500

@app.route('/sua_lich', methods=['POST'])
def sua_lich():
    flight_id = request.form['flight-id']
    aircraft_id = request.form['aircraft-id']

    try:
        # Kiểm tra xem lịch bay có tồn tại không
        check_query = "SELECT COUNT(*) FROM LichBay WHERE MaChuyenBay = ?"
        cursor.execute(check_query, (flight_id,))
        if cursor.fetchone()[0] == 0:
            return jsonify({"error": "Lịch bay không tồn tại"}), 400

        # Cập nhật lịch bay
        update_query = "UPDATE LichBay SET SoHieu = ? WHERE MaChuyenBay = ?"
        cursor.execute(update_query, (aircraft_id, flight_id))
        cnxn.commit()
        
        return jsonify({"success": "Cập nhật lịch bay thành công"}), 200
    
    except Exception as e:
        cnxn.rollback()
        return jsonify({"error": f"Lỗi khi cập nhật lịch bay: {str(e)}"}), 500

@app.route('/xoa_lich', methods=['POST'])
def xoa_lich():
    flight_id = request.form['flight-id']
    aircraft_id = request.form['aircraft-id']
    
    try:
        # Kiểm tra xem MaChuyenBay có trong bảng DatCho không
        check_datcho_query = "SELECT COUNT(*) FROM DatCho WHERE MaChuyenBay = ?"
        cursor.execute(check_datcho_query, (flight_id,))
        datcho_count = cursor.fetchone()[0]
        
        # Kiểm tra xem MaChuyenBay có trong bảng PhanCong không
        check_phancong_query = "SELECT COUNT(*) FROM PhanCong WHERE MaChuyenBay = ?"
        cursor.execute(check_phancong_query, (flight_id,))
        phancong_count = cursor.fetchone()[0]
        
        if datcho_count > 0:
            return jsonify({"error": "Không thể xóa. Mã chuyến bay đã được sử dụng trong bảng DatCho hoặc PhanCong."}), 400
        
        if phancong_count > 0:
            return jsonify({"error": "Không thể xóa. Mã chuyến bay đã được sử dụng trong bảng PhanCong hoặc DatCho."}), 400
        
        # Nếu không có ràng buộc, tiến hành xóa
        delete_query = "DELETE FROM LichBay WHERE MaChuyenBay = ? AND SoHieu = ?"
        cursor.execute(delete_query, (flight_id, aircraft_id))
        cnxn.commit()
        
        return jsonify({"success": "Xóa lịch bay thành công"}), 200
    
    except Exception as e:
        cnxn.rollback()
        return jsonify({"error": f"Lỗi khi xóa lịch bay: {str(e)}"}), 500
    

### Các hàm xử lý cho quản lý PHÂN CÔNG 

@app.route('/them_phan_cong', methods=['POST'])
def them_phan_cong():
    employee_id = request.form['employee-id']
    flight_id = request.form['flight-id']
    departure_datetime = request.form['departure-datetime']

    try:
        # Chuyển đổi chuỗi ngày tháng thành đối tượng datetime
        departure_date = datetime.strptime(departure_datetime, '%Y-%m-%dT%H:%M')
        # Định dạng lại thành chuỗi YYYY-MM-DD
        ngay_di = departure_date.strftime('%Y-%m-%d')

        # Kiểm tra phân công đã tồn tại
        check_query = "SELECT COUNT(*) FROM PhanCong WHERE MaNV = ? AND MaChuyenBay = ? AND NgayDi = ?"
        cursor.execute(check_query, (employee_id, flight_id, ngay_di))
        if cursor.fetchone()[0] > 0:
            return jsonify({"error": "Đã tồn tại phân công cho nhân viên này trên chuyến bay này."}), 400

        # Thêm bản ghi mới
        insert_query = "INSERT INTO PhanCong (MaNV, NgayDi, MaChuyenBay) VALUES (?, ?, ?)"
        cursor.execute(insert_query, (employee_id, ngay_di, flight_id))
        cnxn.commit()
        
        return jsonify({"success": "Thêm phân công thành công"}), 200

    except Exception as e:
        cnxn.rollback()
        return jsonify({"error": f"Lỗi khi thêm phân công: {str(e)}"}), 500

@app.route('/sua_phan_cong', methods=['POST'])
def sua_phan_cong():
    employee_id = request.form['employee-id']
    new_flight_id = request.form['flight-id']
    new_departure_datetime = request.form['departure-datetime']

    try:
        # Trích xuất NgayDi mới từ departure_datetime
        new_ngay_di = datetime.strptime(new_departure_datetime, '%Y-%m-%dT%H:%M').date()

        # Lấy thông tin phân công hiện tại
        get_current_assignment_query = """
        SELECT NgayDi, MaChuyenBay FROM PhanCong 
        WHERE MaNV = ?
        """
        cursor.execute(get_current_assignment_query, (employee_id,))
        result = cursor.fetchone()

        if not result:
            return jsonify({"error": "Không tìm thấy phân công để cập nhật"}), 404

        current_ngay_di, current_flight_id = result.NgayDi, result.MaChuyenBay

        # Cập nhật phân công
        update_query = """
        UPDATE PhanCong 
        SET NgayDi = ?, MaChuyenBay = ?
        WHERE MaNV = ? AND NgayDi = ? AND MaChuyenBay = ?
        """
        cursor.execute(update_query, (new_ngay_di, new_flight_id, employee_id, current_ngay_di, current_flight_id))
        
        if cursor.rowcount == 0:
            return jsonify({"error": "Không thể cập nhật phân công"}), 400

        cnxn.commit()
        return jsonify({"success": "Cập nhật phân công thành công"}), 200

    except Exception as e:
        cnxn.rollback()
        return jsonify({"error": f"Lỗi khi cập nhật phân công: {str(e)}"}), 500

@app.route('/xoa_phan_cong', methods=['POST'])
def xoa_phan_cong():
    employee_id = request.form['employee_id']
    flight_id = request.form['flight_id']
    departure_date = request.form['departure_date']

    try:
        query = "DELETE FROM PhanCong WHERE MaNV = ? AND MaChuyenBay = ? AND NgayDi = ?"
        values = (employee_id, flight_id, departure_date)
        cursor.execute(query, values)
        cnxn.commit()

        return jsonify({"success": "Xóa phân công thành công"}), 200
    except Exception as e:
        cnxn.rollback()
        return jsonify({"error": f"Lỗi khi xóa phân công: {str(e)}"}), 500

@app.route('/get_flight_details_for_assignment', methods=['GET'])
def get_flight_details_for_assignment():
    flight_id = request.args.get('flight_id')
    query = "SELECT GioDi, GioDen, TenSanBayDi, TenSanBayDen FROM ChuyenBay WHERE MaChuyenBay = ?"
    cursor.execute(query, (flight_id,))
    result = cursor.fetchone()
    if result:
        return jsonify({
            'departure_time': result.GioDi.isoformat(),
            'arrival_time': result.GioDen.isoformat(),
            'departure_airport': result.TenSanBayDi,
            'arrival_airport': result.TenSanBayDen
        })
    return jsonify({'error': 'Không tìm thấy chuyến bay'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)