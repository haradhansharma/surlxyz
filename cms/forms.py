from django import forms

class BlogSearchForm(forms.Form):
    search_query = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder':"Search ...", 'class':'form-control'}))
    
