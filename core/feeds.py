from django.contrib.syndication.views import Feed

from .views import published_posts


class LatestPostsFeed(Feed):
    title = "Eddyforge writing"
    link = "/blog/"
    description = "New writing from Eddyforge on software, Django, and deployment."

    def items(self):
        return published_posts()[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.excerpt

    def item_pubdate(self, item):
        return item.published_at or item.created_at
