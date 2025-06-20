from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import Dispatcher, TrashBin, BinStatusHistory
import logging
from django import forms
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Dispatcher, TrashBin, BinStatusHistory

logger = logging.getLogger(__name__)

class UpdateBinForm(forms.Form):
    token = forms.CharField(max_length=64)
    sensor_id = forms.CharField(max_length=50)
    status = forms.ChoiceField(choices=[('FILLED', 'FILLED'), ('EMPTY', 'EMPTY')])
    address = forms.CharField(max_length=200)
    mahalla = forms.CharField(max_length=100, required=False)

@csrf_exempt
def update_bin(request):
    if request.method != 'POST':
        logger.error("Invalid request method: %s", request.method)
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

    form = UpdateBinForm(request.POST)
    if not form.is_valid():
        logger.error("Invalid form data: %s", form.errors)
        return JsonResponse({'status': 'error', 'message': 'Invalid data'}, status=400)

    data = form.cleaned_data
    try:
        dispatcher = Dispatcher.objects.get(api_token=data['token'])
    except Dispatcher.DoesNotExist:
        logger.error("Invalid token: %s", data['token'])
        return JsonResponse({'status': 'error', 'message': 'Invalid token'}, status=403)

    bin_obj, created = TrashBin.objects.update_or_create(
        sensor_id=data['sensor_id'],
        dispatcher=dispatcher,
        defaults={
            'status': data['status'],
            'address': data['address'],
            'mahalla': data['mahalla'] or 'Yunusobod'
        }
    )

    BinStatusHistory.objects.create(trash_bin=bin_obj, status=data['status'])
    logger.info("Bin updated: sensor_id=%s, status=%s", data['sensor_id'], data['status'])

    return JsonResponse({
        'status': 'success',
        'sensor_id': data['sensor_id'],
        'new_status': data['status']
    })

@login_required
def index(request):
    try:
        dispatcher = Dispatcher.objects.get(user=request.user)
    except Dispatcher.DoesNotExist:
        messages.error(request, "Sizda Dispatcher profili mavjud emas.")
        return redirect('logout')

    bins = dispatcher.bins.all()
    total_bins = bins.count()
    filled_bins = bins.filter(status='FILLED').count()

    return render(request, 'index.html', {
        'bins': bins,
        'total_bins': total_bins,
        'filled_bins': filled_bins
    })


@login_required
def get_bins_data(request):
    try:
        dispatcher = Dispatcher.objects.get(user=request.user)
    except Dispatcher.DoesNotExist:
        return JsonResponse({'error': 'Dispatcher profili topilmadi'}, status=403)

    bins = dispatcher.bins.all()
    bins_data = [{
        'id': bin.id,  # id mavjudligini tekshiring
        'sensor_id': bin.sensor_id or 'N/A',
        'mahalla': bin.mahalla or 'N/A',
        'address': bin.address or 'N/A',
        'status': bin.status or 'UNKNOWN'
    } for bin in bins]

    return JsonResponse({
        'bins': bins_data,
        'total_bins': bins.count(),
        'filled_bins': bins.filter(status='FILLED').count()
    })

@login_required
def bin_history(request, bin_id):
    dispatcher = get_object_or_404(Dispatcher, user=request.user)
    trash_bin = get_object_or_404(TrashBin, id=bin_id, dispatcher=dispatcher)
    history = BinStatusHistory.objects.filter(trash_bin=trash_bin).order_by('-timestamp')

    return render(request, 'bin_history.html', {
        'bin': trash_bin,
        'history': history
    })


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('index'))
        else:
            messages.error(request, "Foydalanuvchi nomi yoki parol noto‘g‘ri.")
    return render(request, 'login.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')
