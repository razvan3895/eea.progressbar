""" Widget views
"""
import logging
from zope.i18n import translate
from zope.i18nmessageid.message import Message
from zope.component import queryAdapter
from Products.Five.browser import BrowserView
from eea.progressbar.interfaces import IStorage
logger = logging.getLogger('eea.progressbar')

class ViewForm(BrowserView):
    """ Basic widget view
    """
    def __init__(self, context, request, field=None):
        super(ViewForm, self).__init__(context, request)
        self.parent = self.context.getParentNode()
        self.field = field
        self.prefix = u''
        self._custom = None
        self._ready = None

    def setPrefix(self, prefix):
        """ Prefix
        """
        self.prefix = prefix

    def default(self, name):
        """ Default value
        """
        return u''

    @property
    def custom(self):
        """ Is customized
        """
        if self._custom is None:
            storage = queryAdapter(self.parent, IStorage)
            field = storage.field(self.prefix, {})
            value = field.get('states', None)
            if value is not None:
                self._custom = True
            else:
                self._custom = False
        return self._custom

    def ready(self, context=None):
        """ Is ready
        """
        if self._ready is None:
            if not context:
                context = self.context
            field = context.getField(self.prefix)
            value = field.getAccessor(context)()
            if value in (u'', None, (), []):
                self._ready = False
            else:
                self._ready = True
        return self._ready

    def get(self, name, default=''):
        """ Get widget value for name
        """
        storage = queryAdapter(self.parent, IStorage)
        field = storage.field(self.prefix, {})
        value = field.get(name, self.default(name))

        if isinstance(value, (str, unicode)):
            widget = getattr(self.field, 'widget', None)
            label = getattr(widget, 'label', '')
            label = self.translate(label)
            value = value.format(
                label=label,
                context=self.context,
                field=self.field,
                widget=getattr(self.field, 'widget', None)
            )

        return value if value else default

    def translate(self, message):
        """ Use zope.i18n to translate message
        """
        if not message:
            return ''
        elif isinstance(message, Message):
            # message is an i18n message
            return translate(message, context=self.request)
        else:
            # message is a simple msgid
            for domain in ['eea', 'plone']:
                if isinstance(message, str):
                    try:
                        message = message.decode('utf-8')
                    except Exception, err:
                        logger.exception(err)
                        continue

                value = translate(message, domain=domain, context=self.request)
                if value != message:
                    return value
            else:
                return message

    def __call__(self, *args, **kwargs):
        form = self.request.form
        form.update(kwargs)

        prefix = form.get('prefix', None)
        if prefix:
            self.prefix = prefix
            self.label = prefix

        label = form.get('label', None)
        if label:
            self.label = label

        ready = form.get('ready', None)
        if ready is not None:
            self._ready = ready

        return self.template()