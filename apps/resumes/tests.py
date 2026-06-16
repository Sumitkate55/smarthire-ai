from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase

from .forms import MAX_RESUME_SIZE_BYTES, ResumeUploadForm


class ResumeUploadFormTests(SimpleTestCase):
    def test_rejects_files_larger_than_ten_mb(self):
        resume = SimpleUploadedFile(
            'resume.pdf',
            b'0' * (MAX_RESUME_SIZE_BYTES + 1),
            content_type='application/pdf',
        )

        form = ResumeUploadForm(files={'resume': resume}, data={'name': 'My Resume'})

        self.assertFalse(form.is_valid())
        self.assertIn('Resume must be 10 MB or smaller.', form.errors['resume'])
