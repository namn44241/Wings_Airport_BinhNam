let currentLanguage = 'tieng-viet';
let translations = {};

async function loadTranslations(lang) {
    try {
        const response = await fetch(`/static/lang/${lang}.json`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        translations = await response.json();
    } catch (error) {
        console.error("Không thể tải file ngôn ngữ:", error);
        // Fallback to default language if there's an error
        if (lang !== 'tieng-viet') {
            console.log("Sử dụng ngôn ngữ mặc định (Tiếng Việt)");
            await loadTranslations('tieng-viet');
        }
    }
}

function updatePageLanguage() {
    if (Object.keys(translations).length === 0) {
        console.error("Không có dữ liệu dịch được tải");
        return;
    }

    // Cập nhật menu chính
    document.getElementById('helpLink').textContent = translations.helpLink;
    document.querySelector('a[href="http://127.0.0.1:5000/admin"]').textContent = translations.loginLink;
    document.querySelector('a[onclick="showContainer(\'booking\')"]').textContent = translations.registerLink;
    document.getElementById('languageSelector').textContent = translations.languageSelector;

    // Cập nhật modal ngôn ngữ
    document.querySelector('.modal-content h2').textContent = translations.modalTitle;
    document.querySelector('label[for="country"]').textContent = translations.countryLabel;
    document.querySelector('label[for="language"]').textContent = translations.languageLabel;
    document.getElementById('applyChoice').textContent = translations.applyButton;
    
    // Cập nhật các nút điều hướng
    const navItems = document.querySelectorAll('.navbar > div');
    navItems[0].textContent = translations.navBooking;
    navItems[1].textContent = translations.navManage;
    navItems[2].textContent = translations.navCheckIn;

    // Cập nhật các phần khác (ví dụ: tiêu đề phần, nút, v.v.)
    document.querySelector('.section-title').textContent = translations.popularFlights;
    document.querySelector('.dropdown-note').textContent = translations.priceNote;
    
    // ... Thêm các phần khác của trang web cần được dịch
}

document.getElementById('applyChoice').addEventListener('click', async function() {
    const selectedLanguage = document.getElementById('language').value;
    if (selectedLanguage !== currentLanguage) {
        currentLanguage = selectedLanguage;
        await loadTranslations(currentLanguage);
        updatePageLanguage();
    }
});

// Khởi tạo trang với ngôn ngữ mặc định
document.addEventListener('DOMContentLoaded', function() {
    loadTranslations(currentLanguage).then(updatePageLanguage);
});