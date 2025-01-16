from ninja import Swagger, NinjaAPI


app = NinjaAPI(
    docs=Swagger(
        settings={"persistAuthorization": True, "filter": True, "tryItOutEnabled": True}
    ),
)
