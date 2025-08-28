# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions
# and limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel
"""

import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db, DataValidationError
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(
            name="Fedora",
            description="A red hat",
            price=12.50,
            available=True,
            category=Category.CLOTHS,
        )
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertIsNone(product.id)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertTrue(product.available)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)

        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        # Ensure Decimal comparison is type-safe
        self.assertEqual(
            Decimal(str(new_product.price)), Decimal(str(product.price))
        )
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    def test_read_a_product(self):
        """It should Read a Product"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)

        found_product = Product.find(product.id)
        self.assertEqual(found_product.id, product.id)
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.description, product.description)
        self.assertEqual(found_product.price, product.price)

    def test_update_a_product(self):
        """It should Update a Product"""
        product = ProductFactory()
        # Set the ID of the product object to None and then call the create() method on the product.
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        # Log the product object again after it has been created to verify that the product was created with the desired properties.
        # Assert that the ID of the product object is not None after calling the create() method.
        self.assertIsNotNone(product.id)
        # Update the product in the system with the new property values using the update() method.
        product.description = "testing"
        original_id = product.id
        product.update()
        # Assert that the id is same as the original id but description property of the product object has been updated correctly after calling the update() method.
        self.assertEqual(product.id, original_id)
        self.assertEqual(product.description, "testing")
        # Fetch all the product back from the system.
        products = Product.all()
        # Assert the length of the products list is equal to 1 to verify that after updating the product, there is only one product in the system.
        self.assertEqual(len(products), 1)
        # Assert that the fetched product has id same as the original id.
        self.assertEqual(products[0].id, original_id)
        # Assert that the fetched product has the updated description.
        self.assertEqual(products[0].description, "testing")

    def test_update_without_id(self):
        """It should raise DataValidationError if update called without id"""
        product = Product(name="Test", description="No ID", price=10, available=True, category=Category.FOOD)
        with self.assertRaises(DataValidationError):
            product.update()
    
    def test_deserialize_with_invalid_available_type(self):
        """It should raise error on invalid available type"""
        data = {
            "name": "Test",
            "description": "Invalid available",
            "price": "10",
            "available": "yes",   # sai, phải là bool
            "category": "FOOD"
        }
        product = Product()
        with self.assertRaises(DataValidationError):
            product.deserialize(data)

    def test_deserialize_missing_field(self):
        """It should raise error on missing field"""
        data = {
            "description": "Missing name",
            "price": "10",
            "available": True,
            "category": "FOOD"
        }
        product = Product()
        with self.assertRaises(DataValidationError):
            product.deserialize(data)

    def test_deserialize_with_invalid_category(self):
        """It should raise error on invalid category"""
        data = {
            "name": "Test",
            "description": "Invalid category",
            "price": "10",
            "available": True,
            "category": "INVALID"
        }
        product = Product()
        with self.assertRaises(DataValidationError):
            product.deserialize(data)

    def test_deserialize_with_type_error(self):
        """It should raise DataValidationError when body is not a dict"""
        product = Product()
        with self.assertRaises(DataValidationError):
            product.deserialize(None)   # None sẽ gây TypeError

    def test_delete_a_product(self):
        """It should Delete a Product"""
        product = ProductFactory()
        product.id = None
        product.create()
        products = Product.all()
        self.assertEqual(len(products), 1)

        product.delete()
        products = Product.all()
        self.assertEqual(len(products), 0)

    def test_list_all_products(self):
        """It should List all Products in the database"""
        products = Product.all()
        self.assertEqual(len(products), 0)

        for _ in range(0, 5):
            product = ProductFactory()
            product.create()

        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_find_by_name(self):
        """It should Find a Product by Name"""
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()

        name = products[0].name
        count = len([p for p in products if p.name == name])

        found = Product.find_by_name(name)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.name, name)

    def test_find_by_availability(self):
        """It should Find Products by Availability"""
        products = ProductFactory.create_batch(10)
        for product in products:   
            product.create()

        available = products[0].available
        count = len([p for p in products if p.available == available])

        found = Product.find_by_availability(available)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.available, available)

    def test_find_by_category(self):
        """It should Find Products by Category"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()

        category = products[0].category
        count = len([p for p in products if p.category == category])

        found = Product.find_by_category(category)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.category, category)

    def test_find_by_category_explicit(self):
        """It should Find Products by a specific category"""
        product = ProductFactory(category=Category.FOOD)
        product.create()
        found = Product.find_by_category(Category.FOOD)
        self.assertGreater(found.count(), 0)
        for item in found:
            self.assertEqual(item.category, Category.FOOD)

    def test_find_by_price_decimal(self):
        """It should find products by Decimal price"""
        product = Product(name="Book", description="Sci-fi", price=Decimal("19.99"), available=True, category=Category.FOOD)
        product.create()
        found = Product.find_by_price(Decimal("19.99"))
        self.assertGreater(found.count(), 0)
        for p in found:
            self.assertEqual(p.price, Decimal("19.99"))

    def test_find_by_price_string(self):
        """It should find products by string price"""
        product = Product(name="Pen", description="Blue ink", price=Decimal("2.50"), available=True, category=Category.TOOLS)
        product.create()
        found = Product.find_by_price("2.50")
        self.assertGreater(found.count(), 0)
        for p in found:
            self.assertEqual(p.price, Decimal("2.50"))
