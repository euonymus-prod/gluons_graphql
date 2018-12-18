import graphene
from graphene_django import DjangoObjectType

from users.schema import UserType
from graphql_api.models import QuarkType
from graphql import GraphQLError
from django.db.models import Q

class QuarkTypeType(DjangoObjectType):
    class Meta:
        model = QuarkType


class Query(graphene.ObjectType):
    quark_types = graphene.List(
        QuarkTypeType,
        orderBy=graphene.String(),
    )

    def resolve_quark_types(self, info, **kwargs):
        # The value sent with the search parameter will be in the args variable
        orderBy = kwargs.get("orderBy", None)
        if orderBy:
            # qs = QuarkType.objects.order_by(orderBy).reverse()
            qs = QuarkType.objects.order_by(orderBy)
        else:
            qs = QuarkType.objects.all()

        return qs

class CreateQuarkType(graphene.Mutation):
    id = graphene.Int()
    name = graphene.String()
    image_path = graphene.String()
    name_prop = graphene.String()
    start_prop = graphene.String()
    end_prop = graphene.String()
    has_gender = graphene.Boolean()
    sort = graphene.Int()
    created_at = graphene.String()
    user = graphene.Field(UserType)

    class Arguments:
        name = graphene.String()
        image_path = graphene.String()
        name_prop = graphene.String()
        start_prop = graphene.String()
        end_prop = graphene.String()
        has_gender = graphene.Boolean()
        sort = graphene.Int()

    def mutate(self, info, name, image_path, name_prop, start_prop, end_prop, has_gender, sort):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError('You must be logged to vote!')

        quark_type = QuarkType(
            name=name,
            image_path=image_path,
            name_prop=name_prop,
            start_prop=start_prop,
            end_prop=end_prop,
            has_gender=has_gender,
            sort=sort,
        )
        quark_type.save()

        return CreateQuarkType(
            id=quark_type.id,
            name=quark_type.name,
            image_path=quark_type.image_path,
            name_prop=quark_type.name_prop,
            start_prop=quark_type.start_prop,
            end_prop=quark_type.end_prop,
            has_gender=quark_type.has_gender,
            sort=quark_type.sort,
            created_at=quark_type.created_at,
        )
    

class Mutation(graphene.ObjectType):
    create_quark_type = CreateQuarkType.Field()

