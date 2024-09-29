from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import filters, serializers

from user.models import User


class CustomHighlightFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        active = request.query_params.get('active', None)
        min_views = request.query_params.get('min_views', None)
        max_views = request.query_params.get('max_views', None)
        order_by = request.query_params.get("order_by")

        uploaded_by = request.query_params.get('uploaded_by', None)
        liked_highlights = request.query_params.get('liked_highlights', None)

        if liked_highlights is not None:
            if liked_highlights.lower() == 'true':
                queryset = queryset.filter(liked_by_user = request.user)
            elif liked_highlights.lower() == 'false':
                queryset = queryset.exclude(liked_by_user = request.user)
        if active is not None:
            if active.lower() == 'true':
                queryset = queryset.filter(active=True)
            elif active.lower() == 'false':
                queryset = queryset.filter(active=False)
        if min_views is not None:
            queryset = queryset.filter(views__gte=min_views)
        if max_views is not None:
            queryset = queryset.filter(views__lte=max_views)

        if order_by == "views_asc":
            queryset = queryset.order_by("views")
        if order_by == "views_desc":
            queryset = queryset.order_by("-views")

        if order_by == 'likes_asc':
            queryset = queryset.annotate(num_likes=Count('liked_by_user')).order_by('num_likes')
        elif order_by == 'likes_desc':
            queryset = queryset.annotate(num_likes=Count('liked_by_user')).order_by('-num_likes')

        if uploaded_by is not None:
            # Fetch the user object corresponding to the username
            user = get_object_or_404(User, username=uploaded_by)
            queryset = queryset.filter(uploaded_by=user)

        return queryset


class CustomLikeCountFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        least_likes = request.query_params.get('least_likes')
        most_likes = request.query_params.get("most_likes")

        if least_likes:
            queryset = queryset.annotate(num_likes=Count('liked_by_user')).filter(num_likes__gte=least_likes)

        if most_likes:
            queryset = queryset.annotate(num_likes=Count('liked_by_user')).filter(num_likes__lte=most_likes)

        return queryset

from django.utils.timezone import datetime
class MatchDetailFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        date = request.query_params.get('date')

        if date:
            try:
                # Parse the date parameter into a datetime.date object
                date = datetime.strptime(date, "%Y-%m-%d").date()
                # Filter the queryset to get matches happening on the given date
                queryset = queryset.filter(match_date=date)

                # Check if the filtered queryset is empty
                if not queryset.exists():
                    raise serializers.ValidationError("No matches found on this date.")
            except ValueError:
                raise serializers.ValidationError("Invalid date format. Date should be in YYYY-MM-DD format.")

        return queryset

