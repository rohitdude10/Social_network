from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from .models import FriendRequest


class APITestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects._create_user(
            email='test@example.com',
            name='Test User',
            password='testpassword'
        )
        self.friend_user = get_user_model().objects._create_user(
            email='friend@example.com',
            name='Friend User',
            password='friendpassword'
        )
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_user_signup(self):
        url = reverse('user_signup')
        data = {'email': 'newuser@example.com',
                'name': 'New User', 'password': 'newpassword'}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('token' in response.data)
        self.assertTrue('user_id' in response.data)
        self.assertEqual(response.data['email'], 'newuser@example.com')
        self.assertEqual(response.data['name'], 'New User')

    def test_user_login(self):
        url = reverse('user_login')
        data = {'email': self.user.email, 'password': 'testpassword'}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in response.data)
        self.assertTrue('user_id' in response.data)
        self.assertEqual(response.data['email'], self.user.email)
        self.assertEqual(response.data['name'], self.user.name)

    # Add tests for other APIs following a similar structure
    def test_send_friend_request(self):
        url = reverse('send-friend-request')
        data = {'receiver': self.friend_user.id}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('status' in response.data)
        self.assertEqual(response.data['status'], 'Pending')

    def test_accept_friend_request(self):
        friend_request = FriendRequest.objects.create(
            sender=self.friend_user, receiver=self.user, status='Pending')
        url = reverse('accept-friend-request', args=[friend_request.id])
        response = self.client.put(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'accepted')

    def test_list_friends(self):
        FriendRequest.objects.create(sender=self.user, receiver=self.friend_user, status='accepted')
        url = reverse('list-friends')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['email'], self.friend_user.email)
        self.assertEqual(response.data[0]['name'], self.friend_user.name)

    
    def test_list_pending_friend_requests(self):
        friend_user = get_user_model().objects._create_user(
            email='friend@example.com',
            name='Friend User',
            password='friendpassword'
        )
        FriendRequest.objects.create(
            sender=friend_user, receiver=self.user, status='pending')
        url = reverse('list-pending-friend-requests')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['sender']
                         ['email'], friend_user.email)
        self.assertEqual(response.data[0]['sender']['name'], friend_user.name)
