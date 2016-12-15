from django.test import TestCase
from .models import DegenerateModel, DegenerateTimestampedModel,\
    ContactPerson, DeliveryRecord, Person,\
    Customer, Product, Order, OrderPosition


class DegenerateTestCase(TestCase):
    def setUp(self):
        DegenerateModel.objects.create()

    def test_degenerate_model_to_dict(self):
        """This test tests the simplest case"""
        degenerate_model_instance = DegenerateModel.objects.get()
        self.assertEqual(degenerate_model_instance.to_dict(), {
            'id': degenerate_model_instance.id,
        })


class DegenerateTimestampedModelTestCase(TestCase):
    def setUp(self):
        DegenerateTimestampedModel.objects.create()

    def test_degenerate_model_to_dict(self):
        """This test tests skipping fields"""
        degenerate_timestamped_model_instance = DegenerateTimestampedModel.objects.get()
        self.assertEqual(degenerate_timestamped_model_instance.to_dict(), {
            'id': degenerate_timestamped_model_instance.id,
        })


class ContactTestCase(TestCase):
    def setUp(self):
        ContactPerson.objects.create(name="Name", tel="555-55-55", email="name@example.com")

    def test_contact_to_dict(self):
        """This test tests manual field grouping"""
        contact_person = ContactPerson.objects.get()

        self.assertEqual(contact_person.to_dict(), {
            'id': contact_person.id,
            'name': contact_person.name,
            'contacts': {
                'tel': contact_person.tel,
                'email': contact_person.email
            },
        })

        self.assertEqual(contact_person.to_dict(compress_groups=False), {
            'id': contact_person.id,
            'name': contact_person.name,
            'contacts': {
                'tel': contact_person.tel,
                'email': contact_person.email,
                'website': None
            },
        })


class DeliveryRecordTestCase(TestCase):
    def setUp(self):
        DeliveryRecord.objects.create(address_country="Russia", address_city="Moscow", address_street="Red Square")

    def test_delivery_to_dict(self):
        """This test tests prefix field grouping"""

        delivery = DeliveryRecord.objects.get()

        self.assertEqual(delivery.to_dict(), {
            'id': delivery.id,
            'address': {
                'country': delivery.address_country,
                'city': delivery.address_city,
                'street': delivery.address_street,
            }
        })

        self.assertEqual(delivery.to_dict(compress_prefixes=False), {
            'id': delivery.id,
            'address': {
                'country': delivery.address_country,
                'state': None,
                'city': delivery.address_city,
                'street': delivery.address_street
            }
        })


class PersonTestCase(TestCase):
    def setUp(self):
        Person.objects.create(first_name="Ivo", last_name="Bobul")

    def test_person_to_dict(self):
        """This test tests postfix field grouping"""

        person = Person.objects.get()

        self.assertEqual(person.to_dict(), {
            'id': person.id,
            'name': {
                'first': person.first_name,
                'last': person.last_name,
            }
        })

        self.assertEqual(person.to_dict(compress_postfixes=False), {
            'id': person.id,
            'name': {
                'first': person.first_name,
                'middle': None,
                'last': person.last_name,
            }
        })


class CustomerTestCase(TestCase):
    def setUp(self):
        Customer.objects.create(first_name="Ivo", nickname="Super", last_name="Bobul", middle_name="Tarasovich",
                              actually_exists=False, has_superpowers=True,
                              tel="333-55-55", email="super.ivo@bobul.com", website="https://super.ivo.bobul.com",
                              address_country="Ukraine", address_city="Kiev", address_street="Tarasa Shevchenko")

    def test_customer_to_dict(self):
        """This test tests both prefix and manual field grouping, as well as field skipping"""

        customer = Customer.objects.get()

        self.assertEqual(customer.to_dict(inspect_related_objects=False), {
            'name': {
                'first': customer.first_name,
                'middle': customer.middle_name,
                'last': customer.last_name,
            },
            'nickname': customer.nickname,
            'has_superpowers': customer.has_superpowers,
            'contacts': {
                'tel': customer.tel,
                'email': customer.email,
                'website': customer.website
            },
            'address': {
                'country': customer.address_country,
                'city': customer.address_city,
                'street': customer.address_street
            }
        })


class OrderTestCase(TestCase):
    def setUp(self):
        c = Customer.objects.create(first_name="Ivo", nickname="Super", last_name="Bobul", middle_name="Tarasovich",
                                    actually_exists=False, has_superpowers=True,
                                    tel="333-55-55", email="super.ivo@bobul.com", website="https://super.ivo.bobul.com",
                                    address_country="Ukraine", address_city="Kiev", address_street="Tarasa Shevchenko")

        apple = Product.objects.create(name='Apple', price=10)
        pear = Product.objects.create(name='Pear', price=12)
        tomato = Product.objects.create(name='Tomato', price=9)

        order = Order.objects.create(customer=c)
        OrderPosition.objects.create(order=order, product=apple, price=apple.price, quantity=1)
        OrderPosition.objects.create(order=order, product=pear, price=pear.price, quantity=1)
        OrderPosition.objects.create(order=order, product=tomato, price=tomato.price, quantity=1)

    def test_order_to_dict(self):
        """A complex test for related fields"""

        customer = Customer.objects.get()
        order = Order.objects.get()

        self.assertEqual(order.to_dict(), {
            'customer': {
                'name': {
                    'first': customer.first_name,
                    'middle': customer.middle_name,
                    'last': customer.last_name,
                },
                'nickname': customer.nickname,
                'has_superpowers': customer.has_superpowers,
                'contacts': {
                    'tel': customer.tel,
                    'email': customer.email,
                    'website': customer.website
                },
                'address': {
                    'country': customer.address_country,
                    'city': customer.address_city,
                    'street': customer.address_street
                }
            },
            'id': order.id,
            'order_positions': [
                {'quantity': 1, 'product': 1, 'id': 1, 'order': order.id, 'price': 10},
                {'quantity': 1, 'product': 2, 'id': 2, 'order': order.id, 'price': 12},
                {'quantity': 1, 'product': 3, 'id': 3, 'order': order.id, 'price': 9}
            ]
        })
