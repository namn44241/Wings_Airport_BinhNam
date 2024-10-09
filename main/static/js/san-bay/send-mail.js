
document.addEventListener('DOMContentLoaded', function() {
var emailInput = document.getElementById('email');
var additionalFields = document.getElementById('additional-fields');
var form = document.getElementById('newsletter-form');

// Xử lý hiển thị/ẩn các trường bổ sung
emailInput.addEventListener('focus', function() {
    additionalFields.style.display = 'block';
});

document.addEventListener('click', function(event) {
    if (!emailInput.contains(event.target) && !additionalFields.contains(event.target)) {
        additionalFields.style.display = 'none';
    }
});

form.addEventListener('submit', function(e) {
    e.preventDefault();
    sendEmail();
});
});

// Xử lý việc gửi form
function sendEmail() {
var email = document.getElementById('email').value;
var language = document.getElementById('language').value;
var lastName = document.getElementById('last_name').value;
var firstName = document.getElementById('first_name').value;
var fullName = lastName + ' ' + firstName;

console.log("Selected language:", language);

fetch('http://127.0.0.1:5000/send-email', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        email: email,
        language: language, 
        fullName: fullName
    }),
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        alert('Đăng ký thành công! Email xác nhận đã được gửi.');
        document.getElementById('newsletter-form').reset();
    } else {
        alert('Có lỗi xảy ra. Vui lòng thử lại sau.');
    }
})
.catch((error) => {
    console.error('Error:', error);
    alert('Có lỗi xảy ra. Vui lòng thử lại sau.');
});
}
