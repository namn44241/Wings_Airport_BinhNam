
    document.addEventListener('DOMContentLoaded', function() {
        setTimeout(function() {
        document.getElementById('preloader').classList.add('hidden');
        document.body.classList.add('loaded');
        }, 3000);
    });
    
    window.addEventListener('load', function() {
        setTimeout(function() {
        if (!document.body.classList.contains('loaded')) {
            document.getElementById('preloader').classList.add('hidden');
            document.body.classList.add('loaded');
        }
        }, 500);
    });
