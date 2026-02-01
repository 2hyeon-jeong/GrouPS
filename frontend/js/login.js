/**
 * BOJ Squad - 로그인 페이지 JavaScript
 */

// API 기본 URL
const API_BASE_URL = window.location.origin;

// 로컬 스토리지 키
const TOKEN_KEY = 'access_token';

/**
 * 로그인 폼 제출
 */
document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const handle = document.getElementById('handle').value.trim();
    const password = document.getElementById('password').value;
    
    // 유효성 검사
    if (!handle || !password) {
        showAlert('아이디와 비밀번호를 입력해주세요.', 'warning');
        return;
    }
    
    // 로딩 상태 표시
    setLoginButtonLoading(true);
    
    try {
        // 로그인 API 호출
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ handle, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // 1. 토큰 저장
            localStorage.setItem(TOKEN_KEY, data.access_token);
            
            // 2. 로그인 성공 알림 (선택 사항)
            alert('로그인 성공!');
            
            // 3. 즉시 메인 페이지로 이동
            window.location.href = '/';
            
        } else {
            // 로그인 실패 - 에러 메시지 표시
            showAlert(data.detail || '아이디 또는 비밀번호가 올바르지 않습니다.', 'danger');
        }
        
    } catch (error) {
        console.error('Login error:', error);
        showAlert('서버와 연결할 수 없습니다. 잠시 후 다시 시도해주세요.', 'danger');
    } finally {
        setLoginButtonLoading(false);
    }
});

/**
 * 로그인 버튼 로딩 상태 설정
 */
function setLoginButtonLoading(isLoading) {
    const btn = document.getElementById('loginBtn');
    const btnText = document.getElementById('loginBtnText');
    const spinner = document.getElementById('loginSpinner');
    
    if (isLoading) {
        btn.disabled = true;
        btnText.classList.add('d-none');
        spinner.classList.remove('d-none');
    } else {
        btn.disabled = false;
        btnText.classList.remove('d-none');
        spinner.classList.add('d-none');
    }
}

/**
 * 알림 메시지 표시
 */
function showAlert(message, type = 'info') {
    // 기존 알림 제거
    const existingAlert = document.querySelector('.custom-alert');
    if (existingAlert) {
        existingAlert.remove();
    }
    
    // 새 알림 생성
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show custom-alert`;
    alertDiv.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // 5초 후 자동 제거
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

/**
 * 페이지 로드 시 실행
 */
document.addEventListener('DOMContentLoaded', () => {
    // 이미 로그인된 경우 메인 페이지로 리다이렉트
    const token = localStorage.getItem(TOKEN_KEY);
    
    if (token) {
        console.log('Already logged in, redirecting to main page...');
        window.location.href = '/';
    }
});
