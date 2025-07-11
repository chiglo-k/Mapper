from sqlalchemy import Column, String, Integer, JSON, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from src.Backend.database.database import Base


class Mapping(Base):

    __tablename__ = 'mapping_info'

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects_info.id"))
    name = Column(String(255), nullable=False)
    source_format = Column(String(20), nullable=False)
    mapping_rules = Column(JSON, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    project = relationship("Project_Data", back_populates="mappings")