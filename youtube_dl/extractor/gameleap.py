from __future__ import unicode_literals

import re

from .once import OnceIE
from ..compat import (
    compat_urllib_parse_unquote,
)
from ..utils import (
    unescapeHTML,
    url_basename,
    dict_get,
)


class GameLeapIE(OnceIE):
    _VALID_URL = r'https?://(?:www\.)?gameleap\.com/dota/course/.+~(?P<id>crs_[0-9a-zA-Z]+_)/.+'
    _TESTS = []

    def _real_extract(self, url):
        page_id = self._match_id(url)
        api_url = "https://api.gameleap.com/api/courses/" + page_id + "?game=dota&flatten=true"
        webpage = self._download_json(api_url, page_id)

        course = webpage['result']['course']
        sections_raw = course['sections']

        to_tuples_list = map(lambda x: (x['_id'], x['name']), sections_raw)
        section_id_to_name = dict(to_tuples_list)

        items = webpage['result']['courseItems']
        items = map(lambda x:
                    {
                        'id': x['_id'],
                        'url': x['item']['sources']['hlsPremium'],
                        'section': section_id_to_name[x['section']],
                        'name': x['item']['title'],
                    }, items)

        entries = []
        for item in items:
            formats = self._extract_m3u8_formats(item['url'], item['id'])
            self._sort_formats(formats, ('preference', 'height', 'width', 'fps', 'tbr', 'format_id'))
            entries.append(
                {
                    'id': item['id'],
                    'formats': formats,
                    'chapter': item['section'],
                    'title': item['name'],
                }
            )

        return self.playlist_result(entries, course['_id'], course['name'], course['description'])
