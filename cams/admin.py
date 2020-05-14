from django.contrib import admin

# Register your models here.

from cams.models import Channel


class ChannelAdmin(admin.ModelAdmin):
    pass

admin.site.register(Channel, ChannelAdmin)
