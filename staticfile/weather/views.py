from django.shortcuts import render
from django.contrib import messages
import requests
import datetime


def weatherpage(request):
   
    if 'city' in request.POST:
         city = request.POST['city']
    else:
         city = 'indore'     
    
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid= 963804a07802e5371e2a2bd19f6a7afb'
    PARAMS = {'units':'metric'}

    API_KEY =  ' AIzaSyAPFSLqV5bk9dJ3etShxeSSiQ_Rc2zk8OI  '

    SEARCH_ENGINE_ID = '130921f9bf8ac4610'
     
    query = city + " 1920x1080"
    page = 1
    start = (page - 1) * 10 + 1
    searchType = 'image'
    city_url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={SEARCH_ENGINE_ID}&q={query}&start={start}&searchType={searchType}&imgSize=xlarge"

    # Safe image fetch
    try:
        data = requests.get(city_url).json()
        search_items = data.get("items")
        if search_items and len(search_items) > 1:
            image_url = search_items[1]['link']
        else:
            image_url = "/static/media/Untitled.png"
    except:
        image_url = "/static/media/Untitled.png"
    

    try:
          
          data = requests.get(url,params=PARAMS).json()
          description = data['weather'][0]['description']
          icon = data['weather'][0]['icon']
          temp = data['main']['temp']
          day = datetime.date.today()

          return render(request,'weatherapp/index.html' , {'description':description , 'icon':icon ,'temp':temp , 'day':day , 'city':city , 'exception_occurred':False ,'image_url':image_url})
    
    except KeyError:
          exception_occurred = True
          messages.error(request,'Entered data is not available to API')   
          # city = 'indore'
          # data = requests.get(url,params=PARAMS).json()
          
          # description = data['weather'][0]['description']
          # icon = data['weather'][0]['icon']
          # temp = data['main']['temp']
          day = datetime.date.today()

          return render(request,'weather.html' ,{'description':'clear sky', 'icon':'01d'  ,'temp':25 , 'day':day , 'city':'indore' , 'exception_occurred':exception_occurred } )
               
    
    