"""cyberparlementInitiatives URL Configuration

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

from cyberparlementInitiatives.views import IndexView, InitiativeDetailView, InitiativeListView, InitiativePropositionView, UserCreateView, CyberparlementListView, UserLoginView, InitiativeValidationView, InitiativeStartPollView, InitiativePollVoteView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', IndexView.as_view(), name='index'),
    path('index/', IndexView.as_view(), name='index'),

    path('initiatives/<int:id_cyberparlement>', InitiativeListView.as_view(), name='initiative-list'),
    path('initiative/propose/', InitiativePropositionView.as_view(), name='initiative-propose'),
    path('initiative/validate/<int:id_initiative>', InitiativeValidationView.as_view(), name='initiative-validate'),
    path('initiative/start-poll/<int:id_initiative>', InitiativeStartPollView.as_view(), name='initiative-start-poll'),
    path('initiative/vote-poll/<int:pk>', InitiativePollVoteView.as_view(), name='initiative-vote-poll'),
    path('initiative/<int:id_cyberparlement>/<int:id_initiative>', InitiativeDetailView.as_view(), name='initiative-detail'),

    # Vues relatives à l'authentification -- à des fins de test
    path('user/create/', UserCreateView.as_view(), name='user-create'),
    path('login/', UserLoginView.as_view(), name='user-login'),

    # Vues relatives aux cyberparlements -- à des fins de test
    path('cyberparlements/', CyberparlementListView.as_view(), name='cyberparlement-list'),


]
