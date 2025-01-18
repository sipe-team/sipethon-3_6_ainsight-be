from django.db.models import Count, Q
from ninja import Router, Query
from ninja.pagination import paginate

from apps.answer.filters import AnswerFilter
from apps.answer.models import UserAnswer
from apps.answer.schemas import UserAnswerSchema
from contrib.django.ninja.pagination import ContribPageNumberPagination

router = Router(tags=["Answer"])


@router.get('/answers', response=list[UserAnswerSchema])
@paginate(ContribPageNumberPagination, page_size=4)
def get_answers(request, filter: AnswerFilter = Query(...)):
    answers = UserAnswer.objects.prefetch_related("model_answers").annotate(
        matching_names=Count(
            'model_answers',
            filter=Q(model_answers__model_id__in=filter.models)
        )
    ).filter(
        matching_names=len(filter.models)
    )
    return answers
