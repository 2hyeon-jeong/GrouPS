"""
User 모델
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    """사용자 모델"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, comment="사용자 고유 ID")
    handle = Column(
        String(50), 
        unique=True, 
        index=True, 
        nullable=False, 
        comment="백준 아이디"
    )
    password_hash = Column(
        String(255), 
        nullable=False, 
        comment="해시된 비밀번호"
    )
    tier = Column(
        Integer, 
        default=0, 
        index=True, 
        nullable=False,
        comment="Solved.ac 티어 레벨 (0~30)"
    )
    solved_count = Column(
        Integer, 
        default=0, 
        nullable=False,
        comment="푼 문제 개수"
    )
    created_at = Column(
        DateTime, 
        default=datetime.utcnow, 
        nullable=False, 
        comment="가입일시"
    )
    
    # 관계 설정
    # N:M - GroupMember를 통해 Group과 연결
    group_memberships = relationship(
        "GroupMember", 
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    # 1:N - 소유한 그룹들
    owned_groups = relationship(
        "Group", 
        back_populates="owner",
        foreign_keys="Group.owner_id"
    )
    
    # 1:N - 문제 풀이 기록
    solved_logs = relationship(
        "SolvedLog", 
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, handle={self.handle}, tier={self.tier})>"
