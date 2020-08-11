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
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
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

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))

       # fail this test
    def test_non_existing_category(self):
        res = self.client().get('/categories/9999')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')
     


    def test_get_questions(self):

        res = self.client().get('/questions')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['questions'])
        self.assertEqual(len(data['questions']), 10)
        self.assertTrue(len(data['categories']))

    def test_deleting_non_existing_question(self):
        res = self.client().delete('/questions/asdasd')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    def test_delete_question(self):
        """Tests question deletion success"""

        question = Question(question='new question', answer='new answer',difficulty=1, category=1)
        question.insert()
        question_id = question.id
        questions_before = Question.query.all()

        res= self.client().delete('/questions/{}'.format(question_id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], question_id)

    def test_add_question(self):
        new_question = {
            'question': 'question',
            'answer': 'answer',
            'difficulty': 1,
            'category': 1
        }
        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)
  
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)


    def test_empty_question(self):
        question = {
            'question': '',
            'answer': '',
            'category': 9
        }
        res = self.client().post('/questions', json=question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable entity')

    def test_search_questions(self):
        searchTerm = {'searchTerm': 'Clay'}
        res = self.client().post('/questions/search', json=searchTerm)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)


    
    def test_get_questions_per_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['current_category'],'Science')
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])

    def test_non_existing_get_questions_per_category(self):
        res = self.client().get('/categories/5154/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource not found")


    def test_play_quiz_game(self):
        quiz = {'previous_questions': [4,5],
                          'quiz_category': {'type': 'Science', 'id': 1}}        
        res = self.client().post('/quizzes',json=quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
    

    def test_play_quiz_fails(self):
        res = self.client().post('/quizzes', json={})
        data = json.loads(res.data)

       
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable entity')




# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()