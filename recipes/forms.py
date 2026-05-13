from django import forms


class RecipeSearchForm(forms.Form):
    ingredients = forms.CharField(
        label="Ingredients you have",
        widget=forms.TextInput(
            attrs={
                "placeholder": "chicken, rice, broccoli",
            }
        ),
    )

    max_prep_time = forms.IntegerField(
        label="Maximum prep time",
        required=False,
        min_value=1,
    )

    cuisine = forms.CharField(
        label="Cuisine",
        required=False,
    )

    dietary_preference = forms.CharField(
        label="Dietary preference",
        required=False,
    )