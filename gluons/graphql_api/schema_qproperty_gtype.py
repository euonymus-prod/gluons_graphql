import graphene
from graphene_django import DjangoObjectType

from users.schema import UserType
from graphql_api.models import QpropertyGtype, QuarkProperty, GluonType
from graphql_api.schema_quark_property import QuarkPropertyType
from graphql_api.schema_gluon_type import GluonTypeType
from graphql import GraphQLError
from django.db.models import Q

class QpropertyGtypeType(DjangoObjectType):
    class Meta:
        model = QpropertyGtype

class Query(graphene.ObjectType):
    qproperty_gtypes = graphene.List(
        QpropertyGtypeType,
        orderBy=graphene.String(),
    )

    def resolve_qproperty_gtypes(self, info, **kwargs):
        # The value sent with the search parameter will be in the args variable
        orderBy = kwargs.get("orderBy", None)
        if orderBy:
            # qs = QpropertyGtype.objects.order_by(orderBy).reverse()
            qs = QpropertyGtype.objects.order_by(orderBy)
        else:
            qs = QpropertyGtype.objects.all()

        return qs

class CreateQpropertyGtype(graphene.Mutation):
    id = graphene.Int()
    quark_property = graphene.Field(QuarkPropertyType)
    gluon_type = graphene.Field(GluonTypeType)
    side = graphene.Int()
    created_at = graphene.String()

    class Arguments:
        quark_property_id = graphene.Int()
        gluon_type_id = graphene.Int()
        side = graphene.Int()

    def mutate(self, info, gluon_type_id, quark_property_id, side):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError('You must be logged in!')

        quark_property = QuarkProperty.objects.filter(id=quark_property_id).first()
        if not quark_property:
            raise Exception('Invalid QuarkProperty!')

        gluon_type = GluonType.objects.filter(id=gluon_type_id).first()
        if not gluon_type:
            raise Exception('Invalid GluonType!')

        QpropertyGtype.objects.create(
            quark_property=quark_property,
            gluon_type=gluon_type,
            side=side
         )

        return CreateQpropertyGtype(quark_property=quark_property, gluon_type=gluon_type, side=side)

class Mutation(graphene.ObjectType):
    create_qproperty_gtype = CreateQpropertyGtype.Field()

