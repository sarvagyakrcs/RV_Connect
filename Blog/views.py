from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, generics, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from .models import Post, Comments, Friendship, FriendRequest
from .serializers import (
    PostSerializer,
    CommentsSerializer,
    FriendshipSerializer,
    FriendRequestSerializer,
    UserSerializer,
)
from .models import UserProfilePic
from .serializers import UserProfilePicSerializer
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.authentication import SessionAuthentication, BasicAuthentication




class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        email = request.data.get('email', '')

        if not email.endswith('@rvce.edu.in'):
            return Response({'detail': 'Email must end with @rvce.edu.in'}, status=status.HTTP_400_BAD_REQUEST)

        hashed_password = make_password(request.data['password'])
        request.data['password'] = hashed_password
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'detail': f'User registered successfully: {user}'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfilePicListCreateView(generics.ListCreateAPIView):
    queryset = UserProfilePic.objects.all()
    serializer_class = UserProfilePicSerializer
    permission_classes = [IsAuthenticated]

class UserProfilePicDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfilePic.objects.all()
    serializer_class = UserProfilePicSerializer
    permission_classes = [IsAuthenticated]

from rest_framework.views import APIView
class UserProfilePicByUsernameView(APIView):
    def get(self, request, username, format=None):
        user_profile = get_object_or_404(UserProfilePic, user__username=username)
        serializer = UserProfilePicSerializer(user_profile)
        return Response(serializer.data)

    def update(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        email = request.data.get('email', '')

        if not email.endswith('@rvce.edu.in'):
            return Response({'detail': 'Email must end with @rvce.edu.in'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    from django.shortcuts import get_object_or_404
    from django.http import Http404

    def retrieve(self, request, pk=None):
        try:
            # Try to retrieve by primary key (ID) first
            user = get_object_or_404(User, pk=pk)
        except (Http404, ValueError):
            # If not found or if pk is not a valid number, try to retrieve by username
            user = get_object_or_404(User, username=pk)

        serializer = UserSerializer(user)
        return Response(serializer.data)

    def retrieve_by_userid(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def retrieve_by_username(self, request, pk=None):
        user = get_object_or_404(User, username=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['GET'])
    def find_user(self, request):
        username = request.query_params.get('username', None)
        if username:
            users = User.objects.filter(username=username)
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['GET'])
    def user_details(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-date_posted')[:100]
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            mentioned_user_info = request.data.get('mentioned_user')
            mentioned_user = None

            if isinstance(mentioned_user_info, int):
                try:
                    mentioned_user = User.objects.get(pk=mentioned_user_info)
                except User.DoesNotExist:
                    mentioned_user = None
            elif isinstance(mentioned_user_info, str):
                try:
                    mentioned_user = User.objects.get(username=mentioned_user_info)
                except User.DoesNotExist:
                    mentioned_user = None

            serializer.validated_data['author'] = request.user
            serializer.validated_data['mentioned_user'] = mentioned_user
            post = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieveByID(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)
        serializer = PostSerializer(post)
        return Response(serializer.data)

    def update(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CommentsViewSet(viewsets.ModelViewSet):
    queryset = Comments.objects.all()
    serializer_class = CommentsSerializer

    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication required to create a comment.'},
                            status=status.HTTP_401_UNAUTHORIZED)

        request.data['user_commented'] = request.user.pk

        serializer = CommentsSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            comment = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        comments = Comments.objects.filter(user_commented__username=pk)
        serializer = CommentsSerializer(comments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def comments_on_post(self, request, post_id=None):
        comments = Comments.objects.filter(post_id=post_id)
        serializer = CommentsSerializer(comments, many=True)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        try:
            comment = Comments.objects.get(pk=pk)

            if comment.user_commented != request.user:
                return Response({'detail': 'You do not have permission to delete this comment.'},
                                status=status.HTTP_403_FORBIDDEN)

            comment_data = CommentsSerializer(comment).data
            comment.delete()

            if not Comments.objects.filter(pk=pk).exists():
                return Response({'detail': 'Comment deleted successfully', 'comment': comment_data},
                                status=status.HTTP_200_OK)
            else:
                print(f"Warning: Comment with ID {pk} still exists after deletion.")
            return Response(status=status.HTTP_204_NO_CONTENT)

        except Comments.DoesNotExist:
            return Response({'detail': 'The comment does not exist.'},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Exception during comment deletion: {e}")
            return Response({'detail': f'An error occurred during comment deletion. {str(e)}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FriendshipViewSet(viewsets.ModelViewSet):
    queryset = Friendship.objects.all()
    serializer_class = FriendshipSerializer

class FriendRequestViewSet(viewsets.ModelViewSet):
    serializer_class = FriendRequestSerializer
    queryset = FriendRequest.objects.all()
    def create(self, request, *args, **kwargs):
        sender = request.user.id
        data = request.data.copy()
        data['sender'] = sender
        serializer = FriendRequestSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'])
    def received_requests(self, request):
        try:
            # Get all friend requests received by the user
            received_requests = FriendRequest.objects.filter(receiver=request.user)

            # Serialize the friend requests
            serializer = FriendRequestSerializer(received_requests, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['GET'])
    def sent_requests(self, request):
        try:
            # Get all friend requests sent by the user
            sent_requests = FriendRequest.objects.filter(sender=request.user)

            # Serialize the friend requests
            serializer = FriendRequestSerializer(sent_requests, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['POST'])
    def accept_request(self, request, pk=None):
        try:
            friend_request = self.get_object()

            # Check if the friend request is pending
            if friend_request.status == 'pending' or 'Pending' or ('pending', 'Pending') or ["pending", "Pending"]:
                # Create a friendship object for the accepted request
                friendship = Friendship(user=friend_request.receiver, friend=friend_request.sender, status='accepted')
                friendship.save()

                # Delete the friend request from the database
                friend_request.delete()

                return Response({'detail': 'Friend request accepted and saved as friendship.'},
                                status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Friend request is not pending.'}, status=status.HTTP_400_BAD_REQUEST)
        except FriendRequest.DoesNotExist:
            return Response({'detail': 'Friend request not found.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['POST'])
    def reject_request(self, request, pk=None):
        try:
            friend_request = self.get_object()

            # Check if the friend request is pending
            if friend_request.status == 'pending' or 'Pending' or ('pending', 'Pending') or ["pending", "Pending"]:
                # Delete the friend request from the database
                friend_request.delete()

                return Response({'detail': 'Friend request rejected and removed.'}, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Friend request is not pending.'}, status=status.HTTP_400_BAD_REQUEST)
        except FriendRequest.DoesNotExist:
            return Response({'detail': 'Friend request not found.'}, status=status.HTTP_404_NOT_FOUND)

class FriendshipViewSet(viewsets.ModelViewSet):
    queryset = Friendship.objects.all()
    serializer_class = FriendshipSerializer



class FriendsByUsernameView(generics.ListAPIView):
    serializer_class = FriendshipSerializer

    def get_queryset(self):
        # Get the user by username
        username = self.kwargs['username']
        user = User.objects.get(username=username)

        # Get the user's friends
        return Friendship.objects.filter(user=user, status='accepted')

class UserSearchView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email']


class MentionedPostsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        username = self.kwargs['username']
        user = get_object_or_404(User, username=username)
        return Post.objects.filter(mentioned_user=user)

class PostByAuthorViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        username = self.kwargs['username']
        user = get_object_or_404(User, username=username)
        return Post.objects.filter(author=user)

class UserFriendsView(APIView):
    def get(self, request, user_id, *args, **kwargs):
        friends1 = Friendship.objects.filter(user__id=user_id, status='accepted')
        friends2 = Friendship.objects.filter(friend__id=user_id, status='accepted')

        all_friends = friends1 | friends2
        serializer = FriendshipSerializer(all_friends, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)




from drf_yasg.utils import swagger_auto_schema

@swagger_auto_schema(
    responses={
        200: "Success",
        400: "Bad Request",
        404: "Not Found",
    },
    operation_description="Description",
)
def your_view_name(self, request):
    pass
