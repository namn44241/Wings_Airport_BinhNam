
let slideIndex = 0;
let slides = document.querySelectorAll(".slide1");
let slideWrapper = document.querySelector(".slide1-wrapper");
let dotsContainer = document.querySelector(".dots");

function showSlides(n) {
    slideIndex = n;
    if (slideIndex > slides.length - 1) {
        slideIndex = 0;
    }
    if (slideIndex < 0) {
        slideIndex = slides.length - 1;
    }
    slideWrapper.style.transform = `translateX(-${slideIndex * 100}%)`;
    let dots = dotsContainer.querySelectorAll(".dot");
    dots.forEach((dot, index) => {
        dot.classList.toggle("active", index === slideIndex);
    });
}

function createDots() {
    for (let i = 0; i < slides.length; i++) {
        let dot = document.createElement("span");
        dot.classList.add("dot");
        dot.addEventListener("click", () => showSlides(i));
        dotsContainer.appendChild(dot);
    }
}

function nextSlide() {
    showSlides(slideIndex + 1);
}

createDots();
showSlides(0);
setInterval(nextSlide, 5000);