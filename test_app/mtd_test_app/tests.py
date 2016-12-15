from django.test import TestCase
from .models import DegenerateModel, DegenerateTimestampedModel, Contact, DeliveryRecord, Person


class DegenerateTestCase(TestCase):
    def setUp(self):
        DegenerateModel.objects.create()

    def test_degenerate_model_to_dict(self):
        """This test tests the simpliest case"""

        degenerate_model_instance = DegenerateModel.objects.get()
        self.assertEqual(degenerate_model_instance.to_dict(), {
            'id': degenerate_model_instance.id
        })


class DegenerateTimestampedModelTestCase(TestCase):
    def setUp(self):
        DegenerateTimestampedModel.objects.create()

    def test_degenerate_model_to_dict(self):
        """This test tests skipping fields"""

        degenerate_model_instance = DegenerateTimestampedModel.objects.get()
        self.assertEqual(degenerate_model_instance.to_dict(), {
            'id': degenerate_model_instance.id
        })


class ContactTestCase(TestCase):
    def setUp(self):
        Contact.objects.create(tel="555-55-55", email="name@example.com", website="http://name.me")

    def test_degenerate_model_to_dict(self):
        """This test tests skipping fields"""

        contact = Contact.objects.get()
        self.assertEqual(contact.to_dict(), {
            'id': contact.id,
            'contacts': {
                'tel': '555-55-55',
                'email': 'name@example.com',
                'website': 'http://name.me'
            },
        })


class DeliveryRecordTestCase(TestCase):
    def setUp(self):
        DeliveryRecord.objects.create(address_country="Russia", address_city="Moscow", address_street="Red Square")

    def test_degenerate_model_to_dict(self):
        """This test tests skipping fields"""

        delivery = DeliveryRecord.objects.get()
        self.assertEqual(delivery.to_dict(), {
            'id': delivery.id,
            'address': {
                'country': 'Russia',
                'city': 'Moscow',
                'street': 'Red Square'
            }
        })


class PersonTestCase(TestCase):
    def setUp(self):
        Person.objects.create(first_name="John", last_name="Doe", actually_exists=True, has_superpowers=False,
                              tel="555-55-11", email="john@example.com", website="http://john.doe.me",
                              address_country="USA", address_state="NY", address_city="New York",
                              address_street="Boulevard of Broken Dreams")
        Person.objects.create(first_name="Ivo", nickname="Super", last_name="Bobul", middle_name="Tarasovich",
                              actually_exists=False, has_superpowers=True,
                              tel="333-55-55", email="super.ivo@bobul.com", website="https://super.ivo.bobul.com",
                              address_country="Ukraine", address_city="Kiev", address_street="Tarasa Shevchenko")

    def test_person_to_dict(self):
        """This test tests both prefix and manual field grouping, as well as field skipping"""

        john = Person.objects.get(first_name="John")
        self.assertEqual(john.to_dict(), {
            'name': {
                'first': 'John',
                'last': 'Doe'
            },
            'has_superpowers': False,
            'contacts': {
                'tel': '555-55-11',
                'email': 'john@example.com',
                'website': 'http://john.doe.me'
            },
            'address': {
                'country': 'USA',
                'state': 'NY',
                'city': 'New York',
                'street': 'Boulevard of Broken Dreams'
            }
        })

        ivo = Person.objects.get(first_name="Ivo")
        self.assertEqual(john.to_dict(), {
            'name': {
                'first': 'Ivo',
                'middle': 'Tarasovich',
                'last': 'Bobul',
            },
            'nickname': 'Super',
            'has_superpowers': False,
            'contacts': {
                'tel': '333-55-55',
                'email': 'super.ivo@bobul.com',
                'website': 'https://super.ivo.bobul.com'
            },
            'address': {
                'country': 'Ukraine',
                'city': 'Kiev',
                'street': 'Tarasa Shevchenko'
            }
        })