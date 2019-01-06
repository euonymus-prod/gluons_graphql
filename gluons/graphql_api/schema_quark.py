import graphene
from graphene_django import DjangoObjectType

from users.schema import UserType
from graphql_api.models import Quark, QuarkType
from graphql_api.schema_quark_type import QuarkTypeType
from graphql import GraphQLError
from django.db.models import Q

class QuarkModelType(DjangoObjectType):
    class Meta:
        model = Quark


class Query(graphene.ObjectType):
    quark = graphene.Field(
        QuarkModelType,
        id=graphene.String()
    )
    quarks = graphene.List(
        QuarkModelType,
        search=graphene.String(),
        first=graphene.Int(),
        skip=graphene.Int(),
        orderBy=graphene.String(),
    )
    quark_count = graphene.Int(
        search=graphene.String(),
    )

    def resolve_quark(self, info, id=None, **kwargs):
        return Quark.objects.get(id=id)

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
    id = graphene.String()
    quark_type = graphene.Field(QuarkTypeType)
    name = graphene.NonNull(graphene.String)
    image_path = graphene.String()
    description = graphene.String()
    start = graphene.String()
    end = graphene.String()
    start_accuracy = graphene.String()
    end_accuracy = graphene.String()
    is_momentary = graphene.Boolean()
    url = graphene.String()
    affiliate = graphene.String()
    is_private = graphene.Boolean()
    is_exclusive = graphene.Boolean()
    auto_fill = graphene.Boolean()
    posted_by = graphene.Field(UserType)
    last_modified_by = graphene.Field(UserType)
    created_at = graphene.String()

    class Arguments:
        name = graphene.NonNull(graphene.String)
        image_path = graphene.String()
        description = graphene.String()
        start = graphene.String()
        end = graphene.String()
        start_accuracy = graphene.String()
        end_accuracy = graphene.String()
        is_momentary = graphene.Boolean()
        url = graphene.String()
        affiliate = graphene.String()
        is_private = graphene.Boolean()
        is_exclusive = graphene.Boolean()
        auto_fill = graphene.Boolean()
        quark_type_id = graphene.Int()

    def mutate(self, info, name, image_path, description, start, end, start_accuracy, end_accuracy,
               is_momentary, url, affiliate, is_private, is_exclusive, auto_fill, quark_type_id):

        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError('You must be logged in!')

        if name is '':
            raise Exception('Name is required')

        quark_type = QuarkType.objects.filter(id=quark_type_id).first()
        if not quark_type:
            raise Exception('Invalid QuarkType!')

        if len(start) == 0:
            start = None

        if len(end) == 0:
            end = None

        if auto_fill and (image_path is ''):
            from graphql_api.common import camel_to_snake
            image_file_name = camel_to_snake(quark_type.name)
            image_path = "/img/%s.png" % image_file_name

        generated = Quark.objects.create(
            quark_type=quark_type,
            name=name,
            image_path=image_path,
            description=description,
            start=start,
            end=end,
            start_accuracy=start_accuracy,
            end_accuracy=end_accuracy,
            is_momentary=is_momentary,
            url=url,
            affiliate=affiliate,
            is_private=is_private,
            is_exclusive=is_exclusive,
            posted_by=user,
            last_modified_by=user,
         )

        return CreateQuark(quark_type=quark_type, id=generated.id, name=name, image_path=image_path, description=description,
                           start=start, end=end, start_accuracy=start_accuracy, end_accuracy=end_accuracy,
                           is_momentary=is_momentary, url=url, affiliate=affiliate, is_private=is_private,
                           is_exclusive=is_exclusive, posted_by=user, last_modified_by=user, created_at=generated.created_at)

class UpdateQuark(graphene.Mutation):
    id = graphene.String()
    quark_type = graphene.Field(QuarkTypeType)
    name = graphene.String()
    image_path = graphene.String()
    description = graphene.String()
    start = graphene.String()
    end = graphene.String()
    start_accuracy = graphene.String()
    end_accuracy = graphene.String()
    is_momentary = graphene.Boolean()
    url = graphene.String()
    affiliate = graphene.String()
    is_private = graphene.Boolean()
    is_exclusive = graphene.Boolean()
    posted_by = graphene.Field(UserType)
    last_modified_by = graphene.Field(UserType)
    created_at = graphene.String()

    class Arguments:
        id = graphene.String()
        name = graphene.String()
        image_path = graphene.String()
        description = graphene.String()
        start = graphene.String()
        end = graphene.String()
        start_accuracy = graphene.String()
        end_accuracy = graphene.String()
        is_momentary = graphene.Boolean()
        url = graphene.String()
        affiliate = graphene.String()
        is_private = graphene.Boolean()
        is_exclusive = graphene.Boolean()
        quark_type_id = graphene.Int()

    def mutate(self, info, id, name, image_path, description, start, end, start_accuracy, end_accuracy,
               is_momentary, url, affiliate, is_private, is_exclusive, quark_type_id):

        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError('You must be logged in!')

        quark_type = QuarkType.objects.filter(id=quark_type_id).first()
        if not quark_type:
            raise Exception('Invalid QuarkType!')

        if len(start) == 0:
            start = None

        if len(end) == 0:
            end = None

        target_quark = Quark.objects.filter(id=id)
        if not target_quark:
            raise Exception('Invalid Quark!')

        if not user.is_superuser and user.id != target_quark.first().posted_by.id and target_quark.first().is_exclusive:
            raise Exception('You are not authorized')

        target_quark.update(
            quark_type=quark_type,
            name=name,
            image_path=image_path,
            description=description,
            start=start,
            end=end,
            start_accuracy=start_accuracy,
            end_accuracy=end_accuracy,
            is_momentary=is_momentary,
            url=url,
            affiliate=affiliate,
            is_private=is_private,
            is_exclusive=is_exclusive,
            last_modified_by=user,
        )

        return UpdateQuark(id=id, quark_type=quark_type, name=name, image_path=image_path, description=description,
                           start=start, end=end, start_accuracy=start_accuracy, end_accuracy=end_accuracy,
                           is_momentary=is_momentary, url=url, affiliate=affiliate, is_private=is_private,
                           is_exclusive=is_exclusive, posted_by=user, last_modified_by=user)


class DeleteQuark(graphene.Mutation):
    id = graphene.String()
    name = graphene.String()
    image_path = graphene.String()
    description = graphene.String()
    is_exclusive = graphene.Boolean()
    posted_by = graphene.Field(UserType)
    created_at = graphene.String()

    class Arguments:
        id = graphene.String()

    def mutate(self, info, id):

        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError('You must be logged in!')

        target_quark = Quark.objects.get(id=id)
        if not target_quark:
            raise Exception('Invalid Quark!')

        if not user.is_superuser and user.id != target_quark.posted_by.id and target_quark.is_exclusive:
            raise Exception('You are not authorized')

        target_quark.delete()

        return target_quark

class Mutation(graphene.ObjectType):
    create_quark = CreateQuark.Field()
    update_quark = UpdateQuark.Field()
    delete_quark = DeleteQuark.Field()
