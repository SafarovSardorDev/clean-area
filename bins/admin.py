from django.contrib import admin
from .models import TrashBin

@admin.register(TrashBin)
class TrashBinAdmin(admin.ModelAdmin):
    # Ko‘rsatiladigan maydonlar
    list_display = ('sensor_id', 'mahalla', 'address', 'status', 'updated_at')
    
    # Qidirish maydonlari
    search_fields = ('sensor_id', 'mahalla', 'address')
    
    # Filtrlash imkoniyatlari
    list_filter = ('status', 'mahalla', 'updated_at')
    
    # Tartiblash
    ordering = ('-updated_at',)
    
    # Tahrirlash sahifasidagi maydonlar tartibi
    fields = ('sensor_id', 'mahalla', 'address', 'status')
    
    # Ro‘yxat sahifasida har bir sahifa uchun yozuvlar soni
    list_per_page = 20
    
    # Status uchun chiroyli ko‘rinish (masalan, rangli teglar)
    def get_status_display(self, obj):
        if obj.status == 'FILLED':
            return '<span style="color: red; font-weight: bold;">TO\'LDI</span>'
        return '<span style="color: green; font-weight: bold;">BO\'SH</span>'
    get_status_display.short_description = 'Holat'
    get_status_display.allow_tags = True

    # Admin panelida model nomi va sarlavhalarni o‘zbekchaga moslashtirish
    def __str__(self):
        return f"{self.sensor_id} - {self.mahalla}"

    class Meta:
        verbose_name = "Axlat Idishi"
        verbose_name_plural = "Axlat Idishlari"