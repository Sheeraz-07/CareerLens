// AI Resume Analyzer - Global Scripts

document.addEventListener('DOMContentLoaded', () => {
    console.log("AI Resume Analyzer loaded");

    // Attach loading overlay to forms that have the .needs-loader class
    const loaderForms = document.querySelectorAll('.needs-loader');
    const globalLoader = document.getElementById('global-loader');

    loaderForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (this.checkValidity()) {
                if (globalLoader) {
                    globalLoader.classList.remove('d-none');
                }
            }
        });
    });

    // Handle PDF Export Buttons
    const exportBtns = document.querySelectorAll('.export-pdf-btn');
    exportBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            const targetElement = document.getElementById(targetId);
            const fileName = this.getAttribute('data-filename') || 'export.pdf';
            
            if (targetElement && window.html2pdf) {
                const opt = {
                    margin:       0.5,
                    filename:     fileName,
                    image:        { type: 'jpeg', quality: 0.98 },
                    html2canvas:  { scale: 2 },
                    jsPDF:        { unit: 'in', format: 'letter', orientation: 'portrait' }
                };
                
                // Hide any buttons inside the target before exporting
                const originalDisplay = [];
                const innerBtns = targetElement.querySelectorAll('.btn, button');
                innerBtns.forEach(b => {
                    originalDisplay.push(b.style.display);
                    b.style.display = 'none';
                });
                
                html2pdf().set(opt).from(targetElement).save().then(() => {
                    // Restore buttons
                    innerBtns.forEach((b, idx) => {
                        b.style.display = originalDisplay[idx];
                    });
                });
            }
        });
    });
});
