from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home, name='home'),
    path('search/', views.search_users, name='search'),

    # Profile
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('profile/<str:username>/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/friends/', views.friends_list, name='friends_list'),

    # Friends
    path('friend/request/<str:username>/', views.send_friend_request, name='send_friend_request'),
    path('friend/respond/<int:request_id>/<str:action>/', views.respond_friend_request, name='respond_friend_request'),

    # Scraps
    path('scrap/<str:username>/', views.post_scrap, name='post_scrap'),
    path('scrap/delete/<int:scrap_id>/', views.delete_scrap, name='delete_scrap'),

    # Testimonials
    path('testimonial/<str:username>/', views.post_testimonial, name='post_testimonial'),
    path('testimonial/approve/<int:testimonial_id>/', views.approve_testimonial, name='approve_testimonial'),

    # Communities
    path('communities/', views.community_list, name='community_list'),
    path('communities/new/', views.create_community, name='create_community'),
    path('communities/<int:pk>/', views.community_detail, name='community_detail'),
    path('communities/<int:pk>/join/', views.join_community, name='join_community'),
    path('communities/<int:pk>/leave/', views.leave_community, name='leave_community'),
    path('communities/<int:pk>/post/', views.post_to_community, name='post_to_community'),

    # Albums
    path('albums/<str:username>/', views.album_list, name='album_list'),
    path('albums/view/<int:pk>/', views.album_detail, name='album_detail'),
    path('albums/new/', views.create_album, name='create_album'),
    path('albums/<int:album_pk>/upload/', views.upload_photo, name='upload_photo'),
]
