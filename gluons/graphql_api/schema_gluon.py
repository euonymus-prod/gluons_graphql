import graphene
from graphene_django import DjangoObjectType

from users.schema import UserType
from graphql_api.models import Gluon, Quark, GluonType
from graphql_api.schema_quark import QuarkModelType
from graphql_api.schema_gluon_type import GluonTypeType
from graphql import GraphQLError
from django.db.models import Q

class GluonModelType(DjangoObjectType):
    class Meta:
        model = Gluon

class Query(graphene.ObjectType):
    gluon = graphene.Field(
        GluonModelType,
        id=graphene.String(),
    )
    gluons = graphene.List(
        GluonModelType,
        first=graphene.Int(),
        skip=graphene.Int(),
        orderBy=graphene.String(),
    )
    gluon_count = graphene.Int()

    def resolve_gluon(self, info, id=None, **kwargs):
        return Gluon.objects.get(id=id)

    def resolve_gluons(self, info, first=None, skip=None, **kwargs):
        # The value sent with the search parameter will be in the args variable
        orderBy = kwargs.get("orderBy", None)
        if orderBy:
            qs = Gluon.objects.order_by(orderBy).reverse()
        else:
            qs = Gluon.objects.all()

        if skip:
            qs = qs[skip:]

        if first:
            qs = qs[:first]

        return qs

    def resolve_gluon_count(self, info, **kwargs):
        # The value sent with the search parameter will be in the args variable
        qs = Quark.objects.all()
        return qs.count()



class CreateGluon(graphene.Mutation):
    id = graphene.String()
    gluon_type = graphene.Field(GluonTypeType)
    subject_quark = graphene.Field(QuarkModelType)
    object_quark = graphene.Field(QuarkModelType)
    prefix = graphene.String()
    relation = graphene.String()
    suffix = graphene.String()
    start = graphene.String()
    end = graphene.String()
    start_accuracy = graphene.String()
    end_accuracy = graphene.String()
    is_momentary = graphene.Boolean()
    url = graphene.String()
    is_private = graphene.Boolean()
    is_exclusive = graphene.Boolean()
    posted_by = graphene.Field(UserType)
    last_modified_by = graphene.Field(UserType)
    created_at = graphene.String()

    class Arguments:
        subject_quark_id = graphene.String()
        object_quark_name = graphene.String()
        gluon_type_id = graphene.Int()
        prefix = graphene.String()
        relation = graphene.String()
        suffix = graphene.String()
        start = graphene.String()
        end = graphene.String()
        start_accuracy = graphene.String()
        end_accuracy = graphene.String()
        is_momentary = graphene.Boolean()
        url = graphene.String()
        is_private = graphene.Boolean()
        is_exclusive = graphene.Boolean()

    def mutate(self, info, subject_quark_id, object_quark_name, gluon_type_id, prefix, relation, suffix,
               start, end, start_accuracy, end_accuracy, is_momentary, url, is_private, is_exclusive):

        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError('You must be logged in!')

        subject_quark = Quark.objects.get(id=subject_quark_id)
        if not subject_quark:
            raise Exception('Invalid Subject Quark!')

        object_quarks = Quark.objects.filter(name=object_quark_name)
        if not object_quarks:
            raise Exception('Invalid Object Quark!')

        if not object_quark_name:
            raise Exception('Object Quark Name is required!')

        if not relation:
            raise Exception('Relation is required!')

        gluon_type = GluonType.objects.filter(id=gluon_type_id).first()
        if not gluon_type:
            raise Exception('Invalid GluonType!')

        if len(start) == 0:
            start = None

        if len(end) == 0:
            end = None

        generated = Gluon.objects.create(
            subject_quark=subject_quark,
            object_quark=object_quarks.first(),
            gluon_type=gluon_type,

            prefix=prefix,
            relation=relation,
            suffix=suffix,
            start=start,
            end=end,
            start_accuracy=start_accuracy,
            end_accuracy=end_accuracy,
            is_momentary=is_momentary,
            url=url,
            is_private=is_private,
            is_exclusive=is_exclusive,
            posted_by=user,
            last_modified_by=user,
        )

        return CreateGluon(id=generated.id, gluon_type=gluon_type,
                           subject_quark=subject_quark, object_quark=object_quarks.first(),
                           prefix=prefix, relation=relation, suffix=suffix,
                           start=start, end=end, start_accuracy=start_accuracy, end_accuracy=end_accuracy,
                           is_momentary=is_momentary, url=url, is_private=is_private,
                           is_exclusive=is_exclusive, posted_by=user, last_modified_by=user, created_at=generated.created_at)

class Mutation(graphene.ObjectType):
    create_gluon = CreateGluon.Field()
    # update_gluon = UpdateGluon.Field()
    # delete_gluon = DeleteGluon.Field()
