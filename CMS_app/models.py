from django.db import models
from datetime import date
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group,User
# Create your models here.

# roles = ["Admin", "Receptionist", "Doctor", "Lab Technician", "Pharmacist"]
# for role in roles:
#     Group.objects.get_or_create(name=role) 

class Receptionist(models.Model):
    rec_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    dob = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=10, unique=True)
    email = models.EmailField(unique=True)
    qualification = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class Department(models.Model):
    department_id = models.AutoField(primary_key=True)
    department_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.department_name
    
class Doctor(models.Model):
    SPECIALIZATION_CHOICES = [
    ('Cardiology', 'Cardiology'),
    ('Dermatology', 'Dermatology'),
    ('Neurology', 'Neurology'),
    ('Orthopedics', 'Orthopedics'),
    ('Pediatrics', 'Pediatrics'),
    ('General Medicine', 'General Medicine'),
]
    doc_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    doc_name = models.CharField(max_length=100)
    dob = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=10, unique=True)
    email = models.EmailField(unique=True)
    specialization = models.CharField(max_length=50, choices=SPECIALIZATION_CHOICES)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    consultation_time = models.TimeField()
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.doc_name} - {self.specialization}"
    
class LabTechnician(models.Model):
    lab_tech_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Foreign Key to User
    name = models.CharField(max_length=255)
    dob = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=10, unique=True)
    email_id = models.EmailField(unique=True)
    qualification = models.CharField(max_length=255)
    salary = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name
    
class Pharmacist(models.Model):
    pharm_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Foreign Key to User
    name = models.CharField(max_length=255)
    dob = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=10, unique=True)
    email_id = models.EmailField(unique=True)
    qualification = models.CharField(max_length=255)
    salary = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name
    
class Patient(models.Model):
    patient_id = models.AutoField(primary_key=True)
    registration_id = models.CharField(max_length=10, unique=True)  # PR1000 format
    full_name = models.CharField(max_length=255)
    address = models.TextField()
    dob = models.DateField(null=True, blank=True)
    gender_choices = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    gender = models.CharField(max_length=1, choices=gender_choices)
    blood_group_choices = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B-'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('AB+', 'AB+'), ('AB-', 'AB-')
    ]
    blood_group = models.CharField(max_length=3, choices=blood_group_choices)
    phone_number = models.CharField(max_length=10, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """ Auto-generate registration ID in the format PR1000, PR1001, etc. """
        if not self.registration_id:
            last_patient = Patient.objects.order_by('-id').first()
            last_id = int(last_patient.registration_id[2:]) if last_patient else 999
            self.registration_id = f'PR{last_id + 1}'
        
        

    def __str__(self):
        return f"{self.full_name} ({self.registration_id})"
    
class Token(models.Model):
    token_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE)
    token_number = models.IntegerField()
    issued_at = models.DateTimeField(auto_now_add=True)
    

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    appointment_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE)
    department = models.ForeignKey('Department', on_delete=models.CASCADE)
    token = models.OneToOneField('Token', on_delete=models.CASCADE)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='scheduled')

    def __str__(self):
        return f"Appointment {self.appointment_id} - {self.patient.full_name} with {self.doctor.doc_name} on {self.appointment_date} at {self.appointment_time}"
    
    def clean(self):
        """ Validate that the appointment date is not in the past """
        if self.appointment_date < date.today():
            raise ValidationError("Appointment date cannot be in the past.")
        
class AppointmentBilling(models.Model):
    appointment_bill_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)
    appointment = models.ForeignKey('Appointment', on_delete=models.CASCADE)
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    service_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    gst = models.DecimalField(max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"Bill {self.appointment_bill_id} - {self.patient.full_name} for Appointment {self.appointment.appointment_id}"

    def clean(self):
        """Validate that the consultation_fee matches the doctor's set consultation_fee."""
        if self.doctor and self.consultation_fee != self.doctor.consultation_fee:
            raise ValidationError({'consultation_fee': 'Consultation fee must match the assigned doctor\'s fee.'})

    def save(self, *args, **kwargs):
        """Automatically fetch and set the consultation fee and calculate the total amount before saving."""
        if self.doctor:
            self.consultation_fee = self.doctor.consultation_fee  # Ensure the fee matches the doctor's fee
        self.total_amount = self.consultation_fee + self.service_charge + self.gst
        self.full_clean()  # Run validations before saving
        super().save(*args, **kwargs)

class Medicine(models.Model):
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Not Available', 'Not Available'),
    ]

    medicine_id = models.AutoField(primary_key=True)
    medicine_name = models.CharField(max_length=255, unique=True)
    generic_name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    stock_quantity = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Available')

    def __str__(self):
        return f"{self.medicine_name} - {self.company_name}"

    def save(self, *args, **kwargs):
        """Automatically update the status based on stock availability."""
        if self.stock_quantity == 0:
            self.status = 'Not Available'
        else:
            self.status = 'Available'
        super().save(*args, **kwargs)

class Prescription(models.Model):
    prescription_id = models.AutoField(primary_key=True)
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE)
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)
    diagnosis = models.TextField()
    prescription_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Prescription {self.prescription_id} - Dr.{self.doctor.doc_name} for {self.patient.full_name}"
    
class PrescriptionMedicine(models.Model):
    prescription = models.ForeignKey('Prescription', on_delete=models.CASCADE, related_name='medicines')
    medicine = models.ForeignKey('Medicine', on_delete=models.CASCADE)
    number_of_days = models.PositiveIntegerField()
    dosage = models.CharField(max_length=50)
    frequency = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.medicine.medicine_name} ({self.dosage}, {self.frequency})"
    
class LabTest(models.Model):
    test_id = models.AutoField(primary_key=True)
    test_name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.test_name} - ₹{self.price}"
    
class LabReport(models.Model):
    report_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)
    doctor = models.ForeignKey('Doctor', on_delete=models.SET_NULL, null=True, blank=True)
    test = models.ForeignKey('LabTest', on_delete=models.CASCADE)
    normal_range = models.CharField(max_length=100)
    actual_value = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report {self.report_id} - {self.test.test_name} for {self.patient.full_name}"
    
class LabTestBill(models.Model):
    l_bill_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)
    test = models.ForeignKey('LabTest', on_delete=models.CASCADE)
    doctor = models.ForeignKey('Doctor', on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    gst = models.DecimalField(max_digits=5, decimal_places=2, help_text="GST percentage")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        """Auto-calculate total_amount including GST."""
        self.total_amount = self.price + (self.price * self.gst / 100)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Lab Bill {self.l_bill_id} - {self.test.test_name} for {self.patient.full_name}"
    
    
class MedicineBill(models.Model):
    bill_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)
    doctor = models.ForeignKey('Doctor', on_delete=models.SET_NULL, null=True, blank=True)
    medicine = models.ForeignKey('Medicine', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    gst = models.DecimalField(max_digits=5, decimal_places=2, help_text="GST percentage")
    total = models.DecimalField(max_digits=10, decimal_places=2, editable=False)  # Auto-calculated
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Paid', 'Paid')], default='Pending')

    def save(self, *args, **kwargs):
        """ Automatically calculate total price including GST before saving """
        self.total = self.price + (self.price * self.gst / 100)
        super(MedicineBill, self).save(*args, **kwargs)

    def __str__(self):
        return f"Bill {self.bill_id} - {self.patient.full_name} - {self.medicine.medicine_name}"