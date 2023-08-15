from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

DATABASE_URL = "sqlite:///medical.db"

class Patient(Base):
    __tablename__ = 'patients'
    id = Column(Integer, primary_key=True)
    id_number = Column(String, unique=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    visits = relationship("Visit", back_populates="patient")

class Visit(Base):
    __tablename__ = 'visits'
    id = Column(Integer, primary_key=True)
    visit_date = Column(Date, nullable=False)
    payment_amount = Column(Integer, nullable=False)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
    patient = relationship("Patient", back_populates="visits")

if __name__ == "__main__":
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)