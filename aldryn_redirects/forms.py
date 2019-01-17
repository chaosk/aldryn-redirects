from __future__ import unicode_literals

from tablib import Dataset

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from parler.forms import TranslatableModelForm

from .importers import RedirectImporter, StaticRedirectImporter
from .models import Redirect, StaticRedirect


class RedirectsImportForm(forms.Form):
    importer_class = RedirectImporter

    csv_file = forms.FileField(label=_('csv file'), required=True)

    def __init__(self, *args, **kwargs):
        super(RedirectsImportForm, self).__init__(*args, **kwargs)
        self.importer = self.importer_class()

    def clean_csv_file(self, *args, **kwargs):
        csv_file = self.cleaned_data['csv_file']
        csv_file.seek(0)
        dataset = Dataset().load(csv_file.read().decode('utf-8'), format='csv')

        for idx, row in enumerate(dataset, start=2):
            try:
                self.importer.validate_row(row)
            except ValidationError as e:
                raise forms.ValidationError('Line {}: {}'.format(idx, '\n'.join(e.messages)))

        return csv_file

    def do_import(self):
        csv_file = self.cleaned_data['csv_file']
        csv_file.seek(0)
        dataset = Dataset().load(csv_file.read().decode('utf-8'), format='csv')
        self.importer.import_from_dataset(dataset)


class StaticRedirectsImportForm(RedirectsImportForm):
    importer_class = StaticRedirectImporter


class RedirectForm(TranslatableModelForm):

    def clean(self):
        cleaned_data = super().clean()
        old_path = cleaned_data['old_path']
        qs = Redirect.objects.filter(site=cleaned_data['site'], old_path=old_path)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError({
                'old_path': _('Redirect with "{}" source path exists.').format(
                    old_path,
                ),
            })
        return cleaned_data

    class Meta:
        model = Redirect
        exclude = ('origin', )


class StaticRedirectForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        inbound_route = cleaned_data['inbound_route']
        qs = StaticRedirect.objects.filter(
            sites__in=cleaned_data['sites'],
            inbound_route=inbound_route,
        )
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError({
                'inbound_route': _('Redirect with "{}" source path exists.').format(
                    inbound_route,
                ),
            })
        return cleaned_data

    class Meta:
        model = StaticRedirect
        exclude = ('origin', )
