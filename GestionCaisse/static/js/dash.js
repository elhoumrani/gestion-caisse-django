document.addEventListener('DOMContentLoaded', function() {
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.getElementById('sidebar');
    const main = document.getElementById('main');

    // Toggle Sidebar pour le mobile/tablette
    menuToggle.addEventListener('click', () => {
        if (window.innerWidth > 1024) {
            sidebar.style.width = sidebar.style.width === '0px' ? '260px' : '0px';
            main.style.marginLeft = main.style.marginLeft === '0px' ? '260px' : '0px';
        } else {
            sidebar.classList.toggle('active_mobile');
        }
    });
});