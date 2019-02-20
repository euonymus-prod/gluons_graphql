import graphene
from graphene_django import DjangoObjectType

from users.schema import UserType

from graphql_api.models import Quark, QuarkType, Gluon, GluonType, QuarkProperty, QtypeProperty, QpropertyGtype, QpropertyType

from graphql import GraphQLError
from django.db.models import Q



class GluonModelType(DjangoObjectType):
    class Meta:
        model = Gluon

    target = graphene.Field(
        # QuarkModelType has to be lambda, because it's recursively called
        # https://github.com/graphql-python/graphene-django/issues/52
        lambda: QuarkModelType
    )

    def resolve_target(self, info, **kwargs):
        if self.subject_qid == self.subject_quark_id:
            target_id = self.object_quark_id
        else:
            target_id = self.subject_quark_id

        return Quark.objects.get(id=target_id)


class GluonTypeType(DjangoObjectType):
    class Meta:
        model = GluonType

class QpropertyGtypeType(DjangoObjectType):
    class Meta:
        model = QpropertyGtype

class QuarkPropertyType(DjangoObjectType):
    class Meta:
        model = QuarkProperty

    targets = graphene.List(
        GluonModelType,
        first=graphene.Int(),
        skip=graphene.Int(),
        orderBy=graphene.String(),
    )

    def resolve_targets(self, info, first=None, skip=None, **kwargs):
        # prepare target gluon_types
        qprop_gtypes = QpropertyGtype.objects.all()
        filter_qprop_gtype = (
            Q(quark_property_id__exact=self.id)
        )
        qprop_gtypes = qprop_gtypes.filter(filter_qprop_gtype)

        # The value sent with the search parameter will be in the args variable
        orderBy = kwargs.get("orderBy", None)
        if orderBy:
            from django.db.models import F
            qs = Gluon.objects.order_by(F(orderBy).desc(nulls_last=True))
        else:
            qs = Gluon.objects.all()

        for gtype in qprop_gtypes:
            if (gtype.side == 0):
                filter_original = (
                    Q(subject_quark_id__exact=self.subject_qid) | Q(object_quark_id__exact=self.subject_qid)
                )
            elif (gtype.side == 1):
                filter_original = (
                    Q(subject_quark_id__exact=self.subject_qid)
                )
            elif (gtype.side == 2):
                filter_original = (
                    Q(object_quark_id__exact=self.subject_qid)
                )

            if 'filter' in locals():
                filter = ( filter | (Q(gluon_type_id__exact=gtype.gluon_type_id) & filter_original) )
            else:
                filter = (
                    Q(gluon_type_id__exact=gtype.gluon_type_id) & filter_original
                )

        if 'filter' in locals():
            qs = qs.filter(filter)
        else:
            return []

        if skip:
            qs = qs[skip:]

        if first:
            qs = qs[:first]

        if hasattr(self, 'subject_qid'):
            for item in qs:
                item.subject_qid = self.subject_qid

        return qs


class QtypePropertyType(DjangoObjectType):
    class Meta:
        model = QtypeProperty

    quark_property = graphene.Field(
        QuarkPropertyType,
        id=graphene.String(),
    )

    def resolve_quark_property(self, info, id=None, **kwargs):
        qs = QuarkProperty.objects.get(id=self.quark_property_id)
        if hasattr(self, 'subject_qid'):
            qs.subject_qid = self.subject_qid
        return qs

class QuarkTypeType(DjangoObjectType):
    class Meta:
        model = QuarkType

    having_quark_properties = graphene.List(
        QtypePropertyType,
    )

    def resolve_having_quark_properties(self, info, **kwargs):
        qs = QtypeProperty.objects.all()
        filter = (
            Q(quark_type_id__exact=self.id)
        )
        qs = qs.filter(filter)

        if hasattr(self, 'subject_qid'):
            for item in qs:
                item.subject_qid = self.subject_qid

        return qs


class QuarkModelType(DjangoObjectType):
    class Meta:
        model = Quark

    quark_type = graphene.Field(
        QuarkTypeType,
        id=graphene.String(),
    )
    relatives = graphene.List(
        GluonModelType,
        first=graphene.Int(),
        skip=graphene.Int(),
        orderBy=graphene.String(),
    )

    def resolve_quark_type(self, info, id=None, **kwargs):
        qs = QuarkType.objects.get(id=self.quark_type_id)
        qs.subject_qid = self.id
        return qs

    def resolve_relatives(self, info, first=None, skip=None, **kwargs):
        # Avoiding gluon_type Preparation
        qs_props = QtypeProperty.objects.all().filter((Q(quark_type_id__exact=self.quark_type_id)))
        q_properties = []
        for qproperty in qs_props:
            q_properties.append(qproperty.quark_property_id)

        qs_gtype = QpropertyGtype.objects.all().filter((Q(quark_property_id__in=q_properties)))
        g_types = []
        for gtype in qs_gtype:
            g_types.append(gtype.gluon_type_id)

        # Start Retrieving
        orderBy = kwargs.get("orderBy", None)
        if orderBy:
            # qs = Gluon.objects.order_by(orderBy).reverse()
            qs = Gluon.objects.order_by(F(orderBy).desc(nulls_last=True))
        else:
            qs = Gluon.objects.all()

        filter = (
            Q(subject_quark_id__exact=self.id) | Q(object_quark_id__exact=self.id)
        )
        qs = qs.filter(filter).exclude(gluon_type__in=g_types)

        if skip:
            qs = qs[skip:]

        if first:
            qs = qs[:first]

        for item in qs:
            # item.side = self.side
            item.subject_qid = self.id

        return qs
        

class QpropertyTypeType(DjangoObjectType):
    class Meta:
        model = QpropertyType





quark = graphene.Field(
    QuarkModelType,
    id=graphene.String(),
    name=graphene.String()
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

quark_types = graphene.List(
    QuarkTypeType,
    orderBy=graphene.String(),
)

gluon_types = graphene.List(
    GluonTypeType,
    orderBy=graphene.String(),
)

quark_properties = graphene.List(
    QuarkPropertyType,
    orderBy=graphene.String(),
)

qtype_properties = graphene.List(
    QtypePropertyType,
    quarkTypeId=graphene.Int(),
    orderBy=graphene.String()
)

qproperty_gtypes = graphene.List(
    QpropertyGtypeType,
    orderBy=graphene.String(),
)

qproperty_types = graphene.List(
    QpropertyTypeType,
    orderBy=graphene.String(),
)



class Query(graphene.ObjectType):
    quark = quark
    quarks = quarks
    quark_count = quark_count
    gluon = gluon
    gluons = gluons
    gluon_count = gluon_count
    quark_types = quark_types
    gluon_types = gluon_types
    quark_properties = quark_properties
    qtype_properties = qtype_properties
    qproperty_gtypes = qproperty_gtypes
    qproperty_types = qproperty_types

    def resolve_quark(self, info, id=None, name=None, **kwargs):
        if (id is None) and (name is not None):
            qs = Quark.objects.all()
            filter = (
                Q(name__exact=name)
            )
            return qs.filter(filter).first()

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
                Q(name__icontains=search) |
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
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
            qs = qs.filter(filter)

        return qs.count()

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

    def resolve_quark_types(self, info, **kwargs):
        # The value sent with the search parameter will be in the args variable
        orderBy = kwargs.get("orderBy", None)
        if orderBy:
            # qs = QuarkType.objects.order_by(orderBy).reverse()
            qs = QuarkType.objects.order_by(orderBy)
        else:
            qs = QuarkType.objects.all()

        return qs

    def resolve_gluon_types(self, info, **kwargs):
        # The value sent with the search parameter will be in the args variable
        orderBy = kwargs.get("orderBy", None)
        if orderBy:
            # qs = GluonType.objects.order_by(orderBy).reverse()
            qs = GluonType.objects.order_by(orderBy)
        else:
            qs = GluonType.objects.all()

        return qs


    def resolve_quark_properties(self, info, **kwargs):
        # The value sent with the search parameter will be in the args variable
        orderBy = kwargs.get("orderBy", None)
        if orderBy:
            # qs = QuarkProperty.objects.order_by(orderBy).reverse()
            qs = QuarkProperty.objects.order_by(orderBy)
        else:
            qs = QuarkProperty.objects.all()

        return qs

    def resolve_qtype_properties(self, info, quarkTypeId=None, **kwargs):
        # The value sent with the search parameter will be in the args variable
        orderBy = kwargs.get("orderBy", None)
        if orderBy:
            # qs = QtypeProperty.objects.order_by(orderBy).reverse()
            qs = QtypeProperty.objects.order_by(orderBy)
        else:
            qs = QtypeProperty.objects.all()

        if quarkTypeId:
            filter = (
                Q(quark_type_id__exact=quarkTypeId)
            )
            qs = qs.filter(filter)

        return qs


    def resolve_qproperty_gtypes(self, info, **kwargs):
        # The value sent with the search parameter will be in the args variable
        orderBy = kwargs.get("orderBy", None)
        if orderBy:
            # qs = QpropertyGtype.objects.order_by(orderBy).reverse()
            qs = QpropertyGtype.objects.order_by(orderBy)
        else:
            qs = QpropertyGtype.objects.all()

        return qs

    def resolve_qproperty_types(self, info, **kwargs):
        # The value sent with the search parameter will be in the args variable
        orderBy = kwargs.get("orderBy", None)
        if orderBy:
            # qs = QpropertyType.objects.order_by(orderBy).reverse()
            qs = QpropertyType.objects.order_by(orderBy)
        else:
            qs = QpropertyType.objects.all()

        return qs

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
            raise GraphQLError('You must be logged in!')

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
    
class CreateGluonType(graphene.Mutation):
    id = graphene.Int()
    name = graphene.String()
    caption = graphene.String()
    caption_ja = graphene.String()
    sort = graphene.Int()
    created_at = graphene.String()
    user = graphene.Field(UserType)

    class Arguments:
        name = graphene.String()
        caption = graphene.String()
        caption_ja = graphene.String()
        sort = graphene.Int()

    def mutate(self, info, name, caption, caption_ja, sort):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError('You must be logged in!')

        gluon_type = GluonType(
            name=name,
            caption=caption,
            caption_ja=caption_ja,
            sort=sort,
        )
        gluon_type.save()

        return CreateGluonType(
            id=gluon_type.id,
            name=gluon_type.name,
            caption=gluon_type.caption,
            caption_ja=gluon_type.caption_ja,
            sort=gluon_type.sort,
            created_at=gluon_type.created_at,
        )
    
class CreateQuarkProperty(graphene.Mutation):
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
            raise GraphQLError('You must be logged in!')

        quark_property = QuarkProperty(
            name=name,
            caption=caption,
            caption_ja=caption_ja,
        )
        quark_property.save()

        return CreateQuarkProperty(
            id=quark_property.id,
            name=quark_property.name,
            caption=quark_property.caption,
            caption_ja=quark_property.caption_ja,
            created_at=quark_property.created_at,
        )
    

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
            raise GraphQLError('You must be logged in!')

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
    create_quark = CreateQuark.Field()
    update_quark = UpdateQuark.Field()
    delete_quark = DeleteQuark.Field()

    create_gluon = CreateGluon.Field()
    # update_gluon = UpdateGluon.Field()
    # delete_gluon = DeleteGluon.Field()

    create_quark_type = CreateQuarkType.Field()

    create_gluon_type = CreateGluonType.Field()

    create_quark_property = CreateQuarkProperty.Field()

    create_qtype_property = CreateQtypeProperty.Field()
    
    create_qproperty_gtype = CreateQpropertyGtype.Field()

    create_qproperty_type = CreateQpropertyType.Field()
