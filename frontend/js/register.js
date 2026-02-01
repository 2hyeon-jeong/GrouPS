/**
 * BOJ Squad - 회원가입 페이지 JavaScript
 */

// API 기본 URL
const API_BASE_URL = window.location.origin;

// 핸들 검증 상태
let isHandleVerified = false;
let verifiedHandle = null;

/**
 * 백준 핸들 검증 버튼 클릭
 */
document.getElementById('verifyBtn').addEventListener('click', async () => {
    const handle = document.getElementById('handle').value.trim();
    
    if (!handle) {
        showVerifyResult('백준 아이디를 입력해주세요.', 'warning');
        return;
    }
    
    // 로딩 시작
    const verifyBtn = document.getElementById('verifyBtn');
    const originalText = verifyBtn.innerHTML;
    verifyBtn.disabled = true;
    verifyBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> 검증중...';
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/verify-handle/${handle}`);
        const data = await response.json();
        
        if (response.ok) {
            // 검증 성공
            isHandleVerified = true;
            verifiedHandle = handle;
            
            showVerifyResult(
                `✅ ${data.message}<br>` +
                `<small class="text-muted">티어: ${data.tier} | 푼 문제: ${data.solved_count}개</small>`,
                'success'
            );
        } else {
            // 검증 실패
            isHandleVerified = false;
            verifiedHandle = null;
            showVerifyResult(data.detail || '검증에 실패했습니다.', 'danger');
        }
    } catch (error) {
        console.error('Verify error:', error);
        isHandleVerified = false;
        verifiedHandle = null;
        showVerifyResult('서버와 연결할 수 없습니다.', 'danger');
    } finally {
        verifyBtn.disabled = false;
        verifyBtn.innerHTML = originalText;
    }
});

/**
 * 핸들 입력 변경 시 검증 상태 초기화
 */
document.getElementById('handle').addEventListener('input', () => {
    isHandleVerified = false;
    verifiedHandle = null;
    document.getElementById('handleVerifyResult').innerHTML = '';
});

/**
 * 회원가입 폼 제출
 */
document.getElementById('registerForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const handle = document.getElementById('handle').value.trim();
    const password = document.getElementById('password').value;
    const passwordConfirm = document.getElementById('passwordConfirm').value;
    
    // 유효성 검사
    if (!handle || !password || !passwordConfirm) {
        showAlert('모든 항목을 입력해주세요.', 'warning');
        return;
    }
    
    if (password !== passwordConfirm) {
        showAlert('비밀번호가 일치하지 않습니다.', 'warning');
        return;
    }
    
    if (password.length < 4) {
        showAlert('비밀번호는 최소 4자 이상이어야 합니다.', 'warning');
        return;
    }
    
    // 백준 핸들 검증 확인
    if (!isHandleVerified || verifiedHandle !== handle) {
        showAlert('백준 아이디 검증을 먼저 진행해주세요.', 'warning');
        return;
    }
    
    // 로딩 상태
    setRegisterButtonLoading(true);
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ handle, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // 회원가입 성공
            showAlert(
                `🎉 회원가입 성공!<br>${data.handle}님, 환영합니다!`,
                'success'
            );
            
            // 2초 후 로그인 페이지로 이동
            setTimeout(() => {
                window.location.href = '/static/login.html';
            }, 2000);
            
        } else {
            // 회원가입 실패
            showAlert(data.detail || '회원가입에 실패했습니다.', 'danger');
        }
        
    } catch (error) {
        console.error('Register error:', error);
        showAlert('서버와 연결할 수 없습니다.', 'danger');
    } finally {
        setRegisterButtonLoading(false);
    }
});

/**
 * 핸들 검증 결과 표시
 */
function showVerifyResult(message, type) {
    const resultDiv = document.getElementById('handleVerifyResult');
    const alertClass = `alert alert-${type} alert-dismissible fade show`;
    
    resultDiv.innerHTML = `
        <div class="${alertClass}" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
}

/**
 * 회원가입 버튼 로딩 상태 설정
 */
function setRegisterButtonLoading(isLoading) {
    const btn = document.getElementById('registerSubmitBtn');
    const btnText = document.getElementById('registerBtnText');
    const spinner = document.getElementById('registerSpinner');
    
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
