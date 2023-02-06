from django import forms
from django.utils.translation import gettext_lazy as _

from compendium.models.models import Cabinets
from .models import Test


class TestForm(forms.ModelForm):
    def __init__(self, data=None, reward_is_active=True, *args, **kwargs):
        if not kwargs and not reward_is_active:
            initial = kwargs.get('initial', {})
            initial['reward'] = reward_is_active
            kwargs['initial'] = initial

        super().__init__(data, *args, **kwargs)
        self.label_suffix = ''  # Removes : as label suffix)

    class Meta:
        model = Test

        exclude = ['created_by', 'archived_at', 'archived_by']

        widgets = {
            'published_at': forms.DateInput(attrs={'class': 'hidden'}),
            'published_until': forms.DateInput(attrs={'class': 'hidden'}),
            'title': forms.DateInput(
                attrs={
                    'type': 'text',
                    'class': 'form-control',
                    'data-width': '50%',
                },
            ),
            'title_en': forms.DateInput(
                attrs={
                    'type': 'text',
                    'class': 'form-control',
                    'data-width': '50%',
                },
            ),
            'description': forms.DateInput(
                attrs={
                    'type': 'text',
                    'class': 'form-control',
                    'data-width': '100%',
                },
            ),
            'description_en': forms.DateInput(
                attrs={
                    'type': 'text',
                    'class': 'form-control',
                    'data-width': '100%',
                },
            ),
            'get_random_num': forms.DateInput(
                attrs={
                    'number': 'text',
                    'class': 'form-control',
                    'data-width': '100%',
                },
            ),
            'time': forms.DateInput(
                attrs={
                    'number': 'text',
                    'class': 'form-control',
                    'data-width': '100%',
                },
            ),
            'reward': forms.CheckboxInput(
                attrs={'class': 'custom-control-input'},
            ),
            'is_english_version': forms.CheckboxInput(
                attrs={'class': 'custom-control-input'},
            ),
        }

        labels = {
            'title': _('Title'),
            'title_en': _('Title (English)'),
            'is_english_version': _(
                'Ability to add English version of questions',
            ),
            'description': _('Description'),
            'description_en': _('Description (English)'),
            'time': _('Timer'),
            'get_random_num': _('Random questions'),
            'published_at': _('Publication start date'),
            'published_until': _('Publication end date'),
            'reward': _('Reward'),
            'base_groups': _('Global roles'),
        }

        help_texts = {
            'title': None,
            'title_en': None,
            'description': None,
            'description_en': None,
            'published_at': None,
            'published_until': None,
            'base_groups': _('Roles for which test will be available'),
        }


class TestQuestionAnswerForm(forms.Form):
    def __init__(
            self, data=None, files=None, with_english=False, *args, **kwargs,
    ):
        self.with_english = with_english

        super().__init__(data, files, *args, **kwargs)

        if not with_english:
            del self.fields['q_en']
            del self.fields['a_en_1']
            del self.fields['a_en_2']

        if data:
            answers_number = self.answers_counter(data)
            if answers_number > 2:
                for i in range(3, answers_number + 1):
                    field_name = 'a_ru_{}'.format(i)
                    label = _('Question')
                    self.fields[field_name] = forms.CharField(
                        label=label,
                        max_length=300,
                        widget=forms.TextInput(
                            attrs={'class': 'form-control'},
                        ),
                    )
                    if with_english:
                        field_name = 'a_en_{}'.format(i)
                        label = _('Question (English)')
                        self.fields[field_name] = forms.CharField(
                            label=label,
                            max_length=300,
                            widget=forms.TextInput(
                                attrs={'class': 'form-control'},
                            ),
                        )
                    self.fields['a_correct_{}'.format(i)] = forms.BooleanField(
                        required=False,
                        label=_('Is answer correct?'),
                        widget=forms.CheckboxInput(attrs={'class': 'mr-2'}),
                    )

    @staticmethod
    def answers_counter(post_data):
        result = 0
        for item in post_data:
            if item.startswith('a_ru_'):
                result += 1

        return result

    q_ru = forms.CharField(
        label=_('Question'),
        max_length=300,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    q_en = forms.CharField(
        label=_('Question (English)'),
        max_length=300,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    q_img = forms.ImageField(required=False, label=_('Question image'))

    a_ru_1 = forms.CharField(
        label=_('Answer'),
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    a_en_1 = forms.CharField(
        label=_('Answer (English)'),
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    a_correct_1 = forms.BooleanField(
        required=False,
        label=_('Is answer correct?'),
        widget=forms.CheckboxInput(attrs={'class': 'mr-2'}),
    )

    a_ru_2 = forms.CharField(
        label=_('Answer'),
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    a_en_2 = forms.CharField(
        label=_('Answer (English)'),
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    a_correct_2 = forms.BooleanField(
        required=False,
        label=_('Is answer correct?'),
        widget=forms.CheckboxInput(attrs={'class': 'mr-2'}),
    )

    def is_valid(self):
        valid = super().is_valid()
        if not valid:
            return valid

        # Disallow use "\" character in answers.
        cleaned_data = self.cleaned_data.copy()
        for item in cleaned_data:
            if item.startswith('a_ru') or item.startswith('a_en'):
                if '\\' in cleaned_data[item]:
                    self.add_error(
                        item,
                        forms.ValidationError(
                            _(
                                'Please do not use "\\" character inside answers.',
                            ),
                        ),
                    )
                    break

        if not self.errors:
            return True

        return False


class AssignTestForm(forms.Form):
    assign_file = forms.FileField(label=_('File with logins'))


class AssignTestOnCabinetForm(forms.Form):
    choices = Cabinets.objects.all().values_list('pk', 'name')
    choices = list(choices)

    cabinet = forms.ChoiceField(choices=choices)


class ArchivedTestsDateRange(forms.Form):
    date_from = forms.DateField(
        label=_('Date from'), widget=forms.DateInput(attrs={'type': 'date'}),
    )
    date_until = forms.DateField(
        label=_('Date until'), widget=forms.DateInput(attrs={'type': 'date'}),
    )
