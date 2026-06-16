from django import forms

MAX_RESUME_SIZE_BYTES = 10 * 1024 * 1024


class ResumeUploadForm(forms.Form):
    resume = forms.FileField(
        label='Upload Resume (PDF)',
        widget=forms.ClearableFileInput(attrs={'class': 'sh-input', 'accept': '.pdf'})
    )
    name = forms.CharField(
        max_length=100, required=False, label='Resume Label (optional)',
        widget=forms.TextInput(attrs={'class': 'sh-input', 'placeholder': 'e.g. My Tech Resume'})
    )

    def clean_resume(self):
        resume = self.cleaned_data['resume']
        if resume.size > MAX_RESUME_SIZE_BYTES:
            raise forms.ValidationError('Resume must be 10 MB or smaller.')
        return resume
