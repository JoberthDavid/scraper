"""
URL configuration for scraper project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin

from django.urls import include, path
from rest_framework import routers
from core.api.viewsets import SourceFileViewSet, GenericItemViewSet, CompositionItemViewSet, EquipmentItemViewSet, WorkmanItemViewSet, MaterialItemViewSet, UnitViewSet, MonetaryValueViewSet, CompositionViewSet


router = routers.DefaultRouter()
router.register(r'arquivos-base', SourceFileViewSet, basename='SourceFile')
router.register(r'itens', GenericItemViewSet, basename='GenericItem')
router.register(r'itens-composicoes', CompositionItemViewSet, basename='CompositionItem')
router.register(r'itens-equipamentos', EquipmentItemViewSet, basename='EquipmentItem')
router.register(r'itens-mao-de-obra', WorkmanItemViewSet, basename='WorkmanItem')
router.register(r'itens-materiais', MaterialItemViewSet, basename='MaterialItem')
router.register(r'unidades', UnitViewSet, basename='Unit')
router.register(r'valores-monetarios', MonetaryValueViewSet, basename='MonetaryValue')
router.register(r'composicoes', CompositionViewSet, basename='Composition')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
]
