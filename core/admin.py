from django.contrib import admin
from .models import User, Brand, Industry, CarModel, Facelift, CarBodyType, CarEngine, CarModelTrim

class CarModelTrimInline(admin.TabularInline):
    model = CarModelTrim
    extra = 0
    filter_horizontal = ('trim_body_types',)
    def get_car_id_from_url(self, request):
        segments = request.path.strip('/').split('/')
        if 'change' in segments:
            try:
                change_index = segments.index('change')
                return int(segments[change_index - 1])
            except (ValueError, IndexError):
                return None
        return None
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        car_id = self.get_car_id_from_url(request)
        
        if db_field.name == 'trim_engine':
            if car_id:
                kwargs['queryset'] = CarEngine.objects.filter(car_model_id=car_id)
            else:
                kwargs['queryset'] = CarEngine.objects.none()
                
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


    def formfield_for_manytomany(self, db_field, request, **kwargs):
        car_id = self.get_car_id_from_url(request)

        if db_field.name == 'trim_body_types':
            if car_id:
                kwargs['queryset'] = CarBodyType.objects.filter(car_model_id=car_id)
            else:
                kwargs['queryset'] = CarBodyType.objects.none()
        
        return super().formfield_for_manytomany(db_field, request, **kwargs)


class CarEngineInline(admin.TabularInline):
    model = CarEngine
    extra = 0

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'facelift':
            facelift_id = request.resolver_match and request.resolver_match.kwargs.get('object_id')
            car_id = request.resolver_match.kwargs.get('object_id')

            kwargs['queryset'] = Facelift.objects.filter(car_model__id=car_id)
        else:
            kwargs['queryset'] = Facelift.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class CarBodyTypeInline(admin.TabularInline):
    model = CarBodyType
    extra = 0

class FaceliftInline(admin.TabularInline):
    model = Facelift
    extra = 0

class carInline(admin.TabularInline):
    model = CarModel
    extra = 0
    readonly_fields = ('is_discontinued',)

class CarModelAdmin(admin.ModelAdmin):
    inlines = [FaceliftInline, CarBodyTypeInline, CarEngineInline, CarModelTrimInline]
    list_display = ('brand', 'carModel', 'start_year', 'end_year', 'is_discontinued')

class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'country','is_defunct')
    filter_horizontal = ('industries',)

    # Asks for car models if brand makes cars
    def get_inlines(self, request, obj=None):
        if obj and obj.industries.filter(industry_Code='AUTO').exists():
            return [carInline]
        
        return []
admin.site.register(Facelift)
admin.site.register(CarBodyType)
admin.site.register(CarEngine)
admin.site.register(CarModelTrim)
admin.site.register(CarModel, CarModelAdmin)
admin.site.register(Brand, BrandAdmin)
admin.site.register(Industry)
admin.site.register(User)

from .models import Business
admin.site.register(Business)
