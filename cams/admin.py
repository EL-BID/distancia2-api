from django.contrib import admin
from cams.models import Channel, Record, RemoteCredential


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    pass


@admin.register(RemoteCredential)
class RemoteCredentialAdmin(admin.ModelAdmin):
    pass


@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    pass
