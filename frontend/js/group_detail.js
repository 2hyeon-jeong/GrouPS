/**
 * BOJ Squad - 그룹 상세 페이지
 */

const API_BASE_URL = 'http://localhost:8000';
const TOKEN_KEY = 'access_token';

// URL에서 group_id 추출
const urlParams = new URLSearchParams(window.location.search);
const groupId = urlParams.get('id');

// 티어별 색상 매핑 (Solved.ac 티어)
const TIER_COLORS = {
    0: { name: 'Unranked', color: '#2d3436', bg: '#dfe6e9' },
    1: { name: 'Bronze V', color: '#ad5600', bg: '#f4e4d7' },
    2: { name: 'Bronze IV', color: '#ad5600', bg: '#f4e4d7' },
    3: { name: 'Bronze III', color: '#ad5600', bg: '#f4e4d7' },
    4: { name: 'Bronze II', color: '#ad5600', bg: '#f4e4d7' },
    5: { name: 'Bronze I', color: '#ad5600', bg: '#f4e4d7' },
    6: { name: 'Silver V', color: '#435f7a', bg: '#e8eef3' },
    7: { name: 'Silver IV', color: '#435f7a', bg: '#e8eef3' },
    8: { name: 'Silver III', color: '#435f7a', bg: '#e8eef3' },
    9: { name: 'Silver II', color: '#435f7a', bg: '#e8eef3' },
    10: { name: 'Silver I', color: '#435f7a', bg: '#e8eef3' },
    11: { name: 'Gold V', color: '#ec9a00', bg: '#fef5e0' },
    12: { name: 'Gold IV', color: '#ec9a00', bg: '#fef5e0' },
    13: { name: 'Gold III', color: '#ec9a00', bg: '#fef5e0' },
    14: { name: 'Gold II', color: '#ec9a00', bg: '#fef5e0' },
    15: { name: 'Gold I', color: '#ec9a00', bg: '#fef5e0' },
    16: { name: 'Platinum V', color: '#27e2a4', bg: '#e5f9f2' },
    17: { name: 'Platinum IV', color: '#27e2a4', bg: '#e5f9f2' },
    18: { name: 'Platinum III', color: '#27e2a4', bg: '#e5f9f2' },
    19: { name: 'Platinum II', color: '#27e2a4', bg: '#e5f9f2' },
    20: { name: 'Platinum I', color: '#27e2a4', bg: '#e5f9f2' },
    21: { name: 'Diamond V', color: '#00b4fc', bg: '#e0f4ff' },
    22: { name: 'Diamond IV', color: '#00b4fc', bg: '#e0f4ff' },
    23: { name: 'Diamond III', color: '#00b4fc', bg: '#e0f4ff' },
    24: { name: 'Diamond II', color: '#00b4fc', bg: '#e0f4ff' },
    25: { name: 'Diamond I', color: '#00b4fc', bg: '#e0f4ff' },
    26: { name: 'Ruby V', color: '#ff0062', bg: '#ffe0ed' },
    27: { name: 'Ruby IV', color: '#ff0062', bg: '#ffe0ed' },
    28: { name: 'Ruby III', color: '#ff0062', bg: '#ffe0ed' },
    29: { name: 'Ruby II', color: '#ff0062', bg: '#ffe0ed' },
    30: { name: 'Ruby I', color: '#ff0062', bg: '#ffe0ed' },
};

function getTierInfo(tier) {
    return TIER_COLORS[tier] || TIER_COLORS[0];
}

// 페이지 로드 시 실행
document.addEventListener('DOMContentLoaded', async () => {
    const token = localStorage.getItem(TOKEN_KEY);
    
    if (!token) {
        alert('로그인이 필요합니다.');
        window.location.href = '/login.html';
        return;
    }
    
    if (!groupId) {
        alert('잘못된 접근입니다.');
        window.location.href = '/';
        return;
    }
    
    await loadUserInfo();
    await loadGroupDetail();
});

// 사용자 정보 로드
async function loadUserInfo() {
    const token = localStorage.getItem(TOKEN_KEY);
    
    try {
        const response = await fetch(`${API_BASE_URL}/users/me`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const user = await response.json();
            document.getElementById('userHandle').textContent = user.handle;
        }
    } catch (error) {
        console.error('Failed to load user info:', error);
    }
}

// 그룹 상세 정보 로드
async function loadGroupDetail() {
    const token = localStorage.getItem(TOKEN_KEY);
    
    try {
        const response = await fetch(`${API_BASE_URL}/groups/${groupId}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            if (response.status === 404) {
                alert('존재하지 않는 그룹입니다.');
                window.location.href = '/';
                return;
            }
            throw new Error('Failed to load group detail');
        }
        
        const groupData = await response.json();
        renderGroupInfo(groupData);
        renderMembers(groupData.members);
        renderActionButtons(groupData);
        
    } catch (error) {
        console.error('Error loading group detail:', error);
        alert('그룹 정보를 불러오는데 실패했습니다.');
    }
}

// 그룹 정보 렌더링
function renderGroupInfo(group) {
    document.getElementById('groupIcon').textContent = group.icon;
    document.getElementById('groupName').textContent = group.name;
    document.getElementById('groupDescription').textContent = group.description || '설명이 없습니다.';
    document.getElementById('memberCount').textContent = group.member_count;
    document.getElementById('maxMembers').textContent = group.max_members;
}

// 멤버 리스트 렌더링
function renderMembers(members) {
    const membersList = document.getElementById('membersList');
    
    if (!members || members.length === 0) {
        membersList.innerHTML = `
            <div class="text-center text-muted py-4">
                <p>멤버가 없습니다.</p>
            </div>
        `;
        return;
    }
    
    membersList.innerHTML = members.map(member => {
        const tierInfo = getTierInfo(member.tier);
        const roleClass = member.role === 'admin' ? 'admin' : '';
        const roleIcon = member.role === 'admin' ? '<i class="bi bi-star-fill"></i> ' : '';
        
        return `
            <div class="member-card">
                <div class="member-header">
                    <div>
                        <h6 class="mb-1">
                            <a href="https://solved.ac/profile/${member.handle}" target="_blank" class="text-decoration-none text-dark fw-bold">
                                ${member.handle}
                            </a>
                            <span class="role-badge ${roleClass}">${roleIcon}${member.role === 'admin' ? '방장' : '멤버'}</span>
                        </h6>
                        <small class="text-muted">
                            <i class="bi bi-calendar-check"></i> ${new Date(member.joined_at).toLocaleDateString()}
                        </small>
                    </div>
                </div>
                <div class="d-flex justify-content-between align-items-center mt-2">
                    <span class="tier-badge" style="background-color: ${tierInfo.bg}; color: ${tierInfo.color};">
                        ${tierInfo.name}
                    </span>
                    <span class="text-muted">
                        <i class="bi bi-check-circle-fill text-success"></i> ${member.solved_count}문제
                    </span>
                </div>
            </div>
        `;
    }).join('');
}

// 액션 버튼 렌더링
function renderActionButtons(group) {
    const actionButtons = document.getElementById('actionButtons');
    
    if (group.is_member) {
        // 이미 멤버인 경우
        actionButtons.innerHTML = `
            <button class="btn btn-light btn-lg me-2" onclick="copyInviteLink()">
                <i class="bi bi-link-45deg"></i> 초대 링크 복사
            </button>
            <button class="btn btn-outline-light btn-lg" onclick="leaveGroup()">
                <i class="bi bi-box-arrow-right"></i> 탈퇴하기
            </button>
        `;
    } else {
        // 멤버가 아닌 경우
        if (group.member_count >= group.max_members) {
            actionButtons.innerHTML = `
                <button class="btn btn-secondary btn-lg" disabled>
                    <i class="bi bi-lock-fill"></i> 정원 초과
                </button>
            `;
        } else {
            actionButtons.innerHTML = `
                <button class="btn btn-light btn-lg" onclick="joinGroup()">
                    <i class="bi bi-box-arrow-in-right"></i> 가입하기
                </button>
            `;
        }
    }
}

// 그룹 가입
async function joinGroup() {
    const token = localStorage.getItem(TOKEN_KEY);
    
    // 비공개 그룹인 경우 비밀번호 입력 받기 (추후 구현)
    const password = null;
    
    try {
        const response = await fetch(`${API_BASE_URL}/groups/${groupId}/join`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('그룹에 가입되었습니다!');
            location.reload();  // 페이지 새로고침
        } else {
            alert(data.detail || '그룹 가입에 실패했습니다.');
        }
    } catch (error) {
        console.error('Error joining group:', error);
        alert('그룹 가입 중 오류가 발생했습니다.');
    }
}

// 그룹 탈퇴
function leaveGroup() {
    if (confirm('정말로 이 그룹에서 탈퇴하시겠습니까?')) {
        alert('탈퇴 기능은 곧 구현 예정입니다.');
    }
}

// 초대 링크 복사
function copyInviteLink() {
    const inviteLink = `${window.location.origin}/group_detail.html?id=${groupId}`;
    
    navigator.clipboard.writeText(inviteLink).then(() => {
        alert('초대 링크가 복사되었습니다!\n\n' + inviteLink);
    }).catch(err => {
        console.error('Failed to copy link:', err);
        alert('링크 복사에 실패했습니다.');
    });
}
