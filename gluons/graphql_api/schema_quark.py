import graphene
from graphene_django import DjangoObjectType

# from .models import Link

from users.schema import UserType
from graphql_api.models import Quark, Link, Vote
from graphql import GraphQLError
from django.db.models import Q

# Remove this Later ==============
class LinkType(DjangoObjectType):
    class Meta:
        model = Link

class VoteType(DjangoObjectType):
    class Meta:
        model = Vote
# ================================

class QuarkType(DjangoObjectType):
    class Meta:
        model = Quark


class Query(graphene.ObjectType):
    # Remove this Later ==============
    links = graphene.List(
        LinkType,
        search=graphene.String(),
        first=graphene.Int(),
        skip=graphene.Int(),
        orderBy=graphene.String(),
    )
    total_count = graphene.Int(
        search=graphene.String(),
    )
    votes = graphene.List(VoteType)
    # ================================
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

    # Remove this Later ==============
    # Use them to slice the Django queryset
    def resolve_links(self, info, search=None, first=None, skip=None, **kwargs):
        # The value sent with the search parameter will be in the args variable
        orderBy = kwargs.get("orderBy", None)
        if orderBy:
            qs = Link.objects.order_by(orderBy).reverse()
        else:
            qs = Link.objects.all()

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

    def resolve_total_count(self, info, search=None, **kwargs):
        # The value sent with the search parameter will be in the args variable
        qs = Link.objects.all()

        if search:
            filter = (
                Q(url__icontains=search) |
                Q(description__icontains=search)
            )
            qs = qs.filter(filter)

        return qs.count()

    def resolve_votes(self, info, **kwargs):
        return Vote.objects.all()
    # ================================


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

# Remove this Later ==============
class CreateLink(graphene.Mutation):
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

        link = Link(
            url=url,
            description=description,
            posted_by=user,
        )
        link.save()

        return CreateLink(
            id=link.id,
            url=link.url,
            description=link.description,
            posted_by=link.posted_by,
            created_at=link.created_at,
        )

class CreateVote(graphene.Mutation):
    user = graphene.Field(UserType)
    link = graphene.Field(LinkType)

    class Arguments:
        link_id = graphene.Int()

    def mutate(self, info, link_id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError('You must be logged in!')

        link = Link.objects.filter(id=link_id).first()
        if not link:
            raise Exception('Invalid Link!')

        Vote.objects.create(
            user=user,
            link=link,
        )

        return CreateVote(user=user, link=link)
# ================================
    

class Mutation(graphene.ObjectType):
    create_link = CreateLink.Field()
    create_vote = CreateVote.Field()

