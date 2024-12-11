from django.urls import path
from .views.file_views import FileUploadView, FileUploadChunksView
from .views.data import GetAllData
from .views.query import XPathQueryView

urlpatterns = [
path('upload-file/', FileUploadView.as_view(), name='upload-file'),
path('upload-file/by-chunks', FileUploadChunksView.as_view(), name='upload-file-by-chunks'),
path('data/', GetAllData.as_view(), name='data'),
path('xml/filter-by', XPathQueryView.as_view(), name='xml-filter-by'),
]
