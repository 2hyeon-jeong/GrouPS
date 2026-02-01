/**
 * BOJ Squad - Main App JS
 * Guild Dashboard Logic
 */

const API_BASE_URL = 'http://localhost:8000';
let createGroupModalInstance;
let loginModalInstance;

// 페이지 로드 시 실행
document.addEventListener('DOMContentLoaded', function() {
    // Bootstrap 모달 초기화
    const createGroupModalEl = document.getElementById('createGroupModal');
    const loginModalEl = document.getElementById('loginModal');
    
    if (createGroupModalEl) {
        createGroupModalInstance = new bootstrap.Modal(createGroupModalEl);
    }
    if (loginModalEl) {
        loginModalInstance = new bootstrap.Modal(loginModalEl);
    }
    
    // 로그인 상태 확인
    checkLoginStatus();
    
    // 이벤트 리스너 등록
    const createGroupForm = document.getElementById('createGroupForm');
    if (createGroupForm) {
        createGroupForm.addEventListener('submit', handleCreateGroup);
    }
    
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
});

/**
 * 로그인 상태 확인
 */
function checkLoginStatus() {
    const token = localStorage.getItem('access_token');
    
    if (token) {
        // 로그인 상태
        showDashboard();
        fetchUserInfo();
        fetchMyGroups();
        fetchRanking();
    } else {
        // 비로그인 상태
        showHeroSection();
    }
}

/**
 * 대시보드 표시
 */
function showDashboard() {
    document.getElementById('heroSection').classList.add('d-none');
    document.getElementById('dashboardSection').classList.remove('d-none');
    document.getElementById('guestNav').classList.add('d-none');
    document.getElementById('userNav').classList.remove('d-none');
}

/**
 * Hero Section 표시
 */
function showHeroSection() {
    document.getElementById('heroSection').classList.remove('d-none');
    document.getElementById('dashboardSection').classList.add('d-none');
    document.getElementById('guestNav').classList.remove('d-none');
    document.getElementById('userNav').classList.add('d-none');
}

/**
 * 사용자 정보 조회
 */
async function fetchUserInfo() {
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${API_BASE_URL}/users/me`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const user = await response.json();
            document.getElementById('userHandle').textContent = user.handle;
        } else {
            // 토큰이 유효하지 않으면 로그아웃
            logout();
        }
    } catch (error) {
        console.error('사용자 정보 조회 실패:', error);
    }
}

/**
 * 내 그룹 목록 조회
 */
async function fetchMyGroups() {
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${API_BASE_URL}/groups/my`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const groups = await response.json();
            renderMyGroups(groups);
        }
    } catch (error) {
        console.error('그룹 목록 조회 실패:', error);
    }
}

/**
 * 그룹 카드 렌더링
 */
function renderMyGroups(groups) {
    const container = document.getElementById('myGroupsContainer');
    const noGroupsMessage = document.getElementById('noGroupsMessage');
    
    // [+ 그룹 만들기] 카드는 유지하고, 기존 그룹 카드들만 제거
    const existingCards = container.querySelectorAll('.col-md-4:not(:first-child)');
    existingCards.forEach(card => card.remove());
    
    if (groups.length === 0) {
        noGroupsMessage.classList.remove('d-none');
        return;
    }
    
    noGroupsMessage.classList.add('d-none');
    
    groups.forEach(group => {
        const col = document.createElement('div');
        col.className = 'col-md-4';
        
        col.innerHTML = `
            <div class="card guild-card h-100">
                <div class="card-body">
                    <div class="d-flex align-items-start mb-3">
                        <div class="guild-icon me-3">
                            ${group.icon}
                        </div>
                        <div class="flex-grow-1">
                            <h5 class="card-title mb-1">${escapeHtml(group.name)}</h5>
                            <p class="text-muted small mb-0">${escapeHtml(group.description || '설명 없음')}</p>
                        </div>
                    </div>
                    
                    <div class="guild-stats">
                        <div class="guild-stat">
                            <i class="bi bi-people-fill"></i>
                            <span>${group.member_count} / ${group.max_members}</span>
                        </div>
                    </div>
                    
                    <button class="btn btn-primary w-100 mt-3" onclick="enterGroup(${group.id})">
                        <i class="bi bi-box-arrow-in-right"></i> 입장하기
                    </button>
                </div>
            </div>
        `;
        
        container.appendChild(col);
    });
}

/**
 * 랭킹 조회
 */
async function fetchRanking() {
    try {
        const response = await fetch(`${API_BASE_URL}/groups/ranking?limit=5`);
        
        if (response.ok) {
            const rankings = await response.json();
            renderRanking(rankings);
        }
    } catch (error) {
        console.error('랭킹 조회 실패:', error);
    }
}

/**
 * 랭킹 테이블 렌더링
 */
function renderRanking(rankings) {
    const tbody = document.getElementById('rankingTableBody');
    tbody.innerHTML = '';
    
    if (rankings.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="4" class="text-center text-muted py-4">
                    <i class="bi bi-inbox"></i> 랭킹 데이터가 없습니다
                </td>
            </tr>
        `;
        return;
    }
    
    rankings.forEach(item => {
        const tr = document.createElement('tr');
        
        const rankClass = item.rank <= 3 ? `rank-${item.rank}` : 'rank-other';
        
        tr.innerHTML = `
            <td>
                <span class="rank-badge ${rankClass}">${item.rank}</span>
            </td>
            <td>
                <span class="ranking-icon">${item.icon}</span>
            </td>
            <td>
                <strong>${escapeHtml(item.group_name)}</strong>
            </td>
            <td>
                <span class="badge bg-primary">${item.total_solved} 문제</span>
            </td>
        `;
        
        tbody.appendChild(tr);
    });
}

/**
 * 그룹 만들기 모달 표시
 */
function showCreateGroupModal() {
    const token = localStorage.getItem('access_token');
    if (!token) {
        alert('로그인이 필요합니다.');
        showLoginModal();
        return;
    }
    createGroupModalInstance.show();
}

/**
 * 그룹 생성 처리
 */
async function handleCreateGroup(e) {
    e.preventDefault();
    
    const token = localStorage.getItem('access_token');
    if (!token) {
        alert('로그인이 필요합니다.');
        return;
    }
    
    const formData = {
        name: document.getElementById('groupName').value,
        description: document.getElementById('groupDescription').value,
        icon: document.getElementById('groupIcon').value || '🎯',
        max_members: parseInt(document.getElementById('groupMaxMembers').value),
        password: document.getElementById('groupPassword').value || null
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/groups`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            const newGroup = await response.json();
            alert(`✅ "${newGroup.name}" 그룹이 생성되었습니다!`);
            createGroupModalInstance.hide();
            document.getElementById('createGroupForm').reset();
            fetchMyGroups();
        } else {
            const error = await response.json();
            alert(`❌ 그룹 생성 실패: ${error.detail}`);
        }
    } catch (error) {
        console.error('그룹 생성 실패:', error);
        alert('그룹 생성 중 오류가 발생했습니다.');
    }
}

/**
 * 랜덤 아이콘 생성
 */
function randomIcon() {
    const icons = ['🎯', '🚀', '⚡', '🔥', '💎', '🏆', '⭐', '🌟', '💪', '🎮', '🎨', '🎭', '🎪', '🎬', '🎸'];
    const randomIcon = icons[Math.floor(Math.random() * icons.length)];
    document.getElementById('groupIcon').value = randomIcon;
}

/**
 * 로그인 모달 표시
 */
function showLoginModal() {
    loginModalInstance.show();
}

/**
 * 로그인 처리
 */
async function handleLogin(e) {
    e.preventDefault();
    
    const handle = document.getElementById('loginHandle').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ handle, password })
        });
        
        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('access_token', data.access_token);
            alert(`환영합니다, ${handle}님!`);
            loginModalInstance.hide();
            document.getElementById('loginForm').reset();
            checkLoginStatus();
        } else {
            const error = await response.json();
            alert(`❌ 로그인 실패: ${error.detail}`);
        }
    } catch (error) {
        console.error('로그인 실패:', error);
        alert('로그인 중 오류가 발생했습니다.');
    }
}

/**
 * 로그아웃
 */
function logout() {
    if (confirm('로그아웃하시겠습니까?')) {
        // 1. 토큰 삭제
        localStorage.removeItem('access_token');
        
        // 2. 페이지 새로고침 (자동으로 히어로 섹션 표시됨)
        location.reload();
    }
}

/**
 * 그룹 입장
 */
function enterGroup(groupId) {
    window.location.href = `/group_detail.html?id=${groupId}`;
}

/**
 * HTML 이스케이프
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
