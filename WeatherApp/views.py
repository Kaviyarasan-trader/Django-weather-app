from django.shortcuts import render, redirect
from .form import CityForm
from .models import City
import requests
from django.contrib import messages

API_KEY = '4971f57e9ce5fd7744d802b65263610a'
URL = 'http://api.openweathermap.org/data/2.5/weather?q={}&appid={}&units=metric'

def home(request):
    if request.method == "POST":
        form = CityForm(request.POST)
        if form.is_valid():
            NCity = form.cleaned_data['name'].strip().title()
            if City.objects.filter(name__iexact=NCity).count() == 0:
                try:
                    res = requests.get(URL.format(NCity, API_KEY), timeout=5).json()
                    if res.get('cod') == 200:
                        city_obj = form.save(commit=False)
                        city_obj.name = NCity
                        city_obj.save()
                        messages.success(request, NCity + " Added Successfully...!!!")
                    else:
                        messages.error(request, "City Does Not Exist...!!!")
                except requests.exceptions.RequestException:
                    messages.error(request, "Network error. Please check your connection.")
            else:
                messages.error(request, "City Already Exists...!!!")

    form = CityForm()
    cities = City.objects.all()
    data = []

    for city in cities:
        try:
            res = requests.get(URL.format(city.name, API_KEY), timeout=5).json()
            if res.get('cod') != 200:
                continue
            city_weather = {
                'city': city.name,
                'temperature': res['main']['temp'],
                'description': res['weather'][0]['description'],
                'country': res['sys']['country'],
                'icon': res['weather'][0]['icon'],
            }
            data.append(city_weather)
        except requests.exceptions.RequestException:
            continue

    context = {'data': data, 'form': form}
    return render(request, "weatherapp.html", context)


def delete_city(request, CName):
    City.objects.filter(name__iexact=CName).delete()
    messages.success(request, CName + " Removed Successfully...!!!")
    return redirect('Home')
