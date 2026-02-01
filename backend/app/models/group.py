"""
Group & GroupMember 모델
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Group(Base):
    """그룹 모델"""
    __tablename__ = "groups"
    
    id = Column(Integer, primary_key=True, index=True, comment="그룹 고유 ID")
    name = Column(
        String(100), 
        unique=True, 
        index=True,
        nullable=False, 
        comment="그룹명"
    )
    description = Column(
        Text, 
        nullable=True, 
        comment="그룹 설명"
    )
    owner_id = Column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="그룹 소유자 ID"
    )
    icon = Column(
        String(10),
        default="🎯",
        nullable=False,
        comment="그룹 아이콘 (이모지)"
    )
    password = Column(
        String(255),
        nullable=True,
        comment="비공개 그룹 비밀번호 (해시)"
    )
    max_members = Column(
        Integer,
        default=10,
        nullable=False,
        comment="최대 멤버 수"
    )
    created_at = Column(
        DateTime, 
        default=datetime.utcnow, 
        nullable=False, 
        comment="생성일시"
    )
    
    # 관계 설정
    # N:1 - 그룹 소유자
    owner = relationship(
        "User", 
        back_populates="owned_groups",
        foreign_keys=[owner_id]
    )
    
    # N:M - GroupMember를 통해 User와 연결
    members = relationship(
        "GroupMember", 
        back_populates="group",
        cascade="all, delete-orphan"
    )
    
    # 1:N - 그룹의 미션들
    missions = relationship(
        "GroupMission",
        back_populates="group",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Group(id={self.id}, name={self.name}, owner_id={self.owner_id})>"


class GroupMember(Base):
    """그룹 멤버 연결 테이블 (Association Object)"""
    __tablename__ = "group_members"
    
    group_id = Column(
        Integer, 
        ForeignKey("groups.id", ondelete="CASCADE"),
        primary_key=True,
        comment="그룹 ID"
    )
    user_id = Column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        comment="사용자 ID"
    )
    role = Column(
        String(20),
        default="member",
        nullable=False,
        comment="역할: admin 또는 member"
    )
    joined_at = Column(
        DateTime, 
        default=datetime.utcnow, 
        nullable=False, 
        comment="가입일시"
    )
    
    # 관계 설정
    group = relationship("Group", back_populates="members")
    user = relationship("User", back_populates="group_memberships")
    
    def __repr__(self):
        return f"<GroupMember(group_id={self.group_id}, user_id={self.user_id}, role={self.role})>"


class GroupMission(Base):
    """그룹 미션 모델 (주차별 학습 목표)"""
    __tablename__ = "group_missions"
    
    id = Column(Integer, primary_key=True, index=True, comment="미션 고유 ID")
    group_id = Column(
        Integer,
        ForeignKey("groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="그룹 ID"
    )
    title = Column(
        String(200),
        nullable=False,
        comment="미션 제목 (예: 1주차 DP 부수기)"
    )
    description = Column(
        Text,
        nullable=True,
        comment="미션 설명"
    )
    start_date = Column(
        DateTime,
        nullable=False,
        comment="미션 시작일"
    )
    end_date = Column(
        DateTime,
        nullable=False,
        comment="미션 종료일"
    )
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="생성일시"
    )
    
    # 관계 설정
    # N:1 - 소속 그룹
    group = relationship("Group", back_populates="missions")
    
    # 1:N - 미션에 포함된 문제들
    mission_problems = relationship(
        "MissionProblem",
        back_populates="mission",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<GroupMission(id={self.id}, title={self.title}, group_id={self.group_id})>"


class MissionProblem(Base):
    """미션-문제 연결 테이블 (N:M)"""
    __tablename__ = "mission_problems"
    
    mission_id = Column(
        Integer,
        ForeignKey("group_missions.id", ondelete="CASCADE"),
        primary_key=True,
        comment="미션 ID"
    )
    problem_id = Column(
        Integer,
        ForeignKey("problems.id", ondelete="CASCADE"),
        primary_key=True,
        comment="문제 ID"
    )
    order = Column(
        Integer,
        default=0,
        nullable=False,
        comment="문제 순서"
    )
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="추가일시"
    )
    
    # 관계 설정
    mission = relationship("GroupMission", back_populates="mission_problems")
    problem = relationship("Problem")
    
    def __repr__(self):
        return f"<MissionProblem(mission_id={self.mission_id}, problem_id={self.problem_id})>"
