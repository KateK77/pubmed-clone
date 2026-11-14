from django.contrib.auth import authenticate, get_user_model, login, logout, update_session_auth_hash
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, connection, transaction
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import serializers
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import SimpleRateThrottle
from rest_framework.views import APIView

from . import ncbi
from .citations import FORMATS, citation
from .models import Bookmark, Collection, CollectionPublication, Publication, SavedSearch, SearchHistory
from .query import FILTERS, PMID, build_query, search_options

User = get_user_model()


class AccountThrottle(SimpleRateThrottle):
    rate = "20/min"

    def get_cache_key(self, request, view):
        return "account:" + self.get_ident(request)


class AccountInput(serializers.Serializer):
    username = serializers.RegexField(r"^[\w.@+-]+\Z", max_length=150)
    password = serializers.CharField(max_length=128, trim_whitespace=False)
    email = serializers.EmailField(required=False, allow_blank=True)


class ProfileInput(serializers.Serializer):
    email = serializers.EmailField(required=False, allow_blank=True)
    first_name = serializers.CharField(required=False, max_length=150, allow_blank=True)
    last_name = serializers.CharField(required=False, max_length=150, allow_blank=True)
    password = serializers.CharField(required=False, max_length=128, trim_whitespace=False)
    current_password = serializers.CharField(required=False, max_length=128, trim_whitespace=False)


class RowsInput(serializers.Serializer):
    rows = serializers.ListField(child=serializers.DictField(), min_length=1, max_length=20)


class NameInput(serializers.Serializer):
    name = serializers.CharField(max_length=120)


class ArticleInput(serializers.Serializer):
    pmid = serializers.RegexField(PMID, max_length=12)

    def validate_pmid(self, value):
        return valid_pmid(value)


class ExportInput(serializers.Serializer):
    format = serializers.ChoiceField(choices=list(FORMATS))
    ids = serializers.ListField(child=serializers.RegexField(PMID, max_length=12), required=False, max_length=200)
    collection = serializers.IntegerField(required=False, min_value=1)
    bookmarks = serializers.BooleanField(required=False, default=False)


class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchHistory
        fields = ("id", "query", "filters", "sort", "count", "created")


class SavedSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedSearch
        fields = ("id", "query", "filters", "sort", "created")


def clean(serializer, data):
    instance = serializer(data=data)
    instance.is_valid(raise_exception=True)
    return instance.validated_data


def valid_pmid(pmid):
    if not PMID.fullmatch(pmid):
        raise ValidationError("Enter a valid PMID.")
    return pmid


class SearchInput(serializers.Serializer):
    q = serializers.CharField(max_length=2500)
    sort = serializers.ChoiceField(choices=["best", "recent", "publication"], required=False)
    page = serializers.IntegerField(min_value=1, required=False)
    size = serializers.ChoiceField(choices=[10, 20, 50], required=False)
    years = serializers.ChoiceField(choices=["1", "5", "10"], required=False)
    type = serializers.CharField(required=False)
    language = serializers.CharField(required=False)
    text = serializers.CharField(required=False)
    species = serializers.CharField(required=False)
    subset = serializers.CharField(required=False)

    def get_fields(self):
        fields = super().get_fields()
        fields.update({key: serializers.DateField(required=False) for key in ("from", "to")})
        return fields


def person(user):
    return {field: getattr(user, field) for field in ("id", "username", "email", "first_name", "last_name")} if user.is_authenticated else None


def password_check(password, user):
    try:
        validate_password(password, user=user)
    except DjangoValidationError as exc:
        raise ValidationError({"password": exc.messages}) from exc


@extend_schema(responses={200: OpenApiTypes.OBJECT})
@ensure_csrf_cookie
@api_view(["GET"])
def session(request):
    return Response({"user": person(request.user)})


@extend_schema(request=AccountInput, responses={200: OpenApiTypes.OBJECT})
@api_view(["POST"])
@throttle_classes([AccountThrottle])
def account(request, action):
    SessionAuthentication().enforce_csrf(request)
    if action == "logout":
        logout(request)
        return Response({"user": None})
    data = clean(AccountInput, request.data)
    if action == "register":
        candidate = User(username=data["username"], email=data.get("email", ""))
        password_check(data["password"], candidate)
        try:
            with transaction.atomic():
                user = User.objects.create_user(**data)
        except IntegrityError as exc:
            raise ValidationError("This username is already registered.") from exc
    else:
        user = authenticate(request, username=data["username"], password=data["password"])
        if user is None:
            raise ValidationError("Username or password is incorrect.")
    login(request, user)
    return Response({"user": person(user)})


@extend_schema(request=ProfileInput, responses={200: OpenApiTypes.OBJECT})
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def profile(request):
    user = request.user
    data = clean(ProfileInput, request.data)
    current = data.pop("current_password", "")
    password = data.pop("password", "")
    fields = list(data)
    for key, value in data.items():
        setattr(user, key, value)
    if password:
        if not user.check_password(current):
            raise ValidationError("The current password is incorrect.")
        password_check(password, user)
        user.set_password(password)
        fields.append("password")
    user.save(update_fields=fields)
    if password:
        update_session_auth_hash(request, user)
    return Response({"user": person(user)})


@extend_schema(responses={200: OpenApiTypes.OBJECT})
@api_view(["GET"])
def health(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    return Response({"status": "ok"})


@extend_schema(parameters=[OpenApiParameter(name, str, required=name == "q") for name in
                           ("q", "sort", "page", "size", "years", "from", "to", *FILTERS)],
               responses={200: OpenApiTypes.OBJECT})
@api_view(["GET"])
def search(request):
    return Response(ncbi.search(search_options(request.query_params)))


@extend_schema(request=SearchInput, responses={201: HistorySerializer})
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def record_search(request):
    options = search_options(request.data)
    result = ncbi.search(options)
    item = SearchHistory.objects.create(user=request.user, query=options["query"],
                                        filters=options["filters"], sort=options["sort"], count=result["count"])
    return Response(HistorySerializer(item).data, status=201)


@extend_schema(request=RowsInput, responses={200: OpenApiTypes.OBJECT})
@api_view(["POST"])
def advanced(request):
    return Response({"query": build_query(clean(RowsInput, request.data)["rows"])})


@extend_schema(responses={200: OpenApiTypes.OBJECT})
@api_view(["GET"])
def publication(request, pmid):
    return Response(ncbi.detail(valid_pmid(pmid)))


@extend_schema(operation_id="publication_relationships", responses={200: OpenApiTypes.OBJECT})
@api_view(["GET"])
def relationships(request, pmid, kind):
    return Response({"results": ncbi.related(valid_pmid(pmid), cited=kind == "cited-by")})


def stored_article(pmid):
    article = Publication.objects.filter(pk=valid_pmid(pmid)).first()
    if article:
        return article
    data = ncbi.detail(pmid)
    article, _ = Publication.objects.get_or_create(
        pk=pmid, defaults={"title": data["title"], "journal": data["journal"], "doi": data["doi"],
                           "pmcid": data["pmcid"], "publication_date": data["date"],
                           "abstract": "\n".join(item["text"] for item in data["abstract"]), "metadata": data},
    )
    return article


def article_list(queryset, params):
    search_term = params.get("q", "").strip()
    if search_term:
        queryset = queryset.filter(Q(title__icontains=search_term) | Q(pmid=search_term) | Q(journal__icontains=search_term))
    sort = params.get("sort", "added")
    order = {"title": "title", "date": "-publication_date"}
    if sort in order:
        queryset = queryset.order_by(order[sort], "pmid")
    return [item.metadata for item in queryset]


@extend_schema_view(get=extend_schema(responses={200: OpenApiTypes.OBJECT}),
                    post=extend_schema(request=ArticleInput, responses={201: OpenApiTypes.OBJECT}),
                    delete=extend_schema(responses={204: None}))
class Bookmarks(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        articles = Publication.objects.filter(bookmark__user=request.user).order_by("-bookmark__created")
        return Response({"results": article_list(articles, request.query_params)})

    def post(self, request):
        article = stored_article(clean(ArticleInput, request.data)["pmid"])
        _, created = Bookmark.objects.get_or_create(user=request.user, publication=article)
        return Response(article.metadata, status=201 if created else 200)

    def delete(self, request, pmid):
        Bookmark.objects.filter(user=request.user, publication_id=valid_pmid(pmid)).delete()
        return Response(status=204)


def collection_data(item):
    return {"id": item.id, "name": item.name, "count": item.article_count if hasattr(item, "article_count") else item.publications.count()}


@extend_schema_view(get=extend_schema(responses={200: OpenApiTypes.OBJECT}),
                    post=extend_schema(request=NameInput, responses={201: OpenApiTypes.OBJECT}),
                    patch=extend_schema(request=NameInput, responses={200: OpenApiTypes.OBJECT}),
                    delete=extend_schema(responses={204: None}))
class Collections(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk is None:
            return Response({"results": [collection_data(item) for item in Collection.objects.filter(user=request.user).annotate(article_count=Count("publications"))]})
        item = get_object_or_404(Collection, user=request.user, pk=pk)
        articles = item.publications.order_by("-collectionpublication__created")
        return Response({**collection_data(item), "results": article_list(articles, request.query_params)})

    def post(self, request):
        name = clean(NameInput, request.data)["name"]
        item, created = Collection.objects.get_or_create(user=request.user, name=name)
        return Response(collection_data(item), status=201 if created else 200)

    def patch(self, request, pk):
        item = get_object_or_404(Collection, user=request.user, pk=pk)
        item.name = clean(NameInput, request.data)["name"]
        try:
            with transaction.atomic():
                item.save(update_fields=["name"])
        except IntegrityError as exc:
            raise ValidationError("A collection already uses that name.") from exc
        return Response(collection_data(item))

    def delete(self, request, pk):
        get_object_or_404(Collection, user=request.user, pk=pk).delete()
        return Response(status=204)


@extend_schema_view(get=extend_schema(operation_id="collection_detail", responses={200: OpenApiTypes.OBJECT}))
class CollectionDetail(Collections):
    http_method_names = ["get", "patch", "delete"]


@extend_schema_view(post=extend_schema(request=ArticleInput, responses={201: OpenApiTypes.OBJECT}),
                    delete=extend_schema(responses={204: None}))
class CollectionArticles(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        item = get_object_or_404(Collection, user=request.user, pk=pk)
        article = stored_article(clean(ArticleInput, request.data)["pmid"])
        _, created = CollectionPublication.objects.get_or_create(collection=item, publication=article)
        return Response(article.metadata, status=201 if created else 200)

    def delete(self, request, pk, pmid):
        item = get_object_or_404(Collection, user=request.user, pk=pk)
        item.publications.remove(valid_pmid(pmid))
        return Response(status=204)


@extend_schema(responses={200: HistorySerializer(many=True), 204: None})
@api_view(["GET", "DELETE"])
@permission_classes([IsAuthenticated])
def history(request):
    queryset = SearchHistory.objects.filter(user=request.user)
    if request.method == "DELETE":
        queryset.delete()
        return Response(status=204)
    return Response(HistorySerializer(queryset[:500], many=True).data)


@extend_schema(request=SearchInput, responses={200: SavedSearchSerializer(many=True), 201: SavedSearchSerializer, 204: None})
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def saved_searches(request):
    queryset = SavedSearch.objects.filter(user=request.user)
    if request.method == "GET":
        return Response(SavedSearchSerializer(queryset, many=True).data)
    options = search_options(request.data)
    item = queryset.create(user=request.user, query=options["query"], filters=options["filters"], sort=options["sort"])
    return Response(SavedSearchSerializer(item).data, status=201)


@extend_schema(operation_id="delete_history_item", responses={204: None})
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def history_item(request, pk):
    SearchHistory.objects.filter(user=request.user, pk=pk).delete()
    return Response(status=204)


@extend_schema(responses={204: None})
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def saved_search_item(request, pk):
    SavedSearch.objects.filter(user=request.user, pk=pk).delete()
    return Response(status=204)


@extend_schema(request=ExportInput, responses={(200, "text/plain"): str})
@api_view(["POST"])
def export(request):
    data = clean(ExportInput, request.data)
    sources = [bool(data.get("ids")), bool(data.get("collection")), data["bookmarks"]]
    if sum(sources) != 1:
        raise ValidationError("Choose articles, a collection, or bookmarks.")
    if data.get("ids"):
        ids = list(dict.fromkeys(valid_pmid(pmid) for pmid in data["ids"]))
        records = {item.pmid: item.metadata for item in Publication.objects.filter(pk__in=ids)}
        missing = [pmid for pmid in ids if pmid not in records]
        for start in range(0, len(missing), 50):
            records.update((item["pmid"], item) for item in ncbi.fetch(missing[start:start + 50]))
        if any(pmid not in records for pmid in ids):
            raise ValidationError("One or more articles could not be retrieved for export.")
        articles = [records[pmid] for pmid in ids]
    else:
        if not request.user.is_authenticated:
            from rest_framework.exceptions import NotAuthenticated
            raise NotAuthenticated()
        if data.get("collection"):
            articles = get_object_or_404(Collection, user=request.user, pk=data["collection"]).publications.all()
        else:
            articles = Publication.objects.filter(bookmark__user=request.user)
        articles = [item.metadata for item in articles]
    style = data["format"]
    response = HttpResponse("\n\n".join(citation(item, style) for item in articles) + "\n", content_type="text/plain; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="medresearch.{FORMATS[style]}"'
    return response
