from django.urls import path
from .views.file_views import FileUploadView, FileUploadChunksView
from .views.data import GetAllData
from .views.query import XPathFilterBy, XPathGroupBy, XPathSearch, XPathOrderBy

urlpatterns = [
path('upload-file/', FileUploadView.as_view(), name='upload-file'),
path('upload-file/by-chunks', FileUploadChunksView.as_view(), name='upload-file-by-chunks'),
path('data/', GetAllData.as_view(), name='data'),
path('xml/filter-by', XPathFilterBy.as_view(), name='xml-filter-by'),
path('xml/group-by', XPathGroupBy.as_view(), name='xml-group-by'),
path('xml/search-by', XPathSearch.as_view(), name='xml-search-by'),
path('xml/order-by', XPathOrderBy.as_view(), name='xml-order-by'),
]
