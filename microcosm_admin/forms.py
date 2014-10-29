import django.forms
from django.core.exceptions import ValidationError


def validate_no_spaces(value):
    if ' ' in value:
        raise ValidationError('Profile name cannot contain spaces')


class ProfileEdit(django.forms.Form):
    """
    Form for editing a profile.
    """

    id = django.forms.IntegerField(widget=django.forms.HiddenInput)
    avatar = django.forms.ImageField(required=False)
    profileName = django.forms.CharField(
        max_length='25',
        label='Choose a username by which you wish to be known',
        error_messages = {
            'required' : 'Please add a profile name',
            'max_length' : 'Profile name may not be longer than 25 characters'
        },
        validators=[validate_no_spaces]
    )


class SiteCreate(django.forms.Form):
    """
    Form for creating a site.
    """

    title = django.forms.CharField()
    description = django.forms.CharField()
    subdomainKey = django.forms.CharField()
    domain = django.forms.CharField()
    themeId = django.forms.IntegerField()
    logoUrl = django.forms.CharField()
    backgroundColor = django.forms.CharField()
    backgroundUrl = django.forms.CharField()
    backgroundPosition = django.forms.CharField()
    linkColor = django.forms.CharField()
    gaWebPropertyId = django.forms.CharField()
