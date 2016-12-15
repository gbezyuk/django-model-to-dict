from django.db import models
from django_model_to_dict.mixins import ToDictMixin
from django.utils.translation import ugettext_lazy as _


class DegenerateModel(models.Model, ToDictMixin):
    """This model is not suitable for pretty much anything"""

    class Meta:
        verbose_name = _('Degenerate Model')
        verbose_name_plural = _('Degenerate Models')


class DegenerateTimestampedModel(models.Model, ToDictMixin):
    """This model is not suitable for pretty much anything"""

    class Meta:
        verbose_name = _('Degenerate Model')
        verbose_name_plural = _('Degenerate Models')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    TO_DICT_SKIP = ('created_at', 'updated_at')


class DeliveryRecord(models.Model, ToDictMixin):
    """This model contains delivery information"""

    class Meta:
        verbose_name = _('Delivery Record')
        verbose_name_plural = _('Delivery Records')

    # these fields are supposed to be grouped under 'address' via prefix, see TO_DICT_PREFIXES
    address_country = models.CharField(max_length=100, verbose_name=_('address country'))
    address_state = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('address state'))
    address_city = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('address city'))
    address_street = models.TextField(verbose_name=_('address street'))

    TO_DICT_PREFIXES = ('address_',)


class ContactPerson(models.Model, ToDictMixin):
    """This model contains contact information"""

    class Meta:
        verbose_name = _('Contact')
        verbose_name_plural = _('Contact')

    name = models.CharField(max_length=100, verbose_name=_('name'))

    # these fields are supposed to be grouped under 'contacts', see TO_DICT_GROUPING
    tel = models.CharField(max_length=30, verbose_name=_('tel'))
    email = models.EmailField(max_length=30, verbose_name=_('email'))
    website = models.URLField(max_length=100, blank=True, null=True, verbose_name=_('website'))

    TO_DICT_GROUPING = {'contacts': ('tel', 'email', 'website')}


class Person(models.Model, ToDictMixin):
    """This model contains personal information"""

    class Meta:
        verbose_name = _('Person')
        verbose_name_plural = _('People')

    # these fields are supposed to be grouped under 'name' with 'first', 'middle' and 'last' keys, see TO_DICT_POSTFIXES
    first_name = models.CharField(max_length=100, verbose_name=_('first name'))
    middle_name = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('middle name'))
    last_name = models.CharField(max_length=100, verbose_name=_('last name'))

    TO_DICT_POSTFIXES = ('_name',)


class Customer(models.Model, ToDictMixin):
    """This model is suitable for storing information on both superheroes and ordinary people"""

    class Meta:
        verbose_name = _('Customer')
        verbose_name_plural = _('Customers')

    # these fields are supposed to be grouped under 'name' with 'first', 'middle' and 'last' keys, see TO_DICT_POSTFIXES
    first_name = models.CharField(max_length=100, verbose_name=_('first name'))
    middle_name = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('middle name'))
    last_name = models.CharField(max_length=100, verbose_name=_('last name'))

    # these are just normal fields not affected by any TO_DICT setup
    nickname = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('nickname'))
    has_superpowers = models.BooleanField(default=False, verbose_name=_('has superpowers'))

    # supposed to be grouped under 'contacts', see TO_DICT_GROUPING
    tel = models.CharField(max_length=30, verbose_name=_('tel'))
    email = models.EmailField(max_length=30, verbose_name=_('email'))
    website = models.URLField(max_length=100, verbose_name=_('website'))

    # supposed to be grouped under 'address' via prefix, see TO_DICT_PREFIXES
    address_country = models.CharField(max_length=100, verbose_name=_('address country'))
    address_state = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('address state'))
    address_city = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('address city'))
    address_street = models.TextField(verbose_name=_('address street'))

    # supposed to be skipped during serialization, as well as the 'id' auto-field
    actually_exists = models.BooleanField(default=True, verbose_name=_('actually exists'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # TO_DICT_* local model settings (will override values from project-level settings.py)
    TO_DICT_SKIP = ('id', 'created_at', 'updated_at', 'actually_exists')
    TO_DICT_GROUPING = {
        'contacts': ('tel', 'email', 'website')
    }
    TO_DICT_PREFIXES = ('address_',)
    TO_DICT_POSTFIXES = ('_name',)


class Product(models.Model, ToDictMixin):
    """This model describes a product"""

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Product')

    name = models.CharField(max_length=100, verbose_name=_('name'))
    price = models.PositiveIntegerField(verbose_name=_('price'))


class Order(models.Model, ToDictMixin):
    """This model reflects an order in a shop"""

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

    customer = models.ForeignKey(to=Customer, verbose_name=_('customer'), related_name='orders')


class OrderPosition(models.Model, ToDictMixin):
    """This model reflects a single order position"""

    class Meta:
        verbose_name = _('Order Position')
        verbose_name_plural = _('Order Positions')

    price = models.PositiveIntegerField(verbose_name=_('price'))
    quantity = models.PositiveIntegerField(verbose_name=_('quantity'))
    product = models.ForeignKey(to=Product, verbose_name=_('product'), related_name='order_positions')
    order = models.ForeignKey(to=Order, verbose_name=_('order'), related_name='order_positions')