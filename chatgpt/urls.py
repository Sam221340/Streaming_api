from django.urls import path
from .views import *

urlpatterns = [
    path('stream/', stream_completions, name='stream'),
    path('show_completions/', show_completions, name='show_completions'),
    path('end-session/', end_session, name = 'end-session')
]