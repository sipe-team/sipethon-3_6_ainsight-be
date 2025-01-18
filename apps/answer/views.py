from ninja import Router
from ninja.pagination import paginate

from apps.answer.models import UserAnswer
from apps.answer.schemas import UserAnswerSchema
from contrib.django.ninja.pagination import ContribPageNumberPagination

router = Router(tags=["Answer"])


@router.get('/answers', response=list[UserAnswerSchema])
@paginate(ContribPageNumberPagination, page_size=4)
def get_answers(request):
    answers = UserAnswer.objects.all()
    return answers
