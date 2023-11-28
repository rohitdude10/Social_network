# api/urls.py

from django.urls import path
from .views import UserSignup, UserLogin, UserSearchAPI, SendFriendRequestView, AcceptFriendRequestView, RejectFriendRequestView, ListFriendsView, ListPendingFriendRequestsView

urlpatterns = [
    path('signup/', UserSignup.as_view(), name='user_signup'),
    path('login/', UserLogin.as_view(), name='user_login'),
    path('search/', UserSearchAPI.as_view(), name='user-search'),
    path('send-friend-request/', SendFriendRequestView.as_view(),
         name='send-friend-request'),
    path('accept-friend-request/<int:pk>/',
         AcceptFriendRequestView.as_view(), name='accept-friend-request'),
    path('reject-friend-request/<int:pk>/',
         RejectFriendRequestView.as_view(), name='reject-friend-request'),
    path('list-friends/', ListFriendsView.as_view(), name='list-friends'),
    path('list-pending-friend-requests/', ListPendingFriendRequestsView.as_view(),
         name='list-pending-friend-requests'),


]
