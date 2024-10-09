const API_BASE_URL = 'http://127.0.0.1:5000';

document.addEventListener('DOMContentLoaded', function() {
    const bookingContainer = document.getElementById('booking-container');
    const manageContainer = document.getElementById('manage-container');
    const checkinContainer = document.getElementById('checkin-container');

    // Thêm event listeners cho navbar
    document.getElementById('nav-booking').addEventListener('click', () => showContainer('booking'));
    document.getElementById('nav-manage').addEventListener('click', () => showContainer('manage'));
    document.getElementById('nav-checkin').addEventListener('click', () => showContainer('checkin'));

    function showContainer(containerName) {
        bookingContainer.style.display = 'none';
        manageContainer.style.display = 'none';
        checkinContainer.style.display = 'none';

        switch(containerName) {
            case 'booking':
                bookingContainer.style.display = 'block';
                initializeBooking();
                break;
            case 'manage':
                manageContainer.style.display = 'block';
                initializeManage();
                break;
            case 'checkin':
                checkinContainer.style.display = 'block';
                initializeCheckin();
                break;
        }
    }

    function initializeManage() {
        // Xóa các option cũ (nếu có)
        const flightSelect = document.getElementById('manage-flight-id');
        flightSelect.innerHTML = '<option value="">-- Chọn Mã chuyến bay --</option>';

        // Lấy danh sách chuyến bay chỉ khi người dùng focus vào select
        flightSelect.addEventListener('focus', function() {
            if (this.options.length <= 1) {  // Chỉ tải nếu chưa có dữ liệu
                fetch(`${API_BASE_URL}/api/flights`)
                    .then(response => response.json())
                    .then(data => {
                        data.forEach(flight => {
                            const option = document.createElement('option');
                            option.value = flight.MaChuyenBay;
                            option.textContent = `${flight.MaChuyenBay} - ${flight.TenSanBayDi} - ${flight.TenSanBayDen}`;
                            flightSelect.appendChild(option);
                        });
                    })
                    .catch(error => console.error('Error:', error));
            }
        });

        // Chỉ cập nhật thông tin chuyến bay khi đã chọn Mã chuyến bay
        flightSelect.addEventListener('change', function() {
            if (this.value) {
                updateFlightDetails(this.value);
            } else {
                document.getElementById('manage-departure-datetime').value = '';
                document.getElementById('manage-arrival-datetime').value = '';
            }
        });

        // Hàm cập nhật thông tin chuyến bay
        function updateFlightDetails(flightId) {
            if (flightId) {
                fetch(`${API_BASE_URL}/get_flight_details?flight_id=${flightId}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.error) {
                            alert(data.error);
                        } else {
                            document.getElementById('manage-departure-datetime').value = data.departure_time;
                            document.getElementById('manage-arrival-datetime').value = data.arrival_time;
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('Có lỗi khi lấy thông tin chuyến bay');
                    });
            } else {
                document.getElementById('manage-departure-datetime').value = '';
                document.getElementById('manage-arrival-datetime').value = '';
            }
        }

        // Xử lý sự kiện submit form đặt chỗ
        document.getElementById('bookingForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            
            // Lấy NgayDi từ GioDi
            const departureDatetime = new Date(formData.get('departure-datetime'));
            const ngayDi = departureDatetime.toISOString().split('T')[0]; // Lấy phần yyyy-mm-dd
            formData.append('ngay_di', ngayDi);

            fetch(`${API_BASE_URL}/them_dat_cho_fe`, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(data.message);
                    // Reset form
                    this.reset();
                    document.getElementById('manage-customer-id').value = '';
                } else {
                    alert(data.error || 'Có lỗi xảy ra khi đặt chỗ');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Có lỗi xảy ra khi gửi yêu cầu: ' + error.message);
            });
        });

        const lastRegisteredCustomerId = localStorage.getItem('lastRegisteredCustomerId');
        if (lastRegisteredCustomerId) {
            document.getElementById('manage-customer-id').value = lastRegisteredCustomerId;
            // Xóa giá trị từ localStorage sau khi đã sử dụng
            localStorage.removeItem('lastRegisteredCustomerId');
        }
    }

    function initializeBooking() {
        const form = document.getElementById('customer-form');

        fetchNextCustomerId();

        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            fetch(`${API_BASE_URL}/them_kh_fe`, {
                method: 'POST',
                body: new FormData(this)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(data.message);
                    const customerId = document.getElementById('customer-id').value;
                    // Lưu Mã khách hàng vào localStorage
                    localStorage.setItem('lastRegisteredCustomerId', customerId);
                    showContainer('manage');
                } else {
                    alert('Có lỗi xảy ra: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Có lỗi xảy ra khi gửi yêu cầu');
            });
        });
    }

    function fetchNextCustomerId() {
        fetch(`${API_BASE_URL}/next_customer_id`)
            .then(response => response.json())
            .then(data => {
                document.getElementById('customer-id').value = data.next_customer_id;
            })
            .catch(error => console.error('Error:', error));
    }

    function initializeCheckin() {
        const tableBody = document.querySelector('#flight-table tbody');
        
        tableBody.innerHTML = '<tr><td colspan="7">Đang tải dữ liệu...</td></tr>';

        fetch(`${API_BASE_URL}/api/flights`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                displayFlights(data);
            })
            .catch(error => {
                console.error('Error:', error);
                tableBody.innerHTML = '<tr><td colspan="7">Có lỗi xảy ra khi tải dữ liệu. Vui lòng thử lại sau.</td></tr>';
            });

        document.getElementById('search-flight-form').addEventListener('submit', function(e) {
            e.preventDefault();
            const query = this.querySelector('input[name="query"]').value;
            performSearch('flight', query);
        });

        document.getElementById('search-airport-form').addEventListener('submit', function(e) {
            e.preventDefault();
            const query = this.querySelector('input[name="query"]').value;
            performSearch('airport', query);
        });
    }

    function performSearch(type, query) {
        const tableBody = document.querySelector('#flight-table tbody');
        const rows = tableBody.querySelectorAll('tr');
        
        rows.forEach(row => {
            const cells = row.querySelectorAll('td');
            if (type === 'flight') {
                const flightCode = cells[0].textContent;
                row.style.display = flightCode.toLowerCase().includes(query.toLowerCase()) ? '' : 'none';
            } else if (type === 'airport') {
                const departureAirport = cells[3].textContent;
                const arrivalAirport = cells[4].textContent;
                row.style.display = 
                    departureAirport.toLowerCase().includes(query.toLowerCase()) ||
                    arrivalAirport.toLowerCase().includes(query.toLowerCase()) ? '' : 'none';
            }
        });
    }

    function displayFlights(flights) {
        const tableBody = document.querySelector('#flight-table tbody');
        tableBody.innerHTML = ''; // Xóa nội dung cũ
        
        if (flights.length === 0) {
            const row = document.createElement('tr');
            row.innerHTML = '<td colspan="7">Không có dữ liệu</td>';
            tableBody.appendChild(row);
        } else {
            flights.forEach(flight => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${flight.MaChuyenBay || 'N/A'}</td>
                    <td>${flight.SoHieuMayBay || 'N/A'}</td>
                    <td>${flight.MaLoaiMayBay || 'N/A'}</td>
                    <td>${flight.TenSanBayDi || 'N/A'}</td>
                    <td>${flight.TenSanBayDen || 'N/A'}</td>
                    <td>${flight.GioDi || 'N/A'}</td>
                    <td>${flight.GioDen || 'N/A'}</td>
                `;
                tableBody.appendChild(row);
            });
        }
    }
});
