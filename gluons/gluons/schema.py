import graphene
import graphql_jwt

import graphql_api.schema_quark
import graphql_api.schema_quark_type
import graphql_api.schema_gluon_type
import graphql_api.schema_quark_property
import graphql_api.schema_qtype_property
import graphql_api.schema_qproperty_gtype
import graphql_api.schema_qproperty_type
import users.schema


class Query(
        users.schema.Query,
        graphql_api.schema_quark.Query,
        graphql_api.schema_quark_type.Query,
        graphql_api.schema_gluon_type.Query,
        graphql_api.schema_quark_property.Query,
        graphql_api.schema_qtype_property.Query,
        graphql_api.schema_qproperty_gtype.Query,
        graphql_api.schema_qproperty_type.Query,
        graphene.ObjectType):
    pass

class Mutation(
        users.schema.Mutation,
        graphql_api.schema_quark.Mutation,
        graphql_api.schema_quark_type.Mutation,
        graphql_api.schema_gluon_type.Mutation,
        graphql_api.schema_quark_property.Mutation,
        graphql_api.schema_qtype_property.Mutation,
        graphql_api.schema_qproperty_gtype.Mutation,
        graphql_api.schema_qproperty_type.Mutation,
        graphene.ObjectType,
):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)

