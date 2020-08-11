import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    # set up CORS, allowing all origins
    CORS(app, resources={'/': {'origins': '*'}})

    @app.after_request
    def after_request(response):
        '''
        Sets access control.
        '''
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response

  
 #Get all categories endpoint

    @app.route('/categories')
    def get_categories():
        categories = Category.query.order_by(Category.type).all()
            #view serialized data
        return jsonify({
                'success': True,
                'categories': {category.id: category.type for category in categories}
            })
            


    #get all qus=estions endpoint
    @app.route('/questions')
    def get_questions():
        questions = Question.query.order_by(Question.id).all()
        paginated = paginate_questions(request, questions)
        categories = Category.query.order_by(Category.type).all()

    #View data
        return jsonify({
            'success': True,
            'questions': paginated,
            'categories': {category.id: category.type for category in categories},
            'total_questions': len(questions),
            'current_category': None
        })

    #Delete question By id
    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):

         
             question = Question.query.get(id)           
             question.delete()

            # return success response when deleted
             return jsonify({
                'success': True,
                'deleted': id
              })



      
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        body = request.get_json()
        search_term = body.get('searchTerm')
        search_results = Question.query.filter(
        Question.question.ilike(f'%{search_term}%')).all()
        questions = paginate_questions(request, search_results)

        return jsonify({
                'success': True,
                'questions': questions,
                
            })
    


    

    @app.route("/questions", methods=['POST'])
    def post_question():
        body = request.get_json()

  
        new_question = body.get('question')
        new_answer = body.get('answer')
        new_difficulty = body.get('difficulty')
        new_category = body.get('category')

        try:
          #Add and insert new question
            question = Question(question=new_question, answer=new_answer,
                                difficulty=new_difficulty, category=new_category)
            question.insert()

          # get paginated questions
            questions = Question.query.order_by(Question.id).all()
            paginated_questions = paginate_questions(request, questions)
            total_questions= len(Question.query.all())

            return jsonify({
                    'success': True,
                    'created': question.id,
                    'question_created': question.question,
                    'questions': paginated_questions,
                    'total_questions': total_questions
                })


        except:
            abort(422)


    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):
        try:
            #get category by id
            category = Category.query.filter_by(id=category_id).one_or_none()
            #get all questiions in selected category
            questions = Question.query.filter_by(category=category.id).all()
            paginated = paginate_questions(request, questions)
            total_questions=len(questions)



            return jsonify({
                'success': True,
                'questions': paginated,
                'total_questions': len(questions),
                'current_category': category.type
            })
        except:
            abort(404)


    @app.route('/quizzes', methods=['POST'])
    def play_quiz_question():

        data = request.get_json()
        previous_questions = data.get('previous_questions')
        quiz_category = data.get('quiz_category')

        if not ('quiz_category' in data and 'previous_questions' in data):
            abort(422)


        if (quiz_category['id'] == 0):
            questions = Question.query.filter(Question.id.notin_(previous_questions)).all()
        else:
            questions = Question.query.filter_by(
                    category=quiz_category['id']).filter(Question.id.notin_((previous_questions))).all()



        def get_random_question():
            return questions[random.randint(0, len(questions)-1)]

        if questions:
          question = get_random_question()
        else:
          None

        return jsonify({
            'success': True,
            'question': question.format()
        })




#####  Error handlers

       
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Resource not found"
        }), 404
 
    #
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable entity"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad request"
        }), 400

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'An error has occured'
        }), 500

  
    return app

    