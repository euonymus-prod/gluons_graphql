import graphene
from graphene_django import DjangoObjectType

from users.schema import UserType
from graphql_api.models import QtypeProperty, QuarkType, QuarkProperty
from graphql_api.schema_quark_type import QuarkTypeType
from graphql_api.schema_quark_property import QuarkPropertyType
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
    quark_type = graphene.Field(QuarkTypeType)
    quark_property = graphene.Field(QuarkPropertyType)
    is_required = graphene.Boolean()
    created_at = graphene.String()

    class Arguments:
        quark_type_id = graphene.Int()
        quark_property_id = graphene.Int()
        is_required = graphene.Boolean()

    def mutate(self, info, is_required, quark_type_id, quark_property_id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError('You must be logged to vote!')

        quark_type = QuarkType.objects.filter(id=quark_type_id).first()
        if not quark_type:
            raise Exception('Invalid QuarkType!')

        quark_property = QuarkProperty.objects.filter(id=quark_property_id).first()
        if not quark_property:
            raise Exception('Invalid QuarkProperty!')

        QtypeProperty.objects.create(
            quark_type=quark_type,
            quark_property=quark_property,
            is_required=is_required
         )

        return CreateQtypeProperty(quark_type=quark_type, quark_property=quark_property, is_required=is_required)

class Mutation(graphene.ObjectType):
    create_qtype_property = CreateQtypeProperty.Field()

