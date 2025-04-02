from rest_framework import serializers
from datetime import date, timedelta
from .models import (
    Receptionist, Department, Doctor, LabTechnician, Pharmacist,
    Patient, Token, Appointment, AppointmentBilling, Medicine,
    Prescription, PrescriptionMedicine, LabTest, LabReport,
    LabTestBill, MedicineBill
)

def validate_dob(value):
    """
    Validate date of birth is between 1900-01-01 and today's date
    """
    min_date = date(1900, 1, 1)
    if value < min_date:
        raise serializers.ValidationError(f"Date of birth must be after {min_date}")
    if value > date.today():
        raise serializers.ValidationError("Date of birth cannot be in the future")
    return value

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class DoctorSerializer(serializers.ModelSerializer):
    dob = serializers.DateField(validators=[validate_dob])
    
    class Meta:
        model = Doctor
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'phone_number': {'required': True}
        }

class ReceptionistSerializer(serializers.ModelSerializer):
    dob = serializers.DateField(validators=[validate_dob])
    
    class Meta:
        model = Receptionist
        fields = '__all__'
        extra_kwargs = {
            'email': {'required': True},
            'phone_number': {'required': True}
        }

class LabTechnicianSerializer(serializers.ModelSerializer):
    dob = serializers.DateField(validators=[validate_dob])
    
    class Meta:
        model = LabTechnician
        fields = '__all__'
        extra_kwargs = {
            'email_id': {'required': True},
            'phone_number': {'required': True}
        }

class PharmacistSerializer(serializers.ModelSerializer):
    dob = serializers.DateField(validators=[validate_dob])
    
    class Meta:
        model = Pharmacist
        fields = '__all__'
        extra_kwargs = {
            'email_id': {'required': True},
            'phone_number': {'required': True}
        }

class PatientSerializer(serializers.ModelSerializer):
    dob = serializers.DateField(validators=[validate_dob])
    
    class Meta:
        model = Patient
        fields = '__all__'
        extra_kwargs = {
            'phone_number': {'required': True},
            'blood_group': {'required': True},
            'gender': {'required': True}
        }

    def validate_phone_number(self, value):
        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError("Phone number must be 10 digits")
        return value

class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = '__all__'

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'
    
    def validate(self, data):
        if data['appointment_date'] < date.today():
            raise serializers.ValidationError("Appointment date cannot be in the past")
        
        # Check if doctor is available at that time
        conflicting_appointments = Appointment.objects.filter(
            doctor=data['doctor'],
            appointment_date=data['appointment_date'],
            appointment_time=data['appointment_time'],
            status='scheduled'
        ).exclude(pk=self.instance.pk if self.instance else None)
        
        if conflicting_appointments.exists():
            raise serializers.ValidationError("Doctor already has an appointment at this time")
        
        return data

class AppointmentBillingSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentBilling
        fields = '__all__'
    
    def validate(self, data):
        if data['consultation_fee'] != data['doctor'].consultation_fee:
            raise serializers.ValidationError(
                {"consultation_fee": "Must match doctor's consultation fee"}
            )
        return data

class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = '__all__'
    
    def validate_price_per_unit(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value

class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = '__all__'

class PrescriptionMedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrescriptionMedicine
        fields = '__all__'
    
    def validate_number_of_days(self, value):
        if value <= 0:
            raise serializers.ValidationError("Number of days must be positive")
        return value

class LabTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabTest
        fields = '__all__'
    
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value

class LabReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabReport
        fields = '__all__'

class LabTestBillSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabTestBill
        fields = '__all__'
    
    def validate(self, data):
        if data['price'] != data['test'].price:
            raise serializers.ValidationError(
                {"price": "Must match test price"}
            )
        return data

class MedicineBillSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicineBill
        fields = '__all__'
    
    def validate(self, data):
        if data['price'] != data['medicine'].price_per_unit:
            raise serializers.ValidationError(
                {"price": "Must match medicine price"}
            )
        return data