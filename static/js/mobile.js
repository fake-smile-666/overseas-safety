// 移动端交互增强
document.addEventListener('DOMContentLoaded', function() {
    // 防止iOS双击缩放
    document.addEventListener('touchend', function(event) {
        if (event.target.tagName === 'A' || event.target.tagName === 'BUTTON') {
            event.preventDefault();
            event.target.click();
        }
    }, false);

    // 处理iOS输入框焦点问题
    document.addEventListener('focusin', function(event) {
        if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
            setTimeout(function() {
                event.target.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }, 300);
        }
    });

    // 下拉刷新实现
    let touchStartY = 0;
    let touchEndY = 0;
    let pullToRefresh = document.querySelector('.pull-to-refresh');

    if (pullToRefresh) {
        document.addEventListener('touchstart', function(event) {
            touchStartY = event.touches[0].clientY;
        }, false);

        document.addEventListener('touchmove', function(event) {
            touchEndY = event.touches[0].clientY;
            const pullDistance = touchEndY - touchStartY;
            
            if (pullDistance > 0 && window.scrollY === 0) {
                event.preventDefault();
                pullToRefresh.style.transform = `translateY(${Math.min(pullDistance, 60)}px)`;
            }
        }, false);

        document.addEventListener('touchend', function() {
            const pullDistance = touchEndY - touchStartY;
            
            if (pullDistance > 50) {
                pullToRefresh.style.transform = 'translateY(60px)';
                // 触发刷新
                window.location.reload();
            } else {
                pullToRefresh.style.transform = 'translateY(0)';
            }
        }, false);
    }

    // 处理iOS键盘弹出时的视口问题
    const viewport = document.querySelector('meta[name=viewport]');
    if (viewport) {
        const originalContent = viewport.getAttribute('content');
        if (!originalContent.includes('height=')) {
            viewport.setAttribute('content', originalContent + ', height=' + window.innerHeight);
        }
    }

    // 处理iOS状态栏
    if (window.navigator.standalone) {
        document.body.classList.add('ios-standalone');
    }

    // 优化移动端点击反馈
    document.querySelectorAll('button, .btn, a').forEach(element => {
        if (element) {
            element.addEventListener('touchstart', function() {
                this.style.opacity = '0.7';
            });
            
            element.addEventListener('touchend', function() {
                this.style.opacity = '1';
            });
        }
    });

    // 处理移动端地图交互
    const mapContainer = document.querySelector('.map-container');
    if (mapContainer) {
        mapContainer.addEventListener('touchstart', function() {
            this.style.cursor = 'grabbing';
        });
        
        mapContainer.addEventListener('touchend', function() {
            this.style.cursor = 'grab';
        });
    }

    // 处理移动端表单提交
    document.querySelectorAll('form').forEach(form => {
        if (form) {
            form.addEventListener('submit', function(e) {
                // 获取所有输入字段
                const inputs = this.querySelectorAll('input, textarea');
                let hasError = false;
                
                // 验证所有必填字段
                inputs.forEach(input => {
                    if (input && input.required && !input.value.trim()) {
                        input.classList.add('is-invalid');
                        hasError = true;
                        e.preventDefault();
                    } else if (input) {
                        input.classList.remove('is-invalid');
                    }
                });
                
                if (!hasError) {
                    // 禁用提交按钮，防止重复提交
                    const submitButton = this.querySelector('button[type="submit"]');
                    if (submitButton) {
                        submitButton.disabled = true;
                        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> 提交中...';
                    }
                }
            });
        }
    });

    // 处理移动端图片加载
    document.querySelectorAll('img').forEach(img => {
        if (img) {
            img.addEventListener('load', function() {
                this.classList.add('loaded');
            });
        }
    });
}); 