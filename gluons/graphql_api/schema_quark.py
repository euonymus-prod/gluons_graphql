import graphene
from graphene_django import DjangoObjectType

from users.schema import UserType
from graphql_api.models import Quark
from graphql import GraphQLError
from django.db.models import Q

class QuarkType(DjangoObjectType):
    class Meta:
        model = Quark


class Query(graphene.ObjectType):
    quarks = graphene.List(
        QuarkType,
        search=graphene.String(),
        first=graphene.Int(),
        skip=graphene.Int(),
        orderBy=graphene.String(),
    )
    quark_count = graphene.Int(
        search=graphene.String(),
    )

    def resolve_quarks(self, info, search=None, first=None, skip=None, **kwargs):
        # The value sent with the search parameter will be in the args variable
        orderBy = kwargs.get("orderBy", None)
        if orderBy:
            qs = Quark.objects.order_by(orderBy).reverse()
        else:
            qs = Quark.objects.all()

        if search:
            filter = (
                Q(url__icontains=search) |
                Q(description__icontains=search)
            )
            qs = qs.filter(filter)

        if skip:
            qs = qs[skip:]

        if first:
            qs = qs[:first]

        return qs

    def resolve_quark_count(self, info, search=None, **kwargs):
        # The value sent with the search parameter will be in the args variable
        qs = Quark.objects.all()

        if search:
            filter = (
                Q(url__icontains=search) |
                Q(description__icontains=search)
            )
            qs = qs.filter(filter)

        return qs.count()

class CreateQuark(graphene.Mutation):
    id = graphene.Int()
    url = graphene.String()
    description = graphene.String()
    posted_by = graphene.Field(UserType)
    created_at = graphene.String()

    class Arguments:
        url = graphene.String()
        description = graphene.String()

    def mutate(self, info, url, description):
        user = info.context.user or None

        quark = Quark(
            url=url,
            description=description,
            posted_by=user,
        )
        quark.save()

        return CreateQuark(
            id=quark.id,
            url=quark.url,
            description=quark.description,
            posted_by=quark.posted_by,
            created_at=quark.created_at,
        )

class Mutation(graphene.ObjectType):
    create_quark = CreateQuark.Field()


