from cms.app_base import CMSAppConfig

from djangocms_versioning.datastructures import default_copy, VersionableItem

from .models import Redirect, StaticRedirect


def on_draft_create(version):
    if not version.content.origin:
        version.content.origin = version.content
        version.content.save(update_fields=['origin'])


def copy_redirect(old):
    content_fields = {
        field.name: getattr(old, field.name)
        for field in Redirect._meta.fields
        if Redirect._meta.pk.name != field.name
    }
    new = Redirect.objects.create(**content_fields)
    for translation in old.translations.all():
        new.translations.create(
            language_code=translation.language_code,
            new_path=translation.new_path,
        )
    return new


def copy_static_redirect(old):
    new = default_copy(old)
    new.sites.set(old.sites.all())
    return new


class RedirectsCMSConfig(CMSAppConfig):
    djangocms_versioning_enabled = True
    djangocms_moderation_enabled = True
    versioning = [
        VersionableItem(
            content_model=Redirect,
            grouper_field_name='origin',
            copy_function=copy_redirect,
            on_draft_create=on_draft_create,
        ),
        VersionableItem(
            content_model=StaticRedirect,
            grouper_field_name='origin',
            copy_function=copy_static_redirect,
            on_draft_create=on_draft_create,
        ),
    ]
    moderated_models = [Redirect, StaticRedirect]
