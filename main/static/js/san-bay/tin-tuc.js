
        const notifications = [
            { type: 'Tin tức', date: '10/06/2024', text: 'Thông báo quầy làm thủ tục từ Philippines về Việt Nam', link: 'https://example.com/news1' },
            { type: 'Tin tức', date: '11/06/2024', text: 'Chuyến bay mới từ Hà Nội đi Đà Nẵng', link: 'https://example.com/news2' },
            { type: 'Tin tức', date: '12/06/2024', text: 'Giảm giá vé máy bay mùa hè', link: 'https://example.com/news3' },
            { type: 'Tin tức', date: '13/06/2024', text: 'Lịch bay mùa đông', link: 'https://example.com/news4' }
        ];
        let currentNotificationIndex = 0;
        let intervalId;
    
        function updateNotification() {
            const content = document.getElementById('notification-content');
            const count = document.getElementById('notification-count');
            const moreLink = document.getElementById('notification-more-link');
            const currentNotification = notifications[currentNotificationIndex];
    
            content.innerHTML = `
                <span class="notification-type">${currentNotification.type}</span>: 
                <span>${currentNotification.date}</span> - 
                <a href="${currentNotification.link}" style="text-decoration: none; color: inherit;">
                    ${currentNotification.text}
                </a>`;
            count.innerText = `${currentNotificationIndex + 1}/${notifications.length}`;
            moreLink.href = currentNotification.link;
        }
    
        function prevNotification() {
            currentNotificationIndex = (currentNotificationIndex - 1 + notifications.length) % notifications.length;
            updateNotification();
        }
    
        function nextNotification() {
            currentNotificationIndex = (currentNotificationIndex + 1) % notifications.length;
            updateNotification();
        }
    
        function startAutoSlide() {
            intervalId = setInterval(nextNotification, 5000);
        }
    
        function stopAutoSlide() {
            clearInterval(intervalId);
        }
    
        document.addEventListener('DOMContentLoaded', () => {
            updateNotification();
            startAutoSlide();
    
            const buttons = document.querySelectorAll('.notification-nav button');
            buttons.forEach(button => {
                button.addEventListener('click', stopAutoSlide);
            });
        });