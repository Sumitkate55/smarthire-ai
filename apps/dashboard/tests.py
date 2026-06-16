from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class GitHubLookupViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='sumit',
            email='sumit@example.com',
            password='strong-pass-123',
        )
        self.url = reverse('dashboard:github_lookup')

    def test_redirects_anonymous_user_to_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/users/login/', response.url)

    def test_authenticated_user_access(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/github_lookup.html')

    @patch('apps.dashboard.views.github_analysis')
    def test_fetches_github_data_on_query(self, mock_analysis):
        self.client.force_login(self.user)

        # Setup mock return value
        mock_data = {
            "username": "testuser",
            "name": "Test User",
            "bio": "Test Bio",
            "avatar": "https://avatar.url",
            "followers": 10,
            "following": 5,
            "public_repos": 3,
            "profile_url": "https://github.com/testuser",
            "top_repos": [],
            "top_languages": [],
            "error": None
        }
        mock_analysis.return_value = mock_data

        response = self.client.get(f"{self.url}?github=testuser")
        self.assertEqual(response.status_code, 200)
        mock_analysis.assert_called_once_with("testuser")
        self.assertEqual(response.context['github_data'], mock_data)
        self.assertContains(response, "Test User")
        self.assertContains(response, "@testuser")
