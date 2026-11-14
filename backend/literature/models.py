from django.conf import settings
from django.db import models


class Publication(models.Model):
    pmid = models.CharField(primary_key=True, max_length=12)
    title = models.TextField()
    journal = models.TextField(blank=True)
    doi = models.TextField(blank=True)
    pmcid = models.CharField(max_length=24, blank=True)
    abstract = models.TextField(blank=True)
    publication_date = models.CharField(max_length=100, blank=True)
    metadata = models.JSONField()
    retrieved_at = models.DateTimeField(auto_now=True)


class Bookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]
        constraints = [models.UniqueConstraint(fields=["user", "publication"], name="unique_bookmark")]


class Collection(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    publications = models.ManyToManyField(Publication, through="CollectionPublication")
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        constraints = [models.UniqueConstraint(fields=["user", "name"], name="unique_collection")]


class CollectionPublication(models.Model):
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["collection", "publication"], name="unique_collection_article")]


class SearchHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    query = models.TextField()
    filters = models.JSONField(default=dict)
    sort = models.CharField(max_length=20)
    count = models.PositiveBigIntegerField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created", "-id"]
        indexes = [models.Index(fields=["user", "-created"])]


class SavedSearch(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    query = models.CharField(max_length=2500)
    filters = models.JSONField(default=dict)
    sort = models.CharField(max_length=20)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created", "-id"]
