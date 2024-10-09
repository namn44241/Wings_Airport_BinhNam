
        function showContainer(containerId) {
            var containers = document.querySelectorAll('.container');
            var clickedContainer = document.getElementById(containerId + '-container');
            var overlay = document.getElementById('overlay1');
        
            // Ẩn tất cả các container ngay lập tức
            containers.forEach(function(container) {
                container.style.opacity = '0';
                container.style.display = 'none';
            });
        
            // Hiển thị overlay và container được chọn
            overlay.style.display = 'block';
            clickedContainer.style.display = 'block';
            
            // Đặt opacity thành 1 sau một khoảng thời gian ngắn để kích hoạt transition
            setTimeout(function() {
                clickedContainer.style.opacity = '1';
            }, 10);
        }
        
        // Đóng popup khi click bên ngoài
        document.getElementById('overlay1').addEventListener('click', function() {
            var containers = document.querySelectorAll('.container');
            containers.forEach(function(container) {
                // Ẩn ngay lập tức, không có hiệu ứng fade out
                container.style.display = 'none';
                container.style.opacity = '0';
            });
            this.style.display = 'none';
        });
