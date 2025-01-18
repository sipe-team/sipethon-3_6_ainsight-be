from contrib.django import models



class UserAnswer(models.BaseDateTimeModel):
    question = models.CharField(max_length=150)

    class Meta:
        db_table = 'user_answer'


class ModelAnswer(models.BaseDateTimeModel):
    model_id = models.CharField(max_length=20)
    answer = models.TextField()
    user_answer = models.ForeignKey('answer.UserAnswer', on_delete=models.DO_NOTHING, related_name='model_answers')

    class Meta:
        db_table = 'model_answer'
