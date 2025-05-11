from django.contrib import admin
from django.urls import path
from bins.views import index, update_bin, get_bins_data, login_view, logout_view
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('api/update-bin/', update_bin, name='update_bin'),
    path('get-bins-data/', get_bins_data, name='get_bins_data'),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])