/* Paper2Agent Main JavaScript */

// Global state
let currentProject = null;
let statusCheckInterval = null;

// Create new project
function createProject() {
    const projectName = $('#projectName').val();
    const repoUrl = $('#repoUrl').val();
    const apiKey = $('#apiKey').val();
    
    if (!projectName || !repoUrl || !apiKey) {
        showToast('请填写所有必填字段', 'warning');
        return;
    }
    
    showToast('正在创建项目...', 'info');
    
    $.ajax({
        url: '/api/project/create',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            project_name: projectName,
            repo_url: repoUrl,
            api_key: apiKey
        }),
        success: function(response) {
            showToast('项目创建成功！', 'success');
            $('#newProjectModal').modal('hide');
            $('#newProjectForm')[0].reset();
            setTimeout(() => location.reload(), 1500);
        },
        error: function(xhr) {
            const error = xhr.responseJSON?.error || '创建项目失败';
            showToast(error, 'danger');
        }
    });
}

// Execute pipeline step
function executeStep(projectName, step, stepTitle) {
    if (confirm(`确定要执行 ${stepTitle} 吗？`)) {
        showToast(`开始执行 ${stepTitle}...`, 'info');
        
        $.ajax({
            url: `/api/project/${projectName}/execute/${step}`,
            method: 'POST',
            success: function(response) {
                if (response.success) {
                    showToast(`${stepTitle} 执行成功！`, 'success');
                    setTimeout(() => location.reload(), 1500);
                } else {
                    showToast(`${stepTitle} 执行失败`, 'danger');
                    if (response.error) {
                        console.error(response.error);
                    }
                }
            },
            error: function(xhr) {
                const error = xhr.responseJSON?.error || '执行失败';
                showToast(error, 'danger');
            }
        });
    }
}

// Show toast notification
function showToast(message, type = 'info') {
    const bgColors = {
        'success': 'bg-success',
        'danger': 'bg-danger',
        'warning': 'bg-warning',
        'info': 'bg-info'
    };
    
    const toast = $(`
        <div class="toast align-items-center text-white ${bgColors[type]} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                        data-bs-dismiss="toast"></button>
            </div>
        </div>
    `);
    
    // Create toast container if not exists
    if ($('#toastContainer').length === 0) {
        $('body').append('<div id="toastContainer" class="toast-container position-fixed top-0 end-0 p-3"></div>');
    }
    
    $('#toastContainer').append(toast);
    const bsToast = new bootstrap.Toast(toast[0]);
    bsToast.show();
    
    // Remove after hidden
    toast.on('hidden.bs.toast', function() {
        $(this).remove();
    });
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Copy to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showToast('已复制到剪贴板', 'success');
    }).catch(function() {
        showToast('复制失败', 'danger');
    });
}

// Download file
function downloadFile(projectName, filename) {
    window.location.href = `/api/project/${projectName}/output/${filename}`;
}

// Load visualization
function loadVisualization(imagePath) {
    const modal = $(`
        <div class="modal fade" tabindex="-1">
            <div class="modal-dialog modal-xl modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="bi bi-image"></i> 可视化结果
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body text-center">
                        <img src="${imagePath}" class="img-fluid" alt="Visualization">
                    </div>
                </div>
            </div>
        </div>
    `);
    
    $('body').append(modal);
    const bsModal = new bootstrap.Modal(modal[0]);
    bsModal.show();
    
    modal.on('hidden.bs.modal', function() {
        $(this).remove();
    });
}

// Start status check
function startStatusCheck() {
    if (statusCheckInterval) return;
    
    statusCheckInterval = setInterval(function() {
        $.get('/api/status', function(status) {
            updateStatusIndicator(status);
        });
    }, 3000);
}

// Stop status check
function stopStatusCheck() {
    if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
        statusCheckInterval = null;
    }
}

// Update status indicator
function updateStatusIndicator(status) {
    const indicator = $('#statusIndicator');
    
    if (status.running) {
        indicator.html(`
            <i class="bi bi-circle-fill text-warning"></i> 
            执行中: ${status.step || 'Unknown'}
        `);
    } else {
        indicator.html('<i class="bi bi-circle-fill text-success"></i> 就绪');
    }
}

// Initialize tooltips
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Initialize on page load
$(document).ready(function() {
    initTooltips();
    startStatusCheck();
});

// Cleanup on page unload
$(window).on('beforeunload', function() {
    stopStatusCheck();
});
