import graphene
from graphene_django import DjangoObjectType

from users.schema import UserType
from graphql_api.models import GluonType
from graphql import GraphQLError
from django.db.models import Q

class GluonTypeType(DjangoObjectType):
    class Meta:
        model = GluonType


class Query(graphene.ObjectType):
    gluon_types = graphene.List(
        GluonTypeType,
        orderBy=graphene.String(),
    )

    def resolve_gluon_types(self, info, **kwargs):
        # The value sent with the search parameter will be in the args variable
        orderBy = kwargs.get("orderBy", None)
        if orderBy:
            # qs = GluonType.objects.order_by(orderBy).reverse()
            qs = GluonType.objects.order_by(orderBy)
        else:
            qs = GluonType.objects.all()

        return qs

class CreateGluonType(graphene.Mutation):
    id = graphene.Int()
    name = graphene.String()
    caption = graphene.String()
    caption_ja = graphene.String()
    sort = graphene.Int()
    created_at = graphene.String()
    user = graphene.Field(UserType)

    class Arguments:
        name = graphene.String()
        caption = graphene.String()
        caption_ja = graphene.String()
        sort = graphene.Int()

    def mutate(self, info, name, caption, caption_ja, sort):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError('You must be logged in!')

        gluon_type = GluonType(
            name=name,
            caption=caption,
            caption_ja=caption_ja,
            sort=sort,
        )
        gluon_type.save()

        return CreateGluonType(
            id=gluon_type.id,
            name=gluon_type.name,
            caption=gluon_type.caption,
            caption_ja=gluon_type.caption_ja,
            sort=gluon_type.sort,
            created_at=gluon_type.created_at,
        )
    

class Mutation(graphene.ObjectType):
    create_gluon_type = CreateGluonType.Field()

