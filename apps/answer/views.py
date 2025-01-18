from ninja import Router

from apps.answer.models import UserAnswer
from apps.answer.schemas import UserAnswerSchema

router = Router(tags=["Answer"])


@router.get('/answers', response=list[UserAnswerSchema])
def get_answers(request):
    answers = UserAnswer.objects.all()
    return answers
