from django.contrib import admin
from rallybench.models import RallyTask, RallyUser, RallyUserSession, Deployment

# Register your models here.
admin.site.register(RallyTask)
admin.site.register(RallyUser)
admin.site.register(RallyUserSession)
admin.site.register(Deployment)