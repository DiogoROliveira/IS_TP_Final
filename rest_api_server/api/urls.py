from django.urls import path
from .views.file_views import FileUploadView
from .views.data import GetAllData

urlpatterns = [
path('upload-file/', FileUploadView.as_view(), name='upload-file'),
path('data/', GetAllData.as_view(), name='data')
]
