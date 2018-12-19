import graphene
from graphene_django import DjangoObjectType

from users.schema import UserType
from graphql_api.models import QpropertyType, QuarkProperty, QuarkType
from graphql_api.schema_quark_property import QuarkPropertyType
from graphql_api.schema_quark_type import QuarkTypeType
from graphql import GraphQLError
from django.db.models import Q

class QpropertyTypeType(DjangoObjectType):
    class Meta:
        model = QpropertyType

class Query(graphene.ObjectType):
    qproperty_types = graphene.List(
        QpropertyTypeType,
        orderBy=graphene.String(),
    )

    def resolve_qproperty_types(self, info, **kwargs):
        # The value sent with the search parameter will be in the args variable
        orderBy = kwargs.get("orderBy", None)
        if orderBy:
            # qs = QpropertyType.objects.order_by(orderBy).reverse()
            qs = QpropertyType.objects.order_by(orderBy)
        else:
            qs = QpropertyType.objects.all()

        return qs

class CreateQpropertyType(graphene.Mutation):
    id = graphene.Int()
    quark_property = graphene.Field(QuarkPropertyType)
    quark_type = graphene.Field(QuarkTypeType)
    created_at = graphene.String()

    class Arguments:
        quark_property_id = graphene.Int()
        quark_type_id = graphene.Int()

    def mutate(self, info, quark_type_id, quark_property_id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError('You must be logged in!')

        quark_property = QuarkProperty.objects.filter(id=quark_property_id).first()
        if not quark_property:
            raise Exception('Invalid QuarkProperty!')

        quark_type = QuarkType.objects.filter(id=quark_type_id).first()
        if not quark_type:
            raise Exception('Invalid QuarkType!')

        QpropertyType.objects.create(
            quark_property=quark_property,
            quark_type=quark_type,
         )

        return CreateQpropertyType(quark_property=quark_property, quark_type=quark_type)

class Mutation(graphene.ObjectType):
    create_qproperty_type = CreateQpropertyType.Field()

