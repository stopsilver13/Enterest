from django import forms


class SeatImgUploadForm(forms.Form):
    image1 = forms.ImageField()
    image2 = forms.ImageField(required=False)
    image3 = forms.ImageField(required=False)
