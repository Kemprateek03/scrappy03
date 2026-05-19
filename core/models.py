from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    birthday = models.DateField(blank=True, null=True)
    relationship_status = models.CharField(max_length=50, blank=True, choices=[
        ('single', 'Single'), ('in_relationship', 'In a Relationship'),
        ('married', 'Married'), ('complicated', "It's Complicated"),
    ])
    interests = models.TextField(blank=True, help_text="Comma-separated interests")
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return None

    def friends(self):
        accepted = Friendship.objects.filter(
            models.Q(sender=self.user) | models.Q(receiver=self.user),
            status='accepted'
        )
        friends = []
        for f in accepted:
            friends.append(f.receiver if f.sender == self.user else f.sender)
        return friends

    def friend_count(self):
        return len(self.friends())


class Friendship(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')]
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_requests')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('sender', 'receiver')

    def __str__(self):
        return f"{self.sender} -> {self.receiver} ({self.status})"


class Scrap(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scraps_written')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scraps_received')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Scrap from {self.author} to {self.recipient}"


class Testimonial(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='testimonials_written')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='testimonials_received')
    content = models.TextField()
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Testimonial from {self.author} to {self.recipient}"


class Community(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_communities')
    members = models.ManyToManyField(User, through='CommunityMembership', related_name='communities')
    avatar = models.ImageField(upload_to='communities/', blank=True, null=True)
    category = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'communities'

    def __str__(self):
        return self.name

    def member_count(self):
        return self.members.count()


class CommunityMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    is_moderator = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'community')


class CommunityPost(models.Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Album(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='albums')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.owner.username} - {self.name}"

    def cover_photo(self):
        return self.photos.first()


class Photo(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='photos/')
    caption = models.CharField(max_length=300, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo in {self.album.name}"
