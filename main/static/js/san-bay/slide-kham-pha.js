    
    const slides1 = document.querySelectorAll('.slide');
    const slider = document.querySelector('.slider');
    const dotsContainer1 = document.querySelector('.dots1');
    let currentSlide = 0;
    const slidesPerPage = 3;

    // Tạo dấu chấm động
    const numDots = Math.ceil(slides1.length / slidesPerPage);
    for (let i = 0; i < numDots; i++) {
        const dot = document.createElement('span');
        dot.classList.add('dot');
        if (i === 0) {
            dot.classList.add('active');
        }
        dotsContainer1.appendChild(dot);
    }

    const dots1 = document.querySelectorAll('.dot');
    // // Hàm hiển thị slide dựa trên chỉ số n (số thứ tự của dấu chấm)
    function showSlide(n) {
        currentSlide = n;
        const slideWidth = slides1[0].offsetWidth + 20; 
        const maxTranslate = -(Math.floor((slides1.length - 1) / slidesPerPage) * slidesPerPage * slideWidth);
        let translateX = -n * slidesPerPage * slideWidth;
        translateX = Math.max(maxTranslate, Math.min(0, translateX));
        
        slider.style.transform = `translateX(${translateX}px)`;
        
        dots1.forEach((dot, index) => {
            dot.classList.toggle('active', index === n);
        });
    }

    // Hàm chuyển sang slide tiếp theo (khi hết slide sẽ quay lại slide đầu tiên)
    function nextSlide() {
        currentSlide = (currentSlide + 1) % numDots;
        showSlide(currentSlide);
    }

    showSlide(currentSlide);

    let slideInterval = setInterval(nextSlide, 5000);

    dots1.forEach((dot, index) => {
        dot.addEventListener('click', () => {
            clearInterval(slideInterval);
            showSlide(index);
            slideInterval = setInterval(nextSlide, 5000); 
        });
    });
