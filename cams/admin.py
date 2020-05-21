from django.contrib import admin
from cams.models import Channel, Record


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    pass


@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    pass

