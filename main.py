import os, sys
from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, joinedload
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QFormLayout, QLineEdit, QLabel, QPushButton, QTabWidget, 
                             QWidget, QDateEdit, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView)

Base = declarative_base()

class Patient(Base):
    __tablename__ = 'patients'
    id = Column(Integer, primary_key=True)
    id_number = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    birth_date = Column(Date)
    visits = relationship("Visit", back_populates="patient")

class Visit(Base):
    __tablename__ = "visits"

    id = Column(Integer, primary_key=True)
    visit_date = Column(Date)
    payment_amount = Column(String)
    patient_id = Column(String, ForeignKey("patients.id"))
    patient_last_name = Column(String)

    patient = relationship("Patient", back_populates="visits")

# Set up the database
DATABASE_FILE = "medical.db"
engine = create_engine(f"sqlite:///{DATABASE_FILE}")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Define functions to insert, update, and retrieve data
def add_patient(id_number, first_name, last_name, birth_date):
    patient = Patient(id_number=id_number, first_name=first_name, last_name=last_name, birth_date=birth_date)
    session.add(patient)
    session.commit()

def update_patient(id_number, **kwargs):
    patient = session.query(Patient).filter(Patient.id_number == id_number).one()
    for key, value in kwargs.items():
        setattr(patient, key, value)
    session.commit()

def get_patients(id_number=None, last_name=None):
    with Session() as session:
        if id_number:
            patients = session.query(Patient).filter(Patient.id_number == id_number).all()
        elif last_name:
            patients = session.query(Patient).filter(Patient.last_name == last_name).all()
        else:
            patients = []
    return patients

def add_visit(patient_id, visit_date, payment_amount, last_name):
    visit = Visit(patient_id=patient_id, visit_date=visit_date, payment_amount=payment_amount, patient_last_name=last_name)
    session.add(visit)
    session.commit()

def get_visits(patient_id=None, last_name=None):
    with Session() as session:
        if patient_id:
            visits = session.query(Visit).options(joinedload(Visit.patient)).filter(Visit.patient_id == patient_id).all()
        elif last_name:
            visits = session.query(Visit).options(joinedload(Visit.patient)).join(Patient, Patient.id == Visit.patient_id).filter(Patient.last_name == last_name).all()
        else:
            visits = []
    return visits

class MedicalApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Doctor's Reception Desk")

        main_layout = QVBoxLayout()

        tab_widget = QTabWidget()
        tab_widget.setMinimumWidth(850)
        tab_widget.addTab(self.create_patient_registration_tab(), "Patient Registration")
        tab_widget.addTab(self.create_visit_information_tab(), "Visit Information")
        main_layout.addWidget(tab_widget)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def create_patient_registration_tab(self):
        form_layout = QFormLayout()

        self.first_name_input = QLineEdit()
        self.last_name_input = QLineEdit()
        self.birth_date_input = QDateEdit()
        self.id_number_input = QLineEdit()
        register_button = QPushButton("Register")

        register_button.clicked.connect(self.handle_register_patient)

        form_layout.addRow(QLabel("First Name:"), self.first_name_input)
        form_layout.addRow(QLabel("Last Name:"), self.last_name_input)
        form_layout.addRow(QLabel("Birth Date:"), self.birth_date_input)
        form_layout.addRow(QLabel("ID Number:"), self.id_number_input)
        form_layout.addRow(register_button)
        
        load_patient_button = QPushButton("Load Patient")
        load_patient_button.clicked.connect(self.handle_load_patient)
        form_layout.addRow(load_patient_button)

        info_layout = QVBoxLayout()
        self.patient_table = QTableWidget()
        self.patient_table.setColumnCount(4)
        self.patient_table.setHorizontalHeaderLabels(["ID", "First Name", "Last Name", "Birth Date"])
        self.patient_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        info_layout.addWidget(self.patient_table)

        main_layout = QHBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addLayout(info_layout)

        patient_registration_tab = QWidget()
        patient_registration_tab.setLayout(main_layout)
        return patient_registration_tab

    def create_visit_information_tab(self):
        form_layout = QFormLayout()

        self.visit_date_input = QDateEdit()
        self.payment_amount_input = QLineEdit()
        self.patient_id_input = QLineEdit()
        self.patient_last_name_input = QLineEdit()
        add_visit_button = QPushButton("Add Visit")

        add_visit_button.clicked.connect(self.handle_add_visit)

        form_layout.addRow(QLabel("Visit Date:"), self.visit_date_input)
        form_layout.addRow(QLabel("Payment Amount:"), self.payment_amount_input)
        form_layout.addRow(QLabel("Patient ID:"), self.patient_id_input)
        form_layout.addRow(QLabel("Patient Last Name:"), self.patient_last_name_input)
        form_layout.addRow(add_visit_button)
        
        load_visit_button = QPushButton("Load Visit")
        load_visit_button.clicked.connect(self.handle_load_visit)
        form_layout.addRow(load_visit_button)

        info_layout = QVBoxLayout()
        self.visit_table = QTableWidget()
        self.visit_table.setColumnCount(4)
        self.visit_table.setHorizontalHeaderLabels(["Visit Date", "Payment Amount", "Patient ID", "Last Name"])
        self.visit_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        info_layout.addWidget(self.visit_table)

        main_layout = QHBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addLayout(info_layout)

        visit_information_tab = QWidget()
        visit_information_tab.setLayout(main_layout)
        return visit_information_tab
    
    def add_patient_to_table(self, id_number, first_name, last_name, birth_date):
        row = self.patient_table.rowCount()
        self.patient_table.insertRow(row)

        self.patient_table.setItem(row, 0, QTableWidgetItem(id_number))
        self.patient_table.setItem(row, 1, QTableWidgetItem(first_name))
        self.patient_table.setItem(row, 2, QTableWidgetItem(last_name))
        self.patient_table.setItem(row, 3, QTableWidgetItem(birth_date.isoformat()))
        
    def add_visit_to_table(self, visit_date, payment_amount, patient_id, last_name):
        row = self.visit_table.rowCount()
        self.visit_table.insertRow(row)

        self.visit_table.setItem(row, 0, QTableWidgetItem(visit_date.isoformat()))
        self.visit_table.setItem(row, 1, QTableWidgetItem(payment_amount))
        self.visit_table.setItem(row, 2, QTableWidgetItem(patient_id if patient_id is not None else ""))
        self.visit_table.setItem(row, 3, QTableWidgetItem(last_name if last_name is not None else ""))

    
    def handle_register_patient(self):
        first_name = self.first_name_input.text()
        last_name = self.last_name_input.text()
        birth_date = self.birth_date_input.date().toPyDate()
        id_number = self.id_number_input.text()

        if not first_name or not last_name or not id_number:
            QMessageBox.warning(self, "Missing Input", "Please fill out all required fields.")
            return

        patients = get_patients(id_number=id_number)
        if patients:
            update_patient(id_number, first_name=first_name, last_name=last_name, birth_date=birth_date)
        else:
            add_patient(id_number, first_name, last_name, birth_date)

        self.add_patient_to_table(id_number, first_name, last_name, birth_date)

        self.first_name_input.clear()
        self.last_name_input.clear()
        self.birth_date_input.clear()
        self.id_number_input.clear()

    def handle_add_visit(self):
        visit_date = self.visit_date_input.date().toPyDate()
        payment_amount = self.payment_amount_input.text()
        patient_id = self.patient_id_input.text()
        last_name = self.patient_last_name_input.text()

        if not patient_id or not payment_amount or not last_name:
            QMessageBox.warning(self, "Missing Input", "Please fill out all required fields.")
            return

        add_visit(patient_id, visit_date, payment_amount, last_name) 

        self.add_visit_to_table(visit_date, payment_amount, patient_id, last_name)

        self.visit_date_input.clear()
        self.payment_amount_input.clear()
        self.patient_id_input.clear()
        self.patient_last_name_input.clear()

    def handle_load_patient(self):
        id_number = self.id_number_input.text().strip()
        last_name = self.last_name_input.text().strip()

        if not id_number and not last_name:
            QMessageBox.warning(self, "Missing Input", "Please fill out the ID number or last name field.")
            return

        try:
            patients = get_patients(id_number=id_number, last_name=last_name)
            if not patients:
                QMessageBox.warning(self, "Error", "No patient found with the provided ID number or last name.")
                return
        except Exception as e:
            QMessageBox.warning(self, "Error", "An error occurred while fetching patient data.")
            return

        patient_info_text = ""
        for idx, patient in enumerate(patients, start=1):
            patient_info_text += f"Patient {idx}:\n"
            patient_info_text += f"Patient ID: {patient.id_number}\nFirst Name: {patient.first_name}\nLast Name: {patient.last_name}\nBirth Date: {patient.birth_date}\n\n"

        for patient in patients:
            self.add_patient_to_table(patient.id_number, patient.first_name, patient.last_name, patient.birth_date)

    def handle_load_visit(self):
        patient_id = self.patient_id_input.text().strip()
        last_name = self.patient_last_name_input.text().strip()

        if not patient_id and not last_name:
            QMessageBox.warning(self, "Missing Input", "Please fill out either the patient ID or the last name field.")
            return

        try:
            visit_data = get_visits(patient_id=patient_id, last_name=last_name)
        except Exception as e:
            QMessageBox.warning(self, "Error", "An error occurred while fetching visit data.")
            return

        visit_info_text = ""
        if patient_id:
            visit_info_text += f"Patient ID: {patient_id}\n\n"
        elif last_name:
            visit_info_text += f"Last Name: {last_name}\n\n"

        for idx, visit in enumerate(visit_data, start=1):
            visit_info_text += f"Visit {idx}:\nVisit Date: {visit.visit_date}\nPayment Amount: {visit.payment_amount}\n"
            if visit.patient is not None:
                visit_info_text += f"Patient ID: {visit.patient.id_number}\nLast Name: {visit.patient.last_name}\n\n"

        for visit in visit_data:
            if visit.patient:
                self.add_visit_to_table(visit.visit_date, visit.payment_amount, visit.patient.id_number, visit.patient.last_name)
            else:
                self.add_visit_to_table(visit.visit_date, visit.payment_amount, "", "")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MedicalApp()
    main_window.show()
    sys.exit(app.exec_())