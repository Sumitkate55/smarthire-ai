import uuid
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.resumes.models import ResumeRecord

from .models import ScoreRecord


class AnalyzeViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='sumit',
            email='sumit@example.com',
            password='strong-pass-123',
        )
        self.client.force_login(self.user)
        self.resume = ResumeRecord.objects.create(
            resume_id=uuid.uuid4(),
            user=self.user,
            username=self.user.username,
            label='Backend Resume',
            filename='backend.pdf',
            raw_text=(
                'Python Django SQL project experience education '
                'email sumit@example.com github linkedin'
            ),
            extracted_skills=['python', 'django', 'sql', 'github'],
        )

    def test_save_flag_creates_one_score_then_redirects_to_clean_url(self):
        url = reverse('scoring:analyze', kwargs={'resume_id': self.resume.resume_id})

        response = self.client.get(f'{url}?save=1')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['Location'], url)
        self.assertEqual(ScoreRecord.objects.count(), 1)

        clean_response = self.client.get(url)

        self.assertEqual(clean_response.status_code, 200)
        self.assertEqual(ScoreRecord.objects.count(), 1)


class GitHubAnalysisTests(TestCase):
    @patch('core.services.resume_analyzer.requests.get')
    def test_github_username_cleaning(self, mock_get):
        from unittest.mock import MagicMock
        from core.services.resume_analyzer import github_analysis

        # Setup mock response for profile info to return 404 so it returns early
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        # Test full URL extraction
        github_analysis("https://github.com/testuser")
        called_url = mock_get.call_args_list[-1][0][0]
        self.assertEqual(called_url, "https://api.github.com/users/testuser")

        # Test URL with query parameters
        github_analysis("https://github.com/anotheruser?tab=repositories")
        called_url = mock_get.call_args_list[-1][0][0]
        self.assertEqual(called_url, "https://api.github.com/users/anotheruser")

        # Test @ username
        github_analysis("@atuser")
        called_url = mock_get.call_args_list[-1][0][0]
        self.assertEqual(called_url, "https://api.github.com/users/atuser")

        # Test trailing slash
        github_analysis("slashuser/")
        called_url = mock_get.call_args_list[-1][0][0]
        self.assertEqual(called_url, "https://api.github.com/users/slashuser")

