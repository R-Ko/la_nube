from django.contrib import admin
from core.models.PageVisit import PageVisit
from core.models.Family import Family
from core.models.Child import Child
from core.models.Professor import Professor
from core.models.Activity import Activity
from core.models.User import UserApp
from core.models.Parent import Parent
from django.contrib.auth.admin import UserAdmin

# Register your models here.
admin.site.register(PageVisit)
admin.site.register(Family)
admin.site.register(Child)
admin.site.register(Professor)
admin.site.register(Activity)
admin.site.register(Parent)

@admin.register(UserApp)
class UserAppAdmin(UserAdmin):
    def save_model(self, request, obj, form, change):
        if not change:
            obj.must_change_password = True
        elif 'password' in form.changed_data:
            obj.must_change_password = True
        super().save_model(request, obj, form, change)