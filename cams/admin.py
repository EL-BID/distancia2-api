from django.contrib import admin
from cams.models import Channel, Record, RemoteCredential


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    exclude = ('state', 'last_connection')
    list_display = ('name', 'enabled', 'process_id', 'camera_interface', 'url')


@admin.register(RemoteCredential)
class RemoteCredentialAdmin(admin.ModelAdmin):
    list_display = ('host', 'port', 'username')


@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
