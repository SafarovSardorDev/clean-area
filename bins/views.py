from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import TrashBin

@csrf_exempt
def update_bin(request):
    if request.method == 'POST':
        data = request.POST
        sensor_id = data.get('sensor_id')
        status = data.get('status')
        address = data.get('address')
        mahalla = data.get('mahalla', 'Yunusobod')

        # Ma'lumot tekshiruvi
        if not sensor_id or status not in ['FILLED', 'EMPTY'] or not address:
            return JsonResponse({'status': 'error', 'message': 'Invalid data'}, status=400)

        try:
            bin_obj, created = TrashBin.objects.update_or_create(
                sensor_id=sensor_id,
                defaults={'status': status, 'address': address, 'mahalla': mahalla}
            )
            return JsonResponse({'status': 'success', 'sensor_id': sensor_id, 'status': status})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required
def get_bins_data(request):
    bins = TrashBin.objects.all()
    bins_data = [{
        'id': bin.id,
        'sensor_id': bin.sensor_id,
        'mahalla': bin.mahalla,
        'address': bin.address,
        'status': bin.status
    } for bin in bins]
    return JsonResponse({
        'bins': bins_data,
        'total_bins': bins.count(),
        'filled_bins': bins.filter(status='FILLED').count()
    })

@login_required
def index(request):
    bins = TrashBin.objects.all()
    total_bins = bins.count()
    filled_bins = bins.filter(status='FILLED').count()
    return render(request, 'index.html', {
        'bins': bins,
        'total_bins': total_bins,
        'filled_bins': filled_bins
    })

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, "Foydalanuvchi nomi yoki parol noto‘g‘ri.")
    return render(request, 'login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')