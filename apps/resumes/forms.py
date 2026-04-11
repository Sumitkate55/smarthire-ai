from django import forms


class ResumeUploadForm(forms.Form):
    resume = forms.FileField(
        label='Upload Resume (PDF)',
        widget=forms.ClearableFileInput(attrs={'class': 'sh-input', 'accept': '.pdf'})
    )
    name = forms.CharField(
        max_length=100, required=False, label='Resume Label (optional)',
        widget=forms.TextInput(attrs={'class': 'sh-input', 'placeholder': 'e.g. My Tech Resume'})
    )
