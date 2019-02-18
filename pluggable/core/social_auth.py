"""Pluggable ORM models for Social Auth"""

import base64
import random
import six
import sys

from social_core.storage import (
    UserMixin, AssociationMixin, NonceMixin,
    CodeMixin, PartialMixin, BaseStorage)

# Use the system PRNG if possible
try:
    random = random.SystemRandom()
    using_sysrandom = True
except NotImplementedError:
    import warnings
    warnings.warn('A secure pseudo-random number generator is not available '
                  'on your system. Falling back to Mersenne Twister.')
    using_sysrandom = False


def get_random_string(length=12,
                      allowed_chars='abcdefghijklmnopqrstuvwxyz'
                                    'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
    """
    Return a securely generated random string.
    The default length of 12 with the a-z, A-Z, 0-9 character set returns
    a 71-bit value. log_2((26+26+10)^12) =~ 71 bits
    """
    if not using_sysrandom:
        # This is ugly, and a hack, but it makes things better than
        # the alternative of predictability. This re-seeds the PRNG
        # using a value that is hard for an attacker to predict, every
        # time a random string is required. This may change the
        # properties of the chosen random sequence slightly, but this
        # is better than absolute predictability.
        random.seed(
            hashlib.sha256(
                ('%s%s%s' % (random.getstate(), time.time(), settings.SECRET_KEY)).encode()
            ).digest()
        )
    return ''.join(random.choice(allowed_chars) for i in range(length))


class Objects(object):

    def filter (self, user):

        return 'foo'


class PluggableUserMixin(UserMixin):
    """Social Auth association model"""
    
    @classmethod
    def changed(cls, user):
        user.save()

    def set_extra_data(self, extra_data=None):
        if super(PluggableUserMixin, self).set_extra_data(extra_data):
            self.save()

    @classmethod
    def allowed_to_disconnect(cls, user, backend_name, association_id=None):
        if association_id is not None:
            qs = cls.objects.exclude(id=association_id)
        else:
            qs = cls.objects.exclude(provider=backend_name)
        qs = qs.filter(user=user)

        if hasattr(user, 'has_usable_password'):
            valid_password = user.has_usable_password()
        else:
            valid_password = True
        return valid_password or qs.count() > 0

    @classmethod
    def disconnect(cls, entry):
        entry.delete()

    @classmethod
    def username_field(cls):
        return getattr(cls.user_model(), 'USERNAME_FIELD', 'username')

    @classmethod
    def user_exists(cls, *args, **kwargs):
        """
        Return True/False if a User instance exists with the given arguments.
        Arguments are directly passed to filter() manager method.
        """
        if 'username' in kwargs:
            kwargs[cls.username_field()] = kwargs.pop('username')
        return cls.user_model().objects.filter(*args, **kwargs).count() > 0
    
    @classmethod
    def get_username(cls, user):
        return getattr(user, cls.username_field(), None)

    @classmethod
    def create_user(cls, *args, **kwargs):
        username_field = cls.username_field()
        if 'username' in kwargs:
            if username_field not in kwargs:
                kwargs[username_field] = kwargs.pop('username')
            else:
                # If username_field is 'email' and there is no field named "username"
                # then latest should be removed from kwargs.
                try:
                    cls.user_model()._meta.get_field('username')
                except FieldDoesNotExist:
                    kwargs.pop('username')
        try:
            if hasattr(transaction, 'atomic'):
                # In Pluggable versions that have an "atomic" transaction decorator / context
                # manager, there's a transaction wrapped around this call.
                # If the create fails below due to an IntegrityError, ensure that the transaction
                # stays undamaged by wrapping the create in an atomic.
                with transaction.atomic():
                    user = cls.user_model().objects.create_user(*args, **kwargs)
            else:
                user = cls.user_model().objects.create_user(*args, **kwargs)
        except IntegrityError:
            # User might have been created on a different thread, try and find them.
            # If we don't, re-raise the IntegrityError.
            exc_info = sys.exc_info()
            # If email comes in as None it won't get found in the get
            if kwargs.get('email', True) is None:
                kwargs['email'] = ''
            try:
                user = cls.user_model().objects.get(*args, **kwargs)
            except cls.user_model().DoesNotExist:
                six.reraise(*exc_info)
        return user

    @classmethod
    def get_user(cls, pk=None, **kwargs):
        if pk:
            kwargs = {'pk': pk}
        try:
            return cls.user_model().objects.get(**kwargs)
        except cls.user_model().DoesNotExist:
            return None

    @classmethod
    def get_users_by_email(cls, email):
        user_model = cls.user_model()
        email_field = getattr(user_model, 'EMAIL_FIELD', 'email')
        return user_model.objects.filter(**{email_field + '__iexact': email})

    @classmethod
    def get_social_auth(cls, provider, uid):
        if not isinstance(uid, six.string_types):
            uid = str(uid)
        try:
            return cls.objects.get(provider=provider, uid=uid)
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_social_auth_for_user(cls, user, provider=None, id=None):
        # do we have any existing social auths for this user/provider ?
        return []

    @classmethod
    def create_social_auth(cls, user, uid, provider):
        if not isinstance(uid, six.string_types):
            uid = str(uid)
        if hasattr(transaction, 'atomic'):
            # In Pluggable versions that have an "atomic" transaction decorator / context
            # manager, there's a transaction wrapped around this call.
            # If the create fails below due to an IntegrityError, ensure that the transaction
            # stays undamaged by wrapping the create in an atomic.
            with transaction.atomic():
                social_auth = cls.objects.create(user=user, uid=uid, provider=provider)
        else:
            social_auth = cls.objects.create(user=user, uid=uid, provider=provider)
        return social_auth


class PluggableNonceMixin(NonceMixin):
    @classmethod
    def use(cls, server_url, timestamp, salt):
        return cls.objects.get_or_create(server_url=server_url,
                                         timestamp=timestamp,
                                         salt=salt)[1]


class PluggableAssociationMixin(AssociationMixin):
    @classmethod
    def store(cls, server_url, association):
        # Don't use get_or_create because issued cannot be null
        try:
            assoc = cls.objects.get(server_url=server_url,
                                    handle=association.handle)
        except cls.DoesNotExist:
            assoc = cls(server_url=server_url,
                        handle=association.handle)

        try:
            assoc.secret = base64.encodebytes(association.secret).decode()
        except AttributeError:
            assoc.secret = base64.encodestring(association.secret).decode()
        assoc.issued = association.issued
        assoc.lifetime = association.lifetime
        assoc.assoc_type = association.assoc_type
        assoc.save()

    @classmethod
    def get(cls, *args, **kwargs):
        return cls.objects.filter(*args, **kwargs)

    @classmethod
    def remove(cls, ids_to_delete):
        cls.objects.filter(pk__in=ids_to_delete).delete()


class PluggableCodeMixin(CodeMixin):
    @classmethod
    def get_code(cls, code):
        try:
            return cls.objects.get(code=code)
        except cls.DoesNotExist:
            return None


class PluggablePartialMixin(PartialMixin):
    @classmethod
    def load(cls, token):
        try:
            return cls.objects.get(token=token)
        except cls.DoesNotExist:
            return None

    @classmethod
    def destroy(cls, token):
        partial = cls.load(token)
        if partial:
            partial.delete()


class Code(PluggableCodeMixin):
    #email = models.EmailField(max_length=EMAIL_LENGTH)
    #code = models.CharField(max_length=32, db_index=True)
    #verified = models.BooleanField(default=False)
    #timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        app_label = "social_pluggable"
        db_table = 'social_auth_code'
        unique_together = ('email', 'code')


class Partial(PluggablePartialMixin):
    #token = models.CharField(max_length=32, db_index=True)
    #next_step = models.PositiveSmallIntegerField(default=0)
    #backend = models.CharField(max_length=32)
    #data = JSONField()
    #timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        app_label = "social_django"
        db_table = 'social_auth_partial'


class Association(PluggableAssociationMixin):
    """OpenId account association"""
    #server_url = models.CharField(max_length=ASSOCIATION_SERVER_URL_LENGTH)
    #handle = models.CharField(max_length=ASSOCIATION_HANDLE_LENGTH)
    #secret = models.CharField(max_length=255)  # Stored base64 encoded
    #issued = models.IntegerField()
    #lifetime = models.IntegerField()
    #assoc_type = models.CharField(max_length=64)

    class Meta:
        app_label = "social_django"
        db_table = 'social_auth_association'
        unique_together = (
            ('server_url', 'handle',)
)


class BasePluggableStorage(BaseStorage):
    user = PluggableUserMixin
    nonce = PluggableNonceMixin
    association = PluggableAssociationMixin
    code = PluggableCodeMixin


class Nonce(PluggableNonceMixin):
    """One use numbers"""
    #server_url = models.CharField(max_length=NONCE_SERVER_URL_LENGTH)
    #timestamp = models.IntegerField()
    #salt = models.CharField(max_length=65)

    class Meta:
        app_label = "social_django"
        unique_together = ('server_url', 'timestamp', 'salt')
        db_table = 'social_auth_nonce'


class AbstractUserSocialAuth(PluggableUserMixin):
    """Abstract Social Auth association model"""
    #user = models.ForeignKey(USER_MODEL, related_name='social_auth',
    #                         on_delete=models.CASCADE)
    #provider = models.CharField(max_length=32)
    #uid = models.CharField(max_length=UID_LENGTH)
    #extra_data = JSONField()
    #objects = UserSocialAuthManager()

    def __str__(self):
        return str(self.user)

    class Meta:
        app_label = "social_django"
        abstract = True

    @classmethod
    def get_social_auth(cls, provider, uid):
        import pdb; pdb.set_trace()
        
        try:
            return cls.objects.select_related('user').get(provider=provider,
                                                          uid=uid)
        except cls.DoesNotExist:
            return None

    @classmethod
    def username_max_length(cls):
        username_field = cls.username_field()
        field = cls.user_model()._meta.get_field(username_field)
        return field.max_length

    @classmethod
    def user_model(cls):
        user_model = get_rel_model(field=cls._meta.get_field('user'))
        return user_model


class UserSocialAuth(AbstractUserSocialAuth):
    """Social Auth association model"""

    class Meta:
        """Meta data"""
        app_label = "social_django"
        unique_together = ('provider', 'uid')
        db_table = 'social_auth_usersocialauth'



class PluggableStorage(BasePluggableStorage):
    user = UserSocialAuth
    nonce = Nonce
    association = Association
    code = Code
    partial = Partial

    @classmethod
    def is_integrity_error(cls, exception):
        return exception.__class__ is IntegrityError

from social_core.strategy import BaseStrategy, BaseTemplateStrategy


class PluggableTemplateStrategy(BaseTemplateStrategy):
    def render_template(self, tpl, context):
        template = loader.get_template(tpl)
        return template.render(context=context, request=self.strategy.request)

    def render_string(self, html, context):
        return render_template_string(self.strategy.request, html, context)


class PluggableStrategy(BaseStrategy):
    DEFAULT_TEMPLATE_STRATEGY = PluggableTemplateStrategy

    def __init__(self, storage, request=None, tpl=None):
        self.request = request
        self.session = request.session if request else {}
        super(PluggableStrategy, self).__init__(storage, tpl)

    def get_setting(self, name):
        # get social auth settings
        print('get setting: %s' % name)
        
        settings = dict(
            SOCIAL_AUTH_REDIRECT_IS_HTTPS=False,
            SOCIAL_AUTH_TWITTER_FIELDS_STORED_IN_SESSION=[],
            SOCIAL_AUTH_TWITTER_REQUEST_TOKEN_EXTRA_ARGUMENTS={},
            SOCIAL_AUTH_TWITTER_SCOPE=[],
            SOCIAL_AUTH_TWITTER_IGNORE_DEFAULT_SCOPE=False,
            SOCIAL_AUTH_TWITTER_SECRET='liYZ1TUgxWyOS9ii5QC54ORDkx4KMszea4841PFqVn7o0MWZZj',
            # '1078057220246511618-PKOSPdRxj0Md9SlDOnp5KhYyBDtM7I', #
            SOCIAL_AUTH_TWITTER_KEY='uPC1SXYV8KIKvaIVXQwK1WXIm',
            SOCIAL_AUTH_TWITTER_VERIFY_SSL={},
            SOCIAL_AUTH_TWITTER_REQUESTS_TIMEOUT=1000,
            SOCIAL_AUTH_TWITTER_URLOPEN_TIMEOUT=1000,
            SOCIAL_AUTH_TWITTER_AUTH_EXTRA_ARGUMENTS={})
        # 'VGwgXYB7sNN4lxj25mitWXxY4FmppEcKnHhfeNbz1U082')  # 
        return settings.get(name)

    def request_data(self, merge=True):
        if not self.request:
            return {}
        if merge:
            data = self.request.GET.copy()
            data.update(self.request.POST)
        elif self.request.method == 'POST':
            data = self.request.POST
        else:
            data = self.request.GET
        return data

    def request_host(self):
        if self.request:
            return self.request.get_host()

    def request_is_secure(self):
        """Is the request using HTTPS?"""
        return self.request.is_secure()

    def request_path(self):
        """path of the current request"""
        return self.request.path

    def request_port(self):
        """Port in use for this request"""
        return get_request_port(request=self.request)

    def request_get(self):
        """Request GET data"""
        return self.request.GET.copy()

    def request_post(self):
        """Request POST data"""
        return self.request.POST.copy()

    def redirect(self, url):
        return url

    def html(self, content):
        return HttpResponse(content, content_type='text/html;charset=UTF-8')

    def render_html(self, tpl=None, html=None, context=None):
        if not tpl and not html:
            raise ValueError('Missing template or html parameters')
        context = context or {}
        try:
            template = loader.get_template(tpl)
            return template.render(context=context, request=self.request)
        except TemplateDoesNotExist:
            return render_template_string(self.request, html, context)

    def authenticate(self, backend, *args, **kwargs):
        kwargs['strategy'] = self
        kwargs['storage'] = self.storage
        kwargs['backend'] = backend
        return authenticate(*args, **kwargs)

    def clean_authenticate_args(self, *args, **kwargs):
        """Cleanup request argument if present, which is passed to
        authenticate as for Pluggable 1.11"""
        if len(args) > 0 and isinstance(args[0], HttpRequest):
            kwargs['request'], args = args[0], args[1:]
        return args, kwargs

    def session_get(self, name, default=None):
        return self.session.get(name, default)

    def session_set(self, name, value):
        self.session[name] = value
        if hasattr(self.session, 'modified'):
            self.session.modified = True

    def session_pop(self, name):
        return self.session.pop(name, None)

    def session_setdefault(self, name, value):
        return self.session.setdefault(name, value)

    def build_absolute_uri(self, path=None):
        if self.request:
            return self.request.build_absolute_uri(path)
        else:
            return path

    def random_string(self, length=12, chars=BaseStrategy.ALLOWED_CHARS):
        return get_random_string(length, chars)

    def to_session_value(self, val):
        """Converts values that are instance of Model to a dictionary
        with enough information to retrieve the instance back later."""
        if isinstance(val, Model):
            val = {
                'pk': val.pk,
                'ctype': ContentType.objects.get_for_model(val).pk
            }
        return val

    def from_session_value(self, val):
        """Converts back the instance saved by self._ctype function."""
        if isinstance(val, dict) and 'pk' in val and 'ctype' in val:
            ctype = ContentType.objects.get_for_id(val['ctype'])
            ModelClass = ctype.model_class()
            val = ModelClass.objects.get(pk=val['pk'])
        return val

    def get_language(self):
        """Return current language"""
        return get_language()    
