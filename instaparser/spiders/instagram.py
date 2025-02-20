import scrapy
import re
import json
from copy import deepcopy
from scrapy.http import HtmlResponse
from instaparser.items import InstaparserItem
from urllib.parse import urlencode

class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://instagram.com']
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    inst_graphql_link = 'https://www.instagram.com/graphql/query/?'
    inst_login = 'sergey_smit_1789'
    inst_pass = '#PWD_INSTAGRAM_BROWSER:10:1623763531:AdJQAMRVNUCQZ18PHFBfXwBVdJupunHdxeehj6Q9SI3Ul8MhJGZqWSPs6ixbqJy6UsRAsAHQsvrSCH7H9qilCTdh5o2vnLCgsBMXVX8E6OtDfrzIaqTeLdViF2roolOQ+w18N97QsVVJTcwxEZA='
    parse_user = 'teamrussia'
    query_hash = 'ea4baf885b60cbf664b34ee760397549'
    post_hash = '80d30106288209e3a17722b5f58010f7'

    def parse(self, response: HtmlResponse):             # Первый запрос на стартовую страницу
        csrf_token = self.fetch_csrf_token(response.text)   # csrf token забираем из html
        yield scrapy.FormRequest(                   # заполняем форму для авторизации
                                                    # созндает новую сессиию!
            self.inst_login_link,
            method='POST',
            callback=self.login,
            formdata={'username': self.inst_login, 'enc_password': self.inst_pass},
            headers={'X-CSRFToken': csrf_token}
        )

    def login(self, response: HtmlResponse):
        j_body = response.json()    #  Принимает валидный json
        # '{"user":true,"userId":"48134581998","authenticated":true,"oneTapPrompt":true,"status":"ok"}'
        if j_body['authenticated']:
            yield response.follow(
                f'/{self.parse_user}',
                callback=self.user_parse,
                cb_kwargs={'username': self.parse_user}         # ------->
            )                                                   #         | Сохранить порядок
                                                                #         | передовемы параметров!
    def user_parse(self, response: HtmlResponse, username):     # <-------
        user_id = self.fetch_user_id(response.text, username)
        variables = {
            'id': user_id,
            'first': 12,
        }

        url_posts = f'{self.inst_graphql_link}query_hash={self.query_hash}&{urlencode(variables)}'

        yield response.follow(
            url_posts,
            callback=self.user_posts_parse,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables': deepcopy(variables)}
        )


    def user_posts_parse(self, response: HtmlResponse, username, user_id, variables, parse_user=None):
        j_data = response.json()
        page_info = j_data.get('data').get('user').get('edge_owner_to_timeline_media').get('page_info')
        if page_info.get('has_next_page'):
            variables['after'] = page_info.get('end_cursor')

            url_posts = f'{self.inst_graphql_link}query_hash={self.query_hash}&{urlencode(variables)}'

            yield response.follow(
                url_posts,
                callback=self.user_posts_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables)}
            )

        posts = j_data.get('data').get('user').get('edge_owner_to_timeline_media').get('edges')
        for post in posts:
            shortcode = post.get('node').get('shortcode')
            yield response.follow(
                f'https://www.instagram.com/p/{shortcode}/',
                callback=self.user_post_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'shortcode': shortcode}
            )

    def user_post_parse(self, response: HtmlResponse, username, user_id, shortcode):
        print()
        variables = {
            "shortcode": shortcode,
            "child_comment_count": 3,
            "fetch_comment_count": 40,
            "parent_comment_count": 24,
            "has_threaded_comments": 'true',
        }
        url_posts = f'{self.inst_graphql_link}query_hash={self.post_hash}&{urlencode(variables)}'
        yield response.follow(
                # url_posts,
                f'https://www.instagram.com/graphql/query/?query_hash={self.post_hash}&{urlencode(variables)}',
                callback=self.user_coment_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'shortcode': shortcode}
            )

    def user_coment_parse(self, response: HtmlResponse, username, user_id, shortcode):
        j_data = response.json()
        comments = j_data.get('data').get('shortcode_media').get('edge_media_preview_comment').get('edges')

        i = 0
        for comment in comments:
            if i < 20:
                item = InstaparserItem(
                    # user_id=user_id,
                    # username=username,
                    link=f'https://www.instagram.com/p/{shortcode}/',
                    user_comment_id=comment.get('node').get('id'),
                    text=comment.get('node').get('text'),
                )
                i += 1
                yield item


    # Получаем токен для авторизации
    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    # Получаем id желаемого пользователя
    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')