import graphene
from graphene_django import DjangoObjectType

from users.schema import UserType
from graphql_api.models import QtypeProperty
from graphql import GraphQLError
from django.db.models import Q

class QtypePropertyType(DjangoObjectType):
    class Meta:
        model = QtypeProperty


class Query(graphene.ObjectType):
    qtype_properties = graphene.List(
        QtypePropertyType,
        orderBy=graphene.String(),
    )

    def resolve_qtype_properties(self, info, **kwargs):
        # The value sent with the search parameter will be in the args variable
        orderBy = kwargs.get("orderBy", None)
        if orderBy:
            # qs = QtypeProperty.objects.order_by(orderBy).reverse()
            qs = QtypeProperty.objects.order_by(orderBy)
        else:
            qs = QtypeProperty.objects.all()

        return qs

class CreateQtypeProperty(graphene.Mutation):
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
            raise GraphQLError('You must be logged to vote!')

        qtype_property = QtypeProperty(
            name=name,
            caption=caption,
            caption_ja=caption_ja,
        )
        qtype_property.save()

        return CreateQtypeProperty(
            id=qtype_property.id,
            name=qtype_property.name,
            caption=qtype_property.caption,
            caption_ja=qtype_property.caption_ja,
            created_at=qtype_property.created_at,
        )
    

class Mutation(graphene.ObjectType):
    create_qtype_property = CreateQtypeProperty.Field()

