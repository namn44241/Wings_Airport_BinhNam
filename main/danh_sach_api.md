Dưới đây là danh sách các API đã được định nghĩa, tổng cộng có **44 API**:

### 1. Kiểm tra kết nối và đăng nhập
- **`/test_connection`**: `GET` - Kiểm tra kết nối.
- **`/`**: `GET` - Kiểm tra đăng nhập.
- **`/login`**: `GET` - Đăng nhập.
- **`/auth`**: `GET` - Xác thực người dùng.
- **`/logout`**: `GET` - Đăng xuất.

### 2. Quản lý sân bay và admin
- **`/san_bay`**: `GET` - Lấy danh sách sân bay.
- **`/admin`**: `GET` - Truy cập trang admin.

### 3. Gửi email
- **`/send-email`**: `POST` - Gửi email.

### 4. Quản lý chuyến bay
- **`/api/flights`**: `GET` - Lấy danh sách chuyến bay.
- **`/api/search`**: `GET` - Tìm kiếm chuyến bay.
- **`/api/book`**: `POST` - Đặt vé chuyến bay.
- **`/get_flight_details`**: `GET` - Lấy chi tiết chuyến bay.

### 5. Quản lý chuyến bay (admin)
- **`/them_cb`**: `POST` - Thêm chuyến bay (yêu cầu đăng nhập).
- **`/sua_cb`**: `POST` - Sửa thông tin chuyến bay (yêu cầu đăng nhập).
- **`/xoa_cb/<flight_id>`**: `POST` - Xóa chuyến bay (yêu cầu đăng nhập).

### 6. Quản lý loại máy bay
- **`/them_loai_mb`**: `POST` - Thêm loại máy bay (yêu cầu đăng nhập).
- **`/sua_loai_mb/<plane_type_id>`**: `POST` - Sửa loại máy bay (yêu cầu đăng nhập).
- **`/xoa_loai_mb/<plane_type_id>`**: `POST` - Xóa loại máy bay (yêu cầu đăng nhập).

### 7. Quản lý đặt chỗ
- **`/them_dat_cho`**: `POST` - Thêm đặt chỗ (yêu cầu đăng nhập).
- **`/them_dat_cho_fe`**: `POST` - Thêm đặt chỗ từ frontend.
- **`/sua_dat_cho`**: `POST` - Sửa đặt chỗ (yêu cầu đăng nhập).
- **`/xoa_dat_cho`**: `POST` - Xóa đặt chỗ (yêu cầu đăng nhập).

### 8. Quản lý máy bay
- **`/them_mb`**: `POST` - Thêm máy bay (yêu cầu đăng nhập).
- **`/sua_mb`**: `POST` - Sửa máy bay (yêu cầu đăng nhập).
- **`/xoa_mb/<plane_id>`**: `POST` - Xóa máy bay (yêu cầu đăng nhập).

### 9. Quản lý khách hàng
- **`/them_kh`**: `POST` - Thêm khách hàng (yêu cầu đăng nhập).
- **`/next_customer_id`**: `GET` - Lấy ID khách hàng tiếp theo.
- **`/them_kh_fe`**: `POST` - Thêm khách hàng từ frontend.
- **`/sua_kh`**: `POST` - Sửa khách hàng (yêu cầu đăng nhập).
- **`/xoa_kh/<customer_id>`**: `POST` - Xóa khách hàng (yêu cầu đăng nhập).

### 10. Quản lý nhân viên
- **`/them_nv`**: `POST` - Thêm nhân viên (yêu cầu đăng nhập).
- **`/sua_nv/<employee_id>`**: `POST` - Sửa nhân viên (yêu cầu đăng nhập).
- **`/xoa_nv/<employee_id>`**: `POST` - Xóa nhân viên (yêu cầu đăng nhập).

### 11. Quản lý lịch bay
- **`/them_lich`**: `POST` - Thêm lịch bay (yêu cầu đăng nhập).
- **`/sua_lich`**: `POST` - Sửa lịch bay (yêu cầu đăng nhập).
- **`/xoa_lich`**: `POST` - Xóa lịch bay (yêu cầu đăng nhập).

### 12. Quản lý phân công
- **`/them_phan_cong`**: `POST` - Thêm phân công (yêu cầu đăng nhập).
- **`/sua_phan_cong`**: `POST` - Sửa phân công (yêu cầu đăng nhập).
- **`/xoa_phan_cong`**: `POST` - Xóa phân công (yêu cầu đăng nhập).
- **`/get_flight_details_for_assignment`**: `GET` - Lấy chi tiết chuyến bay cho phân công.