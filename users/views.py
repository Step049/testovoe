
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from .models import User
import requests



def load_initial_users():
    if User.objects.count() == 0:
        response = requests.get('https://randomuser.me/api/?results=1000')
        data = response.json()
        for user_data in data['results']:
            User.objects.create(
                gender=user_data['gender'],
                first_name=user_data['name']['first'],
                last_name=user_data['name']['last'],
                phone=user_data['phone'],
                email=user_data['email'],
                street=f"{user_data['location']['street']['number']} {user_data['location']['street']['name']}",
                city=user_data['location']['city'],
                state=user_data['location']['state'],
                postcode=user_data['location']['postcode'],
                picture_thumbnail=user_data['picture']['thumbnail'],
                picture_large=user_data['picture']['large']
            )


def user_list(request):
    # загружаем 1000 при запуске с которой работаем
    load_initial_users()

    if request.method == 'POST':
        count = min(int(request.POST.get('count', 15)), 1000)  # не больше 1000
        count=  max(1, count)
        return redirect(f'{request.path}?count={count}&page=1')

    # то что получили либо по дефолту
    requested_count = min(int(request.GET.get('count', 15)), 1000)
    requested_count = max(1, requested_count)

    # берем из бд нужное кол-вао
    users = User.objects.all()[:requested_count]

    # пусть будет 15 на стр для удобства
    paginator = Paginator(users, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'users/index.html', {
        'page_obj': page_obj,
        'requested_count': requested_count,
        'total_users': requested_count,
        'show_form': 'count' not in request.GET
    })


def user_detail(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    return render(request, 'users/user_detail.html', {'user': user})

def random_user(request):
    user = User.objects.order_by('?').first()
    return render(request, 'users/user_detail.html', {'user': user})