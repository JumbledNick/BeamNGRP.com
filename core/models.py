from django.contrib.auth.models import AbstractUser
from django.db import models
class User(AbstractUser):
    ROLE_CHOICES = [          
    ('admin', 'Admin'),
    ('business', 'Business Owner'),
    ('user', 'User'),
]
    email = models.EmailField(blank=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)

    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='user')
    
    bank_balance = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0.00)
    
    def __str__(self):
        return self.username

class Business(models.Model):
    owner = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='business'
    )

    name = models.CharField(max_length=255)

    balance = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0.00
    )

    def save(self, *args, **kwargs):
        if  self.owner.role != 'business':
            self.owner.role = 'business'
            self.owner.save()
        super().save(*args, **kwargs)
    
        def __str__(self):
            return self.name
    
class Industry(models.Model):
    Industry_Type = models.CharField(max_length=255)
    industry_Code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.Industry_Type
    
class Brand(models.Model):
    COUNTRY_CHOICES = [
        ('USA', 'United States'),
        ('JP', 'Japan'),
        ('UK', 'United Kingdom'),
        ('AUS', 'Australia'),
        ('GER', 'Germany'),
        ('FR', 'France'),
        ('IT', 'Italy'),
        ('CN', 'China'),
        ('KOR', 'South Korea'),
        ('RUS', 'Russia'),
    ]

    name = models.CharField(max_length=255)
    country = models.CharField(
        max_length=3,
        choices=COUNTRY_CHOICES
    )

    industries = models.ManyToManyField(Industry)

    is_defunct = models.BooleanField(default=False)

    def __str__(self):
        return self.name


 ## THE NEXT 200 LINES ARE SIMPLY TO GET EVERY CAR TRIM AND ENGINE IN THE DATABASE
 # THIS WAS HELL BUT IT WORKS   
class CarModel(models.Model):

    brand =models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='cars')
    carModel = models.CharField(max_length=100)

    start_year = models.PositiveIntegerField()
    end_year = models.PositiveIntegerField(null=True, blank=True)
    is_discontinued = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.end_year and self.end_year < self.start_year:
            raise ValueError("End year cannot be earlier than start year.")
        
        if self.end_year and self.end_year <= 2025:
            self.is_discontinued = True
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.start_year}-{self.end_year} {self.brand.name} {self.carModel}"

class Facelift(models.Model):
    car_model = models.ForeignKey(CarModel, on_delete=models.CASCADE, related_name='facelifts')
    facelift_year = models.PositiveIntegerField()
    changes_description = models.TextField(default='')

    def __str__(self):
        return f"{self.car_model.brand.name} {self.car_model.carModel} Facelift {self.facelift_year}"

class CarBodyType(models.Model):
    car_model = models.ForeignKey(CarModel, on_delete=models.CASCADE, related_name='body_types')
    
    BODY_STYLE_CHOICES = [
        ('SEDAN', 'Sedan'),
        ('WAGON', 'Wagon'),
        ('SUV', 'SUV'),
        ('HATCHBACK', 'Hatchback'),
        ('COMPACT', 'Compact Car'),
        ('COUPE', 'Coupe'),
        ('CONVERTIBLE', 'Convertible'),
        ('SPORTS', 'Sports Car'),
        ('SUPER', 'Supercar'),
        ('LUXURY', 'Luxury Car'),
        ('CONCEPT', 'Concept Car'),
        ('PICKUP', 'Pickup Truck'),
        ('VAN', 'Van/Minivan'),
    ]
    body_type = models.CharField(
        max_length=20,
        choices=BODY_STYLE_CHOICES
    )

    door_count = models.PositiveIntegerField(default=0)
    seat_count = models.PositiveIntegerField(default=0)
    
    offered_from_new = models.BooleanField(default=True)
    bodystyle_start_year = models.PositiveIntegerField(blank=True, null=True)
    bodystyle_end_year = models.PositiveIntegerField(blank=True, null=True)


    def save(self, *args, **kwargs):
        if self.door_count < 0:
            raise ValueError("Door count cannot be negative.")
        if self.seat_count < 0:
            raise ValueError("Seat count cannot be negative.")
        if self.offered_from_new:
            self.bodystyle_start_year = self.car_model.start_year
            self.bodystyle_end_year = self.car_model.end_year
        else:
            if not self.bodystyle_start_year:
                self.bodystyle_start_year = self.car_model.start_year
            if not self.bodystyle_end_year:
                self.bodystyle_end_year = self.car_model.end_year
        super().save(*args, **kwargs)


    def __str__(self):
        start = self.bodystyle_start_year
        end = self.bodystyle_end_year
        return f"{self.body_type} ({start}-{end}) - {self.seat_count} Seats"
    
class CarEngine(models.Model):
    car_model = models.ForeignKey(CarModel, on_delete=models.CASCADE, related_name='engines')
   
    
    ENGINE_TYPE_CHOICES = [
        ('PETROL', 'Internal Combustion Engine - Petrol'),
        ('DIESEL', 'Internal Combustion Engine - Diesel'),
        ('EV', 'Electric Vehicle'),
        ('HYBRID', 'Hybrid - Petrol/Electric'),
        ('DIESEL_HYBRID', 'Hybrid - Diesel/Electric'),
        ('HYDROGEN', 'Hydrogen Fuel Cell'),
    ]

    engine_type = models.CharField(
        max_length=20,
        choices=ENGINE_TYPE_CHOICES
    )

    displacement_cc = models.PositiveIntegerField()
    cylinders = models.PositiveIntegerField()
    horsepower = models.PositiveIntegerField()
    torque_lbft = models.PositiveIntegerField()
    turbocharged = models.BooleanField(default=False)
    supercharged = models.BooleanField(default=False)

    offered_from_new = models.BooleanField(default=True)
    offered_from_facelift = models.BooleanField(default=False)
    facelift = models.ForeignKey(Facelift, on_delete=models.CASCADE, related_name='facelifts', null=True, blank=True)
    engine_start_year = models.PositiveIntegerField(blank=True, null=True)
    engine_end_year = models.PositiveIntegerField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.displacement_cc <= 0:
            raise ValueError("Displacement must be a positive integer.")
        if self.cylinders <= 0:
            raise ValueError("Cylinders must be a positive integer.")
        if self.horsepower < 0:
            raise ValueError("Horsepower cannot be negative.")
        if self.torque_lbft < 0:
            raise ValueError("Torque cannot be negative.")
        
        if self.offered_from_new:
            self.engine_start_year = self.car_model.start_year

            if self.facelift:
                self.engine_end_year = self.facelift.facelift_year
 
            else:   
                first_facelift = self.car_model.facelifts.order_by('facelift_year').first()
            
                if first_facelift:
                    self.engine_end_year = first_facelift.facelift_year 
                else:
                    self.engine_end_year = self.car_model.end_year
            
        elif self.offered_from_facelift:
            if not self.facelift:
                raise ValueError("Facelift must be specified if offered_from_facelift is True.")
                
            self.engine_start_year = self.facelift.facelift_year
            self.engine_end_year = self.car_model.end_year
        
        if self.offered_from_new and self.offered_from_facelift:
            self.engine_start_year = self.car_model.start_year
            self.engine_end_year = self.car_model.end_year

        super().save(*args, **kwargs)

    def __str__(self):
        start = self.engine_start_year
        end = self.engine_end_year
        return f"{self.engine_type} - {self.displacement_cc}cc, {self.horsepower}hp, {self.torque_lbft}lb-ft  ({start}-{end})"
    
class CarModelTrim(models.Model):
    car_model = models.ForeignKey(CarModel, on_delete=models.CASCADE, related_name='trims')
    trim_name = models.CharField(max_length=100)
    trim_engine = models.ForeignKey(CarEngine, on_delete=models.CASCADE, related_name='trim_engines')
    trim_body_types = models.ManyToManyField(CarBodyType, related_name='trims')
    
    def __str__(self):
        return f"{self.car_model.brand.name} {self.car_model.carModel} {self.trim_name}"
    

## THESE ARE THE WHOLESALE PRODUCTS IN THEIR ENTIRETY
## WHOLESALE CODE IS BELOW THIS
