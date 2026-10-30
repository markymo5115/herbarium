"""Forms for accounts and user-managed personal formula editing."""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import inlineformset_factory

from .models import Herb, PersonalFormula, PersonalFormulaIngredient


class SignUpForm(UserCreationForm):
    """User registration form with optional email capture."""

    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class PersonalFormulaForm(forms.ModelForm):
    """Top-level form for naming and annotating a user's personal formula."""

    class Meta:
        model = PersonalFormula
        fields = ["name", "for_whom", "source_formula", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 4}),
        }


class PersonalFormulaIngredientForm(forms.ModelForm):
    """Ingredient form that accepts either a database herb or free text."""

    class Meta:
        model = PersonalFormulaIngredient
        fields = ["herb", "custom_name", "amount", "notes"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["herb"].queryset = Herb.objects.select_related("category").order_by(
            "pinyin_name", "english_name"
        )
        self.fields["herb"].required = False
        self.fields["herb"].label = "Database herb"
        self.fields["custom_name"].required = False
        self.fields["custom_name"].label = "Ingredient name"
        self.fields["custom_name"].widget.attrs[
            "placeholder"
        ] = "Use if the herb is not in the database"

    def clean(self):
        """Require a linked herb or custom ingredient name when a row has data."""

        cleaned_data = super().clean()
        herb = cleaned_data.get("herb")
        custom_name = cleaned_data.get("custom_name")
        amount = cleaned_data.get("amount")
        notes = cleaned_data.get("notes")
        delete = cleaned_data.get("DELETE")
        if not any([herb, custom_name, amount, notes]):
            return cleaned_data
        if not delete and not herb and not custom_name:
            raise forms.ValidationError(
                "Choose a database herb or enter an ingredient name."
            )
        return cleaned_data


PersonalFormulaIngredientFormSet = inlineformset_factory(
    PersonalFormula,
    PersonalFormulaIngredient,
    form=PersonalFormulaIngredientForm,
    extra=5,
    can_delete=True,
)
