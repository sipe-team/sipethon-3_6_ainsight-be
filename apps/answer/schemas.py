from ninja import Schema


class ModelAnswerSchema(Schema):
    model_name: str
    answer: str


class UserAnswerSchema(Schema):
    id: int
    question: str
    model_answers: list[ModelAnswerSchema]

