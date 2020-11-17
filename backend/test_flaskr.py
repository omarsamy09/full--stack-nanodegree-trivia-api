import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_path ='postgres://postgres@localhost:5432/trivia_test'
        setup_db(self.app, self.database_path)
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_paginated_questions(self):
        res=self.client().get('/questions')
        data=json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
   #testing posting a question
    def test_create_question(self):
        new_question={
        'answer':"DARK",
        'question':"what's your favourite tv show",
        'difficulty':"1",
        'category':"5"
        }
        res=self.client().post('/questions',json=new_question)
        data=json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(len(data['questions']))
    #testing missing info in question in form
    def test_create_missing_info_question(self):
        new_question={
        'answer':"DARK",
        'question':"what's your favourite tv show",
        'category':"5"
        }
        res=self.client().post('/questions',json=new_question)
        data=json.loads(res.data)
        self.assertEqual(res.status_code,400)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'bad request')

    #testing searching for a question
    def test_search(self):
        search_term={'searchTerm':"What boxer's original name is Cassius Clay?"}
        res=self.client().post('/search',json=search_term)
        data=json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(len(data['questions'])>0)

    #testing when search term not found
    def test_search_404_error(self):
        search_term={'searchTerm':"What's ur name"}
        res=self.client().post('/search',json=search_term)
        data=json.loads(res.data)
        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'resource not found')

    #testing getting questions in categories
    def test_get_questions_in_category(self):
        res=self.client().get('/categories/5/questions')
        data=json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(len(data['questions'])>0)
   #testing if questions not found
    def test_error_get_questions_in_category(self):
        res=self.client().get('/categories/8/questions')
        data=json.loads(res.data)
        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'resource not found')

  #testing delete end point
    def test_delete_question(self):
        res=self.client().delete('/questions/29')
        data=json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)

    #testing deleting non existing question
    def test_error_deleting(self):
        res=self.client().delete('/questions/1000')
        data=json.loads(res.data)
        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'resource not found')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
