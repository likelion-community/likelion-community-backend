from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(MainBoard)
admin.site.register(SchoolBoard)
admin.site.register(QuestionBoard)
admin.site.register(MainComment)
admin.site.register(SchoolComment)
admin.site.register(QuestionComment)