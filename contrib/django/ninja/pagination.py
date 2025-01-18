from typing import Any

from django.db.models import QuerySet
from ninja.pagination import PageNumberPagination


class ContribPageNumberPagination(PageNumberPagination):

    class Input(PageNumberPagination.Input):
        pass

    class Output(PageNumberPagination.Output):
        current_page: int
        has_next: bool

    def __init__(self, page_size: int = 10) -> None:
        super().__init__(page_size)

    def paginate_queryset(
        self, queryset: QuerySet, pagination: Input, **params: Any
    ) -> Any:
        offset = (pagination.page - 1) * self.page_size
        items = queryset[offset : offset + self.page_size]
        count = self._items_count(queryset)
        return {
            "items": items,
            "count": count,
            "current_page": pagination.page,
            "has_next": self.page_size * pagination.page < count,
        }  # noqa: E203
        return super().paginate_queryset(queryset, pagination, **params)
