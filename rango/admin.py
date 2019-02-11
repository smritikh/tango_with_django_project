from django.contrib import admin
from rango.models import Category, Page, PageAdmin
from rango.models import UserProfile

# Add in this class to customize the admin interface
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('name',)}

#update the registration to include this customized interface
admin.site.register(Category, CategoryAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(UserProfile)

