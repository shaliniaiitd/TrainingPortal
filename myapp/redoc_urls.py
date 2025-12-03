from django.urls import path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="TrainingPortal API",
        default_version="v1",
    ),
    public=True,
)

urlpatterns = [
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='redoc-ui'),
]