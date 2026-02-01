"""
Problem & SolvedLog 모델
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.database import Base


class Problem(Base):
    """백준 문제 정보 캐싱 테이블"""
    __tablename__ = "problems"
    
    id = Column(
        Integer, 
        primary_key=True, 
        index=True,
        autoincrement=False,  # 백준 문제 번호를 직접 사용
        comment="백준 문제 번호"
    )
    title = Column(
        String(200), 
        nullable=False,
        comment="문제 제목"
    )
    level = Column(
        Integer,
        nullable=True,
        comment="문제 난이도 (Solved.ac 레벨)"
    )
    tags = Column(
        JSON,
        nullable=True,
        comment="문제 태그 (JSON 배열)"
    )
    
    # 관계 설정
    # 1:N - 이 문제를 푼 기록들
    solved_logs = relationship(
        "SolvedLog", 
        back_populates="problem",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Problem(id={self.id}, title={self.title}, level={self.level})>"


class SolvedLog(Base):
    """문제 풀이 기록 모델"""
    __tablename__ = "solved_logs"
    
    id = Column(Integer, primary_key=True, index=True, comment="기록 고유 ID")
    user_id = Column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, 
        index=True,
        comment="사용자 ID"
    )
    problem_id = Column(
        Integer, 
        ForeignKey("problems.id", ondelete="CASCADE"),
        nullable=False, 
        index=True,
        comment="백준 문제 번호"
    )
    solved_at = Column(
        DateTime, 
        default=datetime.utcnow, 
        nullable=False,
        index=True, 
        comment="풀이 완료 일시"
    )
    
    # 관계 설정
    user = relationship("User", back_populates="solved_logs")
    problem = relationship("Problem", back_populates="solved_logs")
    
    def __repr__(self):
        return f"<SolvedLog(id={self.id}, user_id={self.user_id}, problem_id={self.problem_id})>"
