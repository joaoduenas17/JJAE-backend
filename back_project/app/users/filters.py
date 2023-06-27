from django.db.models import Q
from django_filters import rest_framework as filters
from users.models import User


class UserFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')
    exclude_user = filters.CharFilter(method='filter_exclude_user')
    order_by = filters.OrderingFilter(
        fields=(
            ('name', 'name'),
            ('last_name', 'last_name'),
            ('created_at', 'date')
        ),
        field_labels={
            'created_at': u'Fecha creación de cuenta'
        }
    )

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(last_name__icontains=value) |
            Q(email__icontains=value)
        )

    def filter_exclude_user(self, queryset, name, value):
        return queryset.exclude(id = value)
    

    class Meta:
        model = User
        fields = ['status', 'name', 'last_name', 'rol','exclude_user']

