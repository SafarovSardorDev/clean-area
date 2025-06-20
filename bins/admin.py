from django.contrib import admin
from .models import Dispatcher, TrashBin, BinStatusHistory
from django.utils.html import format_html



@admin.register(Dispatcher)
class DispatcherAdmin(admin.ModelAdmin):
    list_display = ('user', 'api_token')
    search_fields = ('user__username',)
    readonly_fields = ('api_token',)
    ordering = ('user__username',)


@admin.register(TrashBin)
class TrashBinAdmin(admin.ModelAdmin):
    list_display = ('sensor_id', 'mahalla', 'address', 'colored_status', 'updated_at')
    search_fields = ('sensor_id', 'mahalla', 'address')
    list_filter = ('status', 'mahalla', 'updated_at')
    ordering = ('-updated_at',)
    fields = ('dispatcher', 'sensor_id', 'mahalla', 'address', 'status')
    list_per_page = 20

    def colored_status(self, obj):
        color = 'red' if obj.status == 'FILLED' else 'green'
        label = 'TO‘LDI' if obj.status == 'FILLED' else "BO‘SH"
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, label)
    colored_status.short_description = 'Holat'


@admin.register(BinStatusHistory)
class BinStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('trash_bin', 'status', 'timestamp')
    list_filter = ('status', 'timestamp')
    search_fields = ('trash_bin__sensor_id',)
    ordering = ('-timestamp',)
