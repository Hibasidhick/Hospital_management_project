from django.contrib import admin
from .models import Receptionist,Department,Doctor,LabTechnician,Pharmacist,Patient,Token,Appointment,AppointmentBilling,Medicine,Prescription,PrescriptionMedicine,LabTest,LabReport,LabTestBill,MedicineBill
# Register your models here.

admin.site.register(Receptionist)
admin.site.register(Department)
admin.site.register(Doctor)
admin.site.register(LabTechnician)
admin.site.register(Pharmacist)
admin.site.register(Patient)
admin.site.register(Token)
admin.site.register(Appointment)
admin.site.register(AppointmentBilling)
admin.site.register(Medicine)
admin.site.register(Prescription)
admin.site.register(PrescriptionMedicine)
admin.site.register(LabTest)
admin.site.register(LabReport)
admin.site.register(LabTestBill)
admin.site.register(MedicineBill)
