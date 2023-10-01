from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Post(models.Model):
    COLOR_CHOICES = (
        ('red', 'Red'),
        ('green', 'Green'),
        ('blue', 'Blue'),
        ('yellow', 'Yellow'),
        ('pink', 'Pink'),
        ('purple', 'Purple'),
    )

    mentioned_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentioned_in_posts', blank=True, null=True)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    color_code = models.CharField(max_length=10, choices=COLOR_CHOICES, default='red')

class UserProfilePic(models.Model):
    BRANCH_CHOICES = [
        ('CSE', 'Computer Science and Engineering'),
        ('CSE_DS', 'Computer Science and Engineering (Data Science)'),
        ('CSE_CS', 'Computer Science and Engineering (Cyber Security)'),
        ('ISE', 'Information Science and Engineering'),
        ('EE', 'Electrical Engineering'),
        ('ME', 'Mechanical Engineering'),
        ('TE', 'Telecommunication Engineering'),
        ('IEM', 'Industrial Engineering and Management'),
        ('AIML', 'Artificial Intelligence and Machine Learning'),
        ('AE', 'Aerospace Engineering'),
        ('MCA', 'Masters of Computer Applications'),
        ('ECE', 'Electronics and Telecommunication Engineering'),
        ('EIE', 'Electrinics and Instrumentation Engineering'),
        ('EEE', 'Electrical and Electrinics Engineering'),
        ('CE', 'Chemical Engineering'),
        ('CV', 'Civil Engineering'),
        ('BT', 'Biotechnology')
    ]

    COLLEGE_CHOICES = [
        ('RVCE', 'R.V. College of Engineering'),
        ('RVU', 'R.V. University'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    branch = models.CharField(max_length=30, choices=BRANCH_CHOICES, default='', blank=True, null=True)
    college = models.CharField(max_length=30, choices=COLLEGE_CHOICES, default='', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_branch_display()}"


class Comments(models.Model):
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE)
    comment = models.CharField(max_length=500, null=True)
    user_commented = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    upvote = models.BooleanField(default=False)
    downvote = models.BooleanField(default=False)
    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(upvote=False) | models.Q(downvote=False),
                name='upvote-downvote exclusive',
                violation_error_message='You cannot simultaneously upvote and downvote this comment.',
            )
        ]


class Friendship(models.Model):
    friendship_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_friendships')
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_friendships')
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('unfriended', 'Unfriended'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.friend.username}: {self.status}"

class FriendRequest(models.Model):
    request_id = models.AutoField(primary_key=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_requests')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_requests')
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=('pending', 'Pending'))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} to {self.receiver.username}: {self.status}"



