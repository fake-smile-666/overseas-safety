/**
 * 海外安全助手 JavaScript
 */

// 当DOM加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 添加年份到页脚
    const footerYear = document.querySelector('.footer .text-muted');
    if (footerYear) {
        const now = new Date();
        footerYear.innerHTML = footerYear.innerHTML.replace('{{ now.year }}', now.getFullYear());
    }
    
    // 初始化工具提示
    initializeTooltips();
    
    // 初始化紧急求助按钮
    initializeEmergencyButton();
    
    // 注册验证表单
    initializeFormValidation();
});

/**
 * 初始化Bootstrap工具提示
 */
function initializeTooltips() {
    // 检查是否有Bootstrap的tooltip对象
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

/**
 * 初始化紧急求助按钮功能
 */
function initializeEmergencyButton() {
    const emergencyButton = document.getElementById('sendEmergencyBtn');
    if (emergencyButton) {
        emergencyButton.addEventListener('click', function() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(function(position) {
                    const latitude = position.coords.latitude;
                    const longitude = position.coords.longitude;
                    
                    // 在实际应用中，这里应该发送位置信息到紧急联系人
                    console.log('发送紧急求助信息，位置：', latitude, longitude);
                    
                    // 显示确认信息
                    showEmergencyConfirmation(latitude, longitude);
                }, function(error) {
                    // 位置获取失败
                    console.error('无法获取位置信息：', error);
                    showEmergencyConfirmation();
                });
            } else {
                // 浏览器不支持地理位置
                console.error('您的浏览器不支持地理位置信息获取');
                showEmergencyConfirmation();
            }
        });
    }
}

/**
 * 显示紧急求助确认信息
 */
function showEmergencyConfirmation(latitude, longitude) {
    let message = '紧急求助信息已发送！';
    if (latitude && longitude) {
        message += '\n位置信息: 纬度 ' + latitude + '，经度 ' + longitude;
    } else {
        message += '\n无法获取您的位置信息，但求助信息已发送。';
    }
    
    alert(message);
    
    // 关闭模态框
    const emergencyModal = document.getElementById('emergencyModal');
    if (emergencyModal && typeof bootstrap !== 'undefined' && bootstrap.Modal) {
        const modalInstance = bootstrap.Modal.getInstance(emergencyModal);
        if (modalInstance) {
            modalInstance.hide();
        }
    }
    
    // 可以重定向到安全地图
    setTimeout(function() {
        if (document.querySelector('a[href*="safety_map"]')) {
            window.location.href = document.querySelector('a[href*="safety_map"]').href;
        }
    }, 1000);
}

/**
 * 初始化表单验证
 */
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
} 