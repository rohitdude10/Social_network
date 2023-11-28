# api/views.py

from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import CustomUser, FriendRequest
from .serializers import CustomUserSerializer, FriendRequestSerializer
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from rest_framework import status
from django.contrib.auth import get_user_model, authenticate
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404


class UserSignup(generics.CreateAPIView):
    # Set the queryset to retrieve all user objects
    queryset = get_user_model().objects.all()
    # Use the CustomUserSerializer for serialization
    serializer_class = CustomUserSerializer
    # Allow any user, authenticated or not, to access this view
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        # Extract and normalize the email from the request data
        email = request.data.get('email', '').lower()
        request.data['email'] = email

        # Create an instance of the serializer with the request data
        serializer = self.get_serializer(data=request.data)
        # Validate the serializer data, raising an exception if invalid
        serializer.is_valid(raise_exception=True)
        # Save the user object from the serializer
        user = serializer.save()

        # Create and return an authentication token for the new user
        token = Token.objects.create(user=user)

        # Return a response with the authentication token and user details
        return Response({
            'token': token.key,
            'user_id': user.id,
            'email': user.email,
            'name': user.name
        }, status=status.HTTP_201_CREATED)


class UserLogin(generics.CreateAPIView):
    # Use the CustomUserSerializer for serialization
    serializer_class = CustomUserSerializer
    # Allow any user, authenticated or not, to access this view
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        # Extract and normalize the email and password from the request data
        email = request.data.get('email', '').lower()
        password = request.data.get('password', '')

        # Authenticate the user using the provided email and password
        user = authenticate(request, email=email, password=password)

        if user:
            # If authentication is successful, generate or retrieve the authentication token
            token, created = Token.objects.get_or_create(user=user)

            # Return a response with the authentication token and user details
            return Response({
                'token': token.key,
                'user_id': user.id,
                'email': user.email,
                'name': user.name
            }, status=status.HTTP_200_OK)
        else:
            # If authentication fails, return a response indicating invalid credentials
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class UserSearchAPI(generics.ListAPIView):
    # Use the CustomUserSerializer for serialization
    serializer_class = CustomUserSerializer
    # Allow only authenticated users to access this view
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        # Get the search keyword from the query parameters
        search_keyword = self.request.query_params.get('search_value', '')

        try:
            # Check if the search keyword looks like an email address
            if '@' in search_keyword:
                return CustomUser.objects.filter(email__iexact=search_keyword)
            else:
                return CustomUser.objects.filter(name__icontains=search_keyword)
        except Exception as e:
            # Handle exceptions, log the error, and return an empty queryset
            # Adjust the exception type based on the specific exceptions you want to catch
            # Log the error using your preferred logging mechanism
            print(f"An error occurred: {str(e)}")
            return CustomUser.objects.none()

    def list(self, request, *args, **kwargs):
        # Get the queryset based on the search keyword
        queryset = self.get_queryset()

        # Paginate the queryset if needed
        page = self.paginate_queryset(queryset)

        if page is not None:
            # Serialize and return the paginated data
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # Serialize and return the entire queryset data
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class SendFriendRequestView(generics.CreateAPIView):
    # Use the FriendRequestSerializer for serialization
    serializer_class = FriendRequestSerializer
    # Allow only authenticated users to access this view
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        # Extract receiver ID from the request data
        receiver_id = request.data.get('receiver')

        # Get the receiver user object or return 404 if not found
        receiver = get_object_or_404(CustomUser, id=receiver_id)
        sender = request.user
        # Check if the sender and receiver are different users
        if receiver_id == sender.id:
            return Response({'detail': 'sender and receiver must be the different user'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the sender can send a friend request
        if not FriendRequest.can_send_request(sender, receiver):
            return Response({'detail': 'You cannot send more than 3 friend requests within a minute'}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # Check if a friend request already exists
        existing_request = FriendRequest.objects.filter(
            sender=sender, receiver=receiver).first()
        if existing_request:
            return Response({'detail': 'Friend request already sent'}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new friend request with "Pending" status
        friend_request = FriendRequest.objects.create(
            sender=sender, receiver=receiver, status="Pending")
        serializer = self.get_serializer(friend_request)

        # Return the serialized friend request data
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AcceptFriendRequestView(generics.UpdateAPIView):
    # Set the queryset to include all FriendRequest objects
    queryset = FriendRequest.objects.all()
    # Use the FriendRequestSerializer for serialization
    serializer_class = FriendRequestSerializer
    # Allow only authenticated users to access this view
    permission_classes = (permissions.IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        # Get the FriendRequest object to be updated
        friend_request = self.get_object()

        # Check if the current user is the receiver of the friend request
        if friend_request.receiver != request.user:
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        # Set the status of the friend request to 'accepted' and save the changes
        friend_request.status = 'accepted'
        friend_request.save()

        # Return a response indicating that the friend request was accepted
        return Response({'detail': 'Friend request accepted'}, status=status.HTTP_200_OK)

class RejectFriendRequestView(generics.UpdateAPIView):
    # Set the queryset to include all FriendRequest objects
    queryset = FriendRequest.objects.all()
    # Use the FriendRequestSerializer for serialization
    serializer_class = FriendRequestSerializer
    # Allow only authenticated users to access this view
    permission_classes = (permissions.IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        # Get the FriendRequest object to be updated
        friend_request = self.get_object()

        # Check if the current user is the receiver of the friend request
        if friend_request.receiver != request.user:
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        # Set the status of the friend request to 'rejected' and save the changes
        friend_request.status = 'rejected'
        friend_request.save()

        # Return a response indicating that the friend request was rejected
        return Response({'detail': 'Friend request rejected'}, status=status.HTTP_200_OK)
    
class ListFriendsView(generics.ListAPIView):
    # Use the CustomUserSerializer for serialization
    serializer_class = CustomUserSerializer
    # Allow only authenticated users to access this view
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        # Get the current user
        user = self.request.user

        # Find friends by looking for accepted friend requests
        friends_requests = FriendRequest.objects.filter(
            sender=user, status='accepted') | FriendRequest.objects.filter(receiver=user, status='accepted')

        # Get the corresponding users from the friend requests
        friends = [friend_request.sender if friend_request.receiver == user else friend_request.receiver for friend_request in friends_requests]

        return friends

    def list(self, request, *args, **kwargs):
        # Get the queryset of friends
        queryset = self.get_queryset()

        # Serialize the queryset and return the response
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ListPendingFriendRequestsView(generics.ListAPIView):
    # Use the FriendRequestSerializer for serialization
    serializer_class = FriendRequestSerializer
    # Allow only authenticated users to access this view
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        # Get the current user
        user = self.request.user

        # Find pending friend requests where the authenticated user is the receiver
        pending_requests = FriendRequest.objects.filter(
            receiver=user, status='Pending')

        return pending_requests

    def list(self, request, *args, **kwargs):
        # Get the queryset of pending friend requests
        queryset = self.get_queryset()

        # Serialize the queryset and return the response
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
