"""dm_django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path
from django.urls import include, path

from dm import views
from django.urls import path
urlpatterns = [
    # path('dm/', include('dm.urls')),
    # path('admin/', admin.site.urls),

    path('orm/', views.orm),

    path('dmStatus/', views.dmStatus),

    path('redPara/', views.redPara),

    path('bluePara/', views.bluePara),

    path('benchmarkPara/', views.benchmarkPara),

    path('hardwarePara/', views.hardwarePara),

    path('tmpC/', views.tmpC),

    path('trainingPara/', views.trainingPara),

    path('dmini/', views.dmini),

    # path('get_csrf_token/', views.get_csrf_token),

    path('modifyRedPara/', views.modifyRedPara),

    path('modifyBluePara/', views.modifyBluePara),

    path('modifyBenchmarkPara/', views.modifyBenchmarkPara),

    path('modifyHardwarePara/', views.modifyHardwarePara),

    path('runBenchMark/', views.runBenchMark),

    path('runCommend/', views.runCommand), # 总运行指令

    path('ChatRoom/', views.ChatRoom),

    path('isStopped/', views.isStopped),

    path('isPaused/', views.isPaused),

    path('isUpdate/', views.isUpdate),

    path('reSet_Stopped_And_Paused/', views.reSet_Stopped_And_Paused),

    path('isContinue/', views.isContinue),

    path('runSMAC/', views.runSMAC),

    path('TrainingData/', views.TrainingData),
]
