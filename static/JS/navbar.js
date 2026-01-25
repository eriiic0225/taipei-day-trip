document.addEventListener('DOMContentLoaded', async () => {
    const placeholder = document.getElementById('navbar-placeholder');
    if (placeholder) {
        try {
            const response = await fetch('/static/components/navbar.html');
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            const data = await response.text();
            placeholder.outerHTML = data;
            
            // 載入完成後，發送一個自定義事件，通知其他監聽者 Navbar 已就緒
            document.dispatchEvent(new Event('navbarLoaded'));

        } catch (error) {
            console.error('Error loading navbar:', error);
        }
    }
});