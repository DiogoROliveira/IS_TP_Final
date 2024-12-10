from django.urls import path
from .views.file_views import FileUploadView, FileUploadChunksView
from .views.data import GetAllData

urlpatterns = [
path('upload-file/', FileUploadView.as_view(), name='upload-file'),
path('upload-file/by-chunks', FileUploadChunksView.as_view(), name='upload-file-by-chunks'),
path('data/', GetAllData.as_view(), name='data')
]
