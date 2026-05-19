from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from .models import Profile, Friendship, Scrap, Testimonial, Community, CommunityMembership, CommunityPost, Album, Photo
from .forms import RegisterForm, ProfileForm, ScrapForm, TestimonialForm, CommunityForm, CommunityPostForm, AlbumForm, PhotoForm
from django.http import HttpResponseForbidden


def landing(request):
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'core/landing.html')


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)
            login(request, user)
            return redirect('edit_profile', username=user.username)
    else:
        form = RegisterForm()
    return render(request, 'core/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('landing')


@login_required
def home(request):
    user = request.user
    friends = user.profile.friends()
    pending_requests = Friendship.objects.filter(receiver=user, status='pending')
    recent_scraps = Scrap.objects.filter(recipient=user).order_by('-created_at')[:5]
    communities = user.communities.all()[:4]
    return render(request, 'core/home.html', {
        'friends': friends[:6],
        'pending_requests': pending_requests,
        'recent_scraps': recent_scraps,
        'communities': communities,
    })


@login_required
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=profile_user)
    scraps = Scrap.objects.filter(recipient=profile_user)
    testimonials = Testimonial.objects.filter(recipient=profile_user, approved=True)
    albums = Album.objects.filter(owner=profile_user)
    scrap_form = ScrapForm()
    testimonial_form = TestimonialForm()

    friendship_status = None
    if request.user != profile_user:
        try:
            fs = Friendship.objects.get(
                Q(sender=request.user, receiver=profile_user) |
                Q(sender=profile_user, receiver=request.user)
            )
            friendship_status = fs.status
            if fs.sender == profile_user and fs.status == 'pending':
                friendship_status = 'received'
        except Friendship.DoesNotExist:
            friendship_status = 'none'

    return render(request, 'core/profile.html', {
        'profile_user': profile_user,
        'profile': profile,
        'scraps': scraps,
        'testimonials': testimonials,
        'albums': albums,
        'scrap_form': scrap_form,
        'testimonial_form': testimonial_form,
        'friendship_status': friendship_status,
        'friends': profile.friends(),
    })


@login_required
def edit_profile(request, username=None):
    profile = get_object_or_404(Profile, user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated!')
            return redirect('profile', username=request.user.username)
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'core/edit_profile.html', {'form': form})


@login_required
def send_friend_request(request, username):
    receiver = get_object_or_404(User, username=username)
    if receiver != request.user:
        Friendship.objects.get_or_create(sender=request.user, receiver=receiver)
    return redirect('profile', username=username)


@login_required
def respond_friend_request(request, request_id, action):
    fs = get_object_or_404(Friendship, id=request_id, receiver=request.user)
    if action == 'accept':
        fs.status = 'accepted'
        fs.save()
    elif action == 'reject':
        fs.status = 'rejected'
        fs.save()
    return redirect('home')


@login_required
def post_scrap(request, username):
    recipient = get_object_or_404(User, username=username)
    if request.method == 'POST':
        form = ScrapForm(request.POST)
        if form.is_valid():
            scrap = form.save(commit=False)
            scrap.author = request.user
            scrap.recipient = recipient
            scrap.save()
    return redirect('profile', username=username)


@login_required
def delete_scrap(request, scrap_id):
    scrap = get_object_or_404(Scrap, id=scrap_id)
    if request.user == scrap.recipient or request.user == scrap.author:
        username = scrap.recipient.username
        scrap.delete()
        return redirect('profile', username=username)
    return HttpResponseForbidden()


@login_required
def post_testimonial(request, username):
    recipient = get_object_or_404(User, username=username)
    if request.method == 'POST':
        form = TestimonialForm(request.POST)
        if form.is_valid():
            t = form.save(commit=False)
            t.author = request.user
            t.recipient = recipient
            t.save()
            messages.success(request, 'Testimonial submitted! It will appear after approval.')
    return redirect('profile', username=username)


@login_required
def approve_testimonial(request, testimonial_id):
    t = get_object_or_404(Testimonial, id=testimonial_id, recipient=request.user)
    t.approved = True
    t.save()
    return redirect('profile', username=request.user.username)


@login_required
def community_list(request):
    communities = Community.objects.all().order_by('-created_at')
    my_communities = request.user.communities.all()
    return render(request, 'core/community_list.html', {
        'communities': communities,
        'my_communities': my_communities,
    })


@login_required
def community_detail(request, pk):
    community = get_object_or_404(Community, pk=pk)
    is_member = CommunityMembership.objects.filter(user=request.user, community=community).exists()
    posts = community.posts.all()
    post_form = CommunityPostForm()
    return render(request, 'core/community_detail.html', {
        'community': community,
        'is_member': is_member,
        'posts': posts,
        'post_form': post_form,
    })


@login_required
def create_community(request):
    if request.method == 'POST':
        form = CommunityForm(request.POST, request.FILES)
        if form.is_valid():
            community = form.save(commit=False)
            community.creator = request.user
            community.save()
            CommunityMembership.objects.create(user=request.user, community=community, is_moderator=True)
            return redirect('community_detail', pk=community.pk)
    else:
        form = CommunityForm()
    return render(request, 'core/create_community.html', {'form': form})


@login_required
def join_community(request, pk):
    community = get_object_or_404(Community, pk=pk)
    CommunityMembership.objects.get_or_create(user=request.user, community=community)
    return redirect('community_detail', pk=pk)


@login_required
def leave_community(request, pk):
    community = get_object_or_404(Community, pk=pk)
    CommunityMembership.objects.filter(user=request.user, community=community).delete()
    return redirect('community_detail', pk=pk)


@login_required
def post_to_community(request, pk):
    community = get_object_or_404(Community, pk=pk)
    if request.method == 'POST':
        form = CommunityPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.community = community
            post.save()
    return redirect('community_detail', pk=pk)


@login_required
def album_list(request, username):
    profile_user = get_object_or_404(User, username=username)
    albums = Album.objects.filter(owner=profile_user)
    return render(request, 'core/album_list.html', {'profile_user': profile_user, 'albums': albums})


@login_required
def album_detail(request, pk):
    album = get_object_or_404(Album, pk=pk)
    photos = album.photos.all()
    photo_form = PhotoForm()
    return render(request, 'core/album_detail.html', {
        'album': album,
        'photos': photos,
        'photo_form': photo_form,
    })


@login_required
def create_album(request):
    if request.method == 'POST':
        form = AlbumForm(request.POST)
        if form.is_valid():
            album = form.save(commit=False)
            album.owner = request.user
            album.save()
            return redirect('album_detail', pk=album.pk)
    else:
        form = AlbumForm()
    return render(request, 'core/create_album.html', {'form': form})


@login_required
def upload_photo(request, album_pk):
    album = get_object_or_404(Album, pk=album_pk, owner=request.user)
    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.album = album
            photo.save()
    return redirect('album_detail', pk=album_pk)


@login_required
def search_users(request):
    query = request.GET.get('q', '')
    results = []
    if query:
        results = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ).exclude(id=request.user.id)
    return render(request, 'core/search.html', {'results': results, 'query': query})


@login_required
def friends_list(request, username):
    profile_user = get_object_or_404(User, username=username)
    friends = profile_user.profile.friends()
    return render(request, 'core/friends_list.html', {'profile_user': profile_user, 'friends': friends})
