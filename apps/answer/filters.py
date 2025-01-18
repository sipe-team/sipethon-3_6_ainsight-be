from django.db.models import Q
from ninja import FilterSchema


class AnswerFilter(FilterSchema):
    models: list[str]

    def filter_models(self, data):
        return Q(model_answers__model_id__in=data)