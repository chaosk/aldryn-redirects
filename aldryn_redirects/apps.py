# -*- coding: utf-8 -*-
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

from .utils import old_path_exists


class AldrynRedirects(AppConfig):
    name = 'aldryn_redirects'
    verbose_name = 'Aldryn Redirects'

    def ready(self):
        from djangocms_versioning.exceptions import ConditionFailed
        from djangocms_versioning.models import Version
        from .models import Redirect, StaticRedirect

        def can_revert(version, user):
            if isinstance(version.content, (Redirect, StaticRedirect)):
                exists, old_path = old_path_exists(version)
                if exists:
                    raise ConditionFailed(
                        _('Redirect with "{}" source path exists.').format(
                            old_path,
                        )
                    )

        def can_discard(version, user):
            if isinstance(version.content, (Redirect, StaticRedirect)):
                try:
                    latest_version = Version.objects.filter_by_content_grouping_values(
                        version.content,
                    ).exclude(pk=version.pk).latest('created')
                except Version.DoesNotExist:
                    return
                exists, old_path = old_path_exists(latest_version)
                if exists:
                    raise ConditionFailed(
                        _('Redirect with "{}" source path exists.').format(
                            old_path,
                        )
                    )

        Version.check_revert += [can_revert]
        Version.check_discard += [can_discard]
