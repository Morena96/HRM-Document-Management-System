from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib import admin
from .models import *
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
# Register your models here.

admin.site.site_title = "Edara"
admin.site.site_header = "DOKUMENT DOLANYŞYGY"
admin.site.index_title = "Title"

class WelayatlarAdmin(admin.ModelAdmin):
    pass

admin.site.register(Welayatlar,WelayatlarAdmin)

class EdaralarAdmin(admin.ModelAdmin):
    list_display = ['ady','welaýaty']
    list_filter= ('welaýaty',)
    list_per_page=30
admin.site.register(Edaralar,EdaralarAdmin)

class BolumlerAdmin(admin.ModelAdmin):
    list_display = ['ady']

admin.site.register(Bolumler,BolumlerAdmin)

class FileAdmin(admin.ModelAdmin):
    list_display = ['ady','eýesi','welayaty','edarasy','bölümi','görnüşi','dokument'
    ,'döredilen_senesi','üýgedilen_senesi']
    fields = ('ady','görnüşi','dokument','mazmuny')
    date_hierarchy = 'döredilen_senesi'
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
#        if db_field.name == "welaýaty" and (not request.user.is_superuser):
#            print(request.user.welaýaty)
#            kwargs["initial"] = request.user.welaýaty
#            kwargs['disabled'] = True
        if db_field.name == "görnüşi":
            kwargs["queryset"] = Hasabat.objects.filter(bölümi=request.user.bölümi)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if(request.user.groups.filter(name='Ulanyjy').exists()):
            return qs.filter(eýesi=request.user)
        return qs.filter(eýesi__döreden=request.user)

    def save_model(self, request, obj, form, change):
        obj.eýesi = request.user
        obj.edarasy=request.user.edarasy
        obj.bölümi=request.user.bölümi
        super().save_model(request, obj, form, change)

    def welayaty(self,obj):
        if obj.edarasy:
            return obj.edarasy.welaýaty
            
    def has_delete_permission(self, request, obj=None):
        if(request.user.groups.filter(name='Ulanyjy').exists()):
            return True
        return False

    def has_add_permission(self,request):
        if(request.user.groups.filter(name='Ulanyjy').exists()):
            return True
        return False
    def has_change_permission(self,request, obj=None):
        if(request.user.groups.filter(name='Ulanyjy').exists()):
            return True
        return False


#    empty_value_display = '-empty-'
admin.site.register(File,FileAdmin)

class HasabatAdmin(admin.ModelAdmin):
    list_display = ['ady','bölümi']

admin.site.register(Hasabat,HasabatAdmin)

@receiver(post_save, sender=Ulanyjy)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.döreden.is_superuser:
            instance.groups.add(Group.objects.get(name='Admin'))
        else:
            print('bb')
            instance.groups.add(Group.objects.get(name='Ulanyjy'))

class UlanyjyAdmin(UserAdmin):
    list_display = ['username','ady','edarasy','welayaty','bölümi','döreden','mac_adresi']#
    fieldsets = (
    (None, {
        'fields': ( 'username','ady','edarasy','bölümi','password','mac_adresi')
    }),
    ('Goşmaça Maglumatlar', {
        'classes': ('collapse',),
        'fields': ('first_name', 'last_name'),
    }),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
#        if db_field.name == "welaýaty" and (not request.user.is_superuser):
#            print(request.user.welaýaty)
#            kwargs["initial"] = request.user.welaýaty
#            kwargs['disabled'] = True
        if db_field.name == "edarasy" and (not request.user.is_superuser):
            kwargs['disabled'] = True
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(döreden=request.user)

    def save_model(self, request, obj, form, change):
        if not obj.döreden:
            obj.döreden = request.user
        obj.is_staff=True
        if not obj.edarasy and (not request.user.is_superuser):
            obj.edarasy=request.user.edarasy
        super().save_model(request, obj, form, change)
    def welayaty(self,obj):
        if obj.edarasy:
            return obj.edarasy.welaýaty

admin.site.register(Ulanyjy,UlanyjyAdmin)