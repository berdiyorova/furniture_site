from django.urls import path

from common.views import home_page_view

app_name = 'common'

urlpatterns = [
    path('', home_page_view, name='home')
]