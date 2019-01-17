from six.moves.urllib.parse import urlparse, parse_qsl, urlencode


def get_query_params_dict(url):
    # request.GET sounds tempting below but wouldn't work for malformed querystrings (such as '/path?hamster').
    return dict(parse_qsl(urlparse(url).query, keep_blank_values=True))


def remove_query_params(url):
    return urlparse(url)._replace(query='').geturl()


def add_query_params_to_url(url, params):
    return urlparse(url)._replace(query=urlencode(params)).geturl()


def old_path_exists(version):
    old_path_field = next(
        field for field in ('old_path', 'inbound_route')
        if hasattr(version.content, field)
    )
    old_path = getattr(version.content, old_path_field)
    versionable = version.versionable
    return versionable.distinct_groupers().exclude(
        pk=version.content.pk,
    ).filter(**{
        old_path_field: old_path,
        'site_id': version.content.site_id,
    }).exists(), old_path
