from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from bins.views import (
    index, update_bin, get_bins_data,
    login_view, logout_view, bin_history
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('api/update-bin/', update_bin, name='update_bin'),
    path('api/get-bins/', get_bins_data, name='get_bins_data'),
    path('bin/<int:bin_id>/history/', bin_history, name='bin_history'),
]

# Static fayllar faqat DEBUG rejimda xizmat qilinadi
if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
