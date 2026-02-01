"""
그룹 및 미션 관리 API 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models import Group, GroupMember, GroupMission, MissionProblem, Problem, SolvedLog, User
from app.schemas import (
    GroupCreate,
    GroupResponse,
    GroupDetailResponse,
    GroupJoinRequest,
    MemberInfo,
    MissionCreate,
    MissionResponse,
    MissionProblemResponse,
    MissionStatusResponse,
    MemberSolveDetail
)
from app.api.deps import get_current_user
from app.services.solved_client import get_solved_client
from app.core.security import get_password_hash, verify_password
from sqlalchemy import func

router = APIRouter()


@router.post("", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
async def create_group(
    group_data: GroupCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    그룹 생성
    
    - 그룹명, 설명, 아이콘, 최대 인원 수 설정
    - 비밀번호 설정 시 비공개 그룹
    - 생성자가 자동으로 방장이 됨
    """
    # 1. 그룹명 중복 체크
    result = await db.execute(select(Group).where(Group.name == group_data.name))
    existing_group = result.scalar_one_or_none()
    
    if existing_group:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 존재하는 그룹명입니다"
        )
    
    # 2. 그룹 생성
    new_group = Group(
        name=group_data.name,
        description=group_data.description,
        owner_id=current_user.id,
        icon=group_data.icon,
        max_members=group_data.max_members,
        password=get_password_hash(group_data.password) if group_data.password else None
    )
    
    db.add(new_group)
    await db.flush()
    
    # 3. 방장을 멤버로 자동 추가
    group_member = GroupMember(
        group_id=new_group.id,
        user_id=current_user.id,
        role="admin"
    )
    db.add(group_member)
    
    await db.commit()
    await db.refresh(new_group)
    
    # 4. 멤버 수 계산
    result = await db.execute(
        select(func.count(GroupMember.user_id)).where(GroupMember.group_id == new_group.id)
    )
    member_count = result.scalar()
    
    return GroupResponse(
        id=new_group.id,
        name=new_group.name,
        description=new_group.description,
        owner_id=new_group.owner_id,
        icon=new_group.icon,
        max_members=new_group.max_members,
        member_count=member_count,
        created_at=new_group.created_at
    )


@router.get("/my", response_model=List[GroupResponse])
async def get_my_groups(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    내가 가입한 그룹 목록 조회
    """
    # 내가 멤버인 그룹 조회
    result = await db.execute(
        select(Group)
        .join(GroupMember)
        .where(GroupMember.user_id == current_user.id)
        .order_by(Group.created_at.desc())
    )
    groups = result.scalars().all()
    
    # 각 그룹의 멤버 수 계산
    group_responses = []
    for group in groups:
        result = await db.execute(
            select(func.count(GroupMember.user_id)).where(GroupMember.group_id == group.id)
        )
        member_count = result.scalar()
        
        group_responses.append(GroupResponse(
            id=group.id,
            name=group.name,
            description=group.description,
            owner_id=group.owner_id,
            icon=group.icon,
            max_members=group.max_members,
            member_count=member_count,
            created_at=group.created_at
        ))
    
    return group_responses


@router.get("/ranking", response_model=List[dict])
async def get_group_ranking(
    db: AsyncSession = Depends(get_db),
    limit: int = 5
):
    """
    그룹 랭킹 (해결 문제 수 기준 TOP N)
    """
    # 각 그룹의 멤버들이 푼 문제 수 합계 계산
    result = await db.execute(
        select(
            Group.id,
            Group.name,
            Group.icon,
            func.count(func.distinct(SolvedLog.problem_id)).label("total_solved")
        )
        .join(GroupMember, Group.id == GroupMember.group_id)
        .join(SolvedLog, GroupMember.user_id == SolvedLog.user_id)
        .group_by(Group.id, Group.name, Group.icon)
        .order_by(func.count(func.distinct(SolvedLog.problem_id)).desc())
        .limit(limit)
    )
    
    rankings = []
    for idx, row in enumerate(result.all(), start=1):
        rankings.append({
            "rank": idx,
            "group_id": row.id,
            "group_name": row.name,
            "icon": row.icon,
            "total_solved": row.total_solved
        })
    
    return rankings


@router.get("/{group_id}", response_model=GroupDetailResponse)
async def get_group_detail(
    group_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    그룹 상세 정보 조회 (멤버 리스트 포함)
    
    - 그룹 기본 정보 (이름, 설명, 아이콘 등)
    - 멤버 리스트 (핸들, 티어, 푼 문제 수, 역할, 가입일)
    - 현재 사용자가 멤버인지 여부
    """
    # 1. 그룹 존재 여부 확인
    result = await db.execute(select(Group).where(Group.id == group_id))
    group = result.scalar_one_or_none()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="존재하지 않는 그룹입니다"
        )
    
    # 2. 멤버 목록 조회 (User와 GroupMember를 조인)
    result = await db.execute(
        select(User, GroupMember)
        .join(GroupMember, User.id == GroupMember.user_id)
        .where(GroupMember.group_id == group_id)
        .order_by(GroupMember.joined_at.asc())  # 가입 순서대로
    )
    
    members_data = result.all()
    
    members = []
    is_member = False
    
    for user, group_member in members_data:
        if user.id == current_user.id:
            is_member = True
        
        members.append(MemberInfo(
            user_id=user.id,
            handle=user.handle,
            tier=user.tier,
            solved_count=user.solved_count,
            role=group_member.role,
            joined_at=group_member.joined_at
        ))
    
    # 3. 응답 생성
    return GroupDetailResponse(
        id=group.id,
        name=group.name,
        description=group.description,
        owner_id=group.owner_id,
        icon=group.icon,
        max_members=group.max_members,
        member_count=len(members),
        created_at=group.created_at,
        members=members,
        is_member=is_member
    )


@router.post("/{group_id}/join", status_code=status.HTTP_200_OK)
async def join_group(
    group_id: int,
    join_data: GroupJoinRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    그룹 가입
    
    - 비공개 그룹인 경우 비밀번호 확인
    - 이미 가입된 경우 에러
    - 최대 인원 초과 시 에러
    """
    # 1. 그룹 존재 여부 확인
    result = await db.execute(select(Group).where(Group.id == group_id))
    group = result.scalar_one_or_none()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="존재하지 않는 그룹입니다"
        )
    
    # 2. 이미 가입된 멤버인지 확인
    result = await db.execute(
        select(GroupMember)
        .where(GroupMember.group_id == group_id, GroupMember.user_id == current_user.id)
    )
    existing_member = result.scalar_one_or_none()
    
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 가입된 그룹입니다"
        )
    
    # 3. 비공개 그룹인 경우 비밀번호 확인
    if group.password:
        if not join_data.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="비공개 그룹입니다. 비밀번호를 입력해주세요."
            )
        
        if not verify_password(join_data.password, group.password):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="비밀번호가 올바르지 않습니다"
            )
    
    # 4. 최대 인원 체크
    result = await db.execute(
        select(func.count(GroupMember.user_id)).where(GroupMember.group_id == group_id)
    )
    current_member_count = result.scalar()
    
    if current_member_count >= group.max_members:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"그룹이 가득 찼습니다 (최대 {group.max_members}명)"
        )
    
    # 5. 멤버로 추가
    new_member = GroupMember(
        group_id=group_id,
        user_id=current_user.id,
        role="member"
    )
    
    db.add(new_member)
    await db.commit()
    
    return {
        "message": "그룹에 가입되었습니다",
        "group_id": group_id,
        "group_name": group.name
    }


@router.post("/{group_id}/missions", response_model=MissionResponse, status_code=status.HTTP_201_CREATED)
async def create_mission(
    group_id: int,
    mission_data: MissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    그룹 미션 생성 (방장 전용)
    
    - 제목, 기간, 문제 번호 리스트를 받아서 미션 생성
    - 문제 정보가 DB에 없으면 Solved.ac API로 가져와서 저장 (Upsert)
    """
    # 1. 그룹 존재 여부 및 권한 확인
    result = await db.execute(select(Group).where(Group.id == group_id))
    group = result.scalar_one_or_none()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="존재하지 않는 그룹입니다"
        )
    
    # 방장인지 확인
    if group.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="그룹 방장만 미션을 생성할 수 있습니다"
        )
    
    # 2. 문제 정보 확인 및 Upsert
    solved_client = get_solved_client()
    problem_ids = mission_data.problem_ids
    
    # DB에 없는 문제 ID 찾기
    result = await db.execute(
        select(Problem.id).where(Problem.id.in_(problem_ids))
    )
    existing_problem_ids = set(result.scalars().all())
    missing_problem_ids = [pid for pid in problem_ids if pid not in existing_problem_ids]
    
    # 없는 문제는 API에서 가져오기
    if missing_problem_ids:
        print(f"🔍 DB에 없는 문제 {len(missing_problem_ids)}개를 Solved.ac에서 가져옵니다...")
        problems_data = await solved_client.fetch_problems_detail(missing_problem_ids)
        
        # DB에 저장
        for problem_data in problems_data:
            problem_id = problem_data.get("problemId")
            title = problem_data.get("titleKo", "")
            level = problem_data.get("level", 0)
            tags = problem_data.get("tags", [])
            
            new_problem = Problem(
                id=problem_id,
                title=title,
                level=level,
                tags=tags
            )
            db.add(new_problem)
        
        await db.commit()
        print(f"✅ {len(problems_data)}개 문제 정보 저장 완료")
    
    # 3. 미션 생성
    new_mission = GroupMission(
        group_id=group_id,
        title=mission_data.title,
        description=mission_data.description,
        start_date=mission_data.start_date,
        end_date=mission_data.end_date
    )
    
    db.add(new_mission)
    await db.flush()  # ID 생성
    
    # 4. 미션-문제 연결
    for idx, problem_id in enumerate(problem_ids):
        mission_problem = MissionProblem(
            mission_id=new_mission.id,
            problem_id=problem_id,
            order=idx
        )
        db.add(mission_problem)
    
    await db.commit()
    await db.refresh(new_mission)
    
    # 5. 응답 생성 (문제 정보 포함)
    result = await db.execute(
        select(Problem)
        .join(MissionProblem)
        .where(MissionProblem.mission_id == new_mission.id)
        .order_by(MissionProblem.order)
    )
    problems = result.scalars().all()
    
    return MissionResponse(
        id=new_mission.id,
        group_id=new_mission.group_id,
        title=new_mission.title,
        description=new_mission.description,
        start_date=new_mission.start_date,
        end_date=new_mission.end_date,
        created_at=new_mission.created_at,
        problems=[
            MissionProblemResponse(
                id=p.id,
                title=p.title,
                level=p.level
            )
            for p in problems
        ]
    )


@router.get("/{group_id}/missions/{mission_id}/status", response_model=MissionStatusResponse)
async def get_mission_status(
    group_id: int,
    mission_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    미션 현황판 조회 (핵심 기능)
    
    - 그룹의 모든 멤버에 대해 미션 문제 풀이 현황을 확인
    - SolvedLog를 통해 각 멤버가 어떤 문제를 풀었는지 체크
    """
    # 1. 미션 정보 조회
    result = await db.execute(
        select(GroupMission)
        .where(GroupMission.id == mission_id, GroupMission.group_id == group_id)
    )
    mission = result.scalar_one_or_none()
    
    if not mission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="존재하지 않는 미션입니다"
        )
    
    # 2. 미션에 포함된 문제 목록 조회
    result = await db.execute(
        select(Problem)
        .join(MissionProblem)
        .where(MissionProblem.mission_id == mission_id)
        .order_by(MissionProblem.order)
    )
    problems = result.scalars().all()
    problem_ids = [p.id for p in problems]
    
    if not problems:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="미션에 문제가 없습니다"
        )
    
    # 3. 그룹 멤버 목록 조회
    result = await db.execute(
        select(User)
        .join(GroupMember)
        .where(GroupMember.group_id == group_id)
    )
    members = result.scalars().all()
    
    # 4. 각 멤버의 풀이 현황 계산
    members_status = []
    
    for member in members:
        # 해당 멤버가 푼 문제 조회 (미션 문제 중에서)
        result = await db.execute(
            select(SolvedLog.problem_id)
            .where(
                SolvedLog.user_id == member.id,
                SolvedLog.problem_id.in_(problem_ids)
            )
            .distinct()
        )
        solved_problem_ids = set(result.scalars().all())
        
        # 문제별 풀이 여부
        details = {pid: (pid in solved_problem_ids) for pid in problem_ids}
        
        solved_count = len(solved_problem_ids)
        total_count = len(problem_ids)
        completion_rate = round((solved_count / total_count * 100), 2) if total_count > 0 else 0.0
        
        members_status.append(MemberSolveDetail(
            handle=member.handle,
            solved_count=solved_count,
            total_count=total_count,
            completion_rate=completion_rate,
            details=details
        ))
    
    # 5. 응답 생성
    return MissionStatusResponse(
        mission_id=mission.id,
        mission_title=mission.title,
        start_date=mission.start_date,
        end_date=mission.end_date,
        problems=[
            MissionProblemResponse(
                id=p.id,
                title=p.title,
                level=p.level
            )
            for p in problems
        ],
        members_status=members_status
    )


@router.get("/{group_id}/missions", response_model=List[MissionResponse])
async def get_group_missions(
    group_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    그룹의 모든 미션 목록 조회
    """
    # 그룹 존재 여부 확인
    result = await db.execute(select(Group).where(Group.id == group_id))
    group = result.scalar_one_or_none()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="존재하지 않는 그룹입니다"
        )
    
    # 미션 목록 조회
    result = await db.execute(
        select(GroupMission)
        .where(GroupMission.group_id == group_id)
        .order_by(GroupMission.created_at.desc())
    )
    missions = result.scalars().all()
    
    # 각 미션의 문제 목록 조회
    mission_responses = []
    for mission in missions:
        result = await db.execute(
            select(Problem)
            .join(MissionProblem)
            .where(MissionProblem.mission_id == mission.id)
            .order_by(MissionProblem.order)
        )
        problems = result.scalars().all()
        
        mission_responses.append(MissionResponse(
            id=mission.id,
            group_id=mission.group_id,
            title=mission.title,
            description=mission.description,
            start_date=mission.start_date,
            end_date=mission.end_date,
            created_at=mission.created_at,
            problems=[
                MissionProblemResponse(
                    id=p.id,
                    title=p.title,
                    level=p.level
                )
                for p in problems
            ]
        ))
    
    return mission_responses
