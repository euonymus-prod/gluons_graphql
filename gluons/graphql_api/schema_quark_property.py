import graphene
from graphene_django import DjangoObjectType

from users.schema import UserType
from graphql_api.models import QuarkProperty
from graphql import GraphQLError
from django.db.models import Q

class QuarkPropertyType(DjangoObjectType):
    class Meta:
        model = QuarkProperty


class Query(graphene.ObjectType):
    quark_properties = graphene.List(
        QuarkPropertyType,
        orderBy=graphene.String(),
    )

    def resolve_quark_properties(self, info, **kwargs):
        # The value sent with the search parameter will be in the args variable
        orderBy = kwargs.get("orderBy", None)
        if orderBy:
            # qs = QuarkProperty.objects.order_by(orderBy).reverse()
            qs = QuarkProperty.objects.order_by(orderBy)
        else:
            qs = QuarkProperty.objects.all()

        return qs

class CreateQuarkProperty(graphene.Mutation):
    id = graphene.Int()
    name = graphene.String()
    caption = graphene.String()
    caption_ja = graphene.String()
    created_at = graphene.String()
    user = graphene.Field(UserType)

    class Arguments:
        name = graphene.String()
        caption = graphene.String()
        caption_ja = graphene.String()

    def mutate(self, info, name, caption, caption_ja):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError('You must be logged in!')

        quark_property = QuarkProperty(
            name=name,
            caption=caption,
            caption_ja=caption_ja,
        )
        quark_property.save()

        return CreateQuarkProperty(
            id=quark_property.id,
            name=quark_property.name,
            caption=quark_property.caption,
            caption_ja=quark_property.caption_ja,
            created_at=quark_property.created_at,
        )
    

class Mutation(graphene.ObjectType):
    create_quark_property = CreateQuarkProperty.Field()

