import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import sys

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
def paginate_questions(request,selection):
    page=request.args.get('page',1,type=int)

    start=(page-1)*QUESTIONS_PER_PAGE
    end=start+QUESTIONS_PER_PAGE

    questions=[question.format() for question in selection]
    curr_questions=questions[start:end]

    return curr_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

  '''
  Done: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''

  '''
  DONE: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers','Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods','GET,POST,DELETE,OPTIONS')
      return response


  '''
  @DONE:
  Create an endpoint to handle GET requests
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():
       categories=Category.query.all()
       req_categories={}
       #formatting categories as dictionary of key value pairs
       for category in categories:
           req_categories[category.id]=category.type
       return jsonify({'success':True,'categories':req_categories})

  '''
  @Done:
  Create an endpoint to handle GET requests for questions,
  including pagination (every 10 questions).
  This endpoint should return a list of questions,
  number of total questions, current category, categories.


  TEST: At this point, whens you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions.
  '''
  @app.route('/questions',methods=['GET'])
  def get_questions():
      questions=Question.query.order_by(Question.id).all()
      curr_questions=paginate_questions(request,questions)

      if len(curr_questions)==0:
          abort(404)

      req_categories={}

      categories=Category.query.all()

      #getting categories type
      for category in categories:
          req_categories[category.id]=category.type

      curr_category=[]

      #getting categories of current questions
      for category in curr_questions:
          curr_category.append(category['id'])

      return jsonify({'success':True,'questions':curr_questions,'total_questions':len(Question.query.all()),'categories':req_categories,'currentCategory':curr_category})
  '''
  Done
  Create an endpoint to DELETE question using a question ID.

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page.
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    question = Question.query.filter(Question.id
            == question_id).one_or_none()

    #cheching if no question is found
    if question is None:
        abort(404)
    try:
        question.delete()
        questions = Question.query.order_by(Question.id).all()
        curr_questions = paginate_questions(request, questions)
        return jsonify({'success': True, 'questions': curr_questions,
                       'total_questions': len(Question.query.all())})
    except:
        abort(422)


  '''
  Done
  Create an endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.
  '''
  @app.route('/questions', methods=['POST'])
  def create_question():
      body=request.get_json()
      if not body:
          abort(400)

      input_question=body.get('question',None)
      input_answer=body.get('answer',None)
      input_category=body.get('category',None)
      input_difficulty=body.get('difficulty',None)

      #checking for missing info
      if input_question is None:
          abort(400)
      if input_answer is None:
          abort(400)
      if input_category is None:
          abort(400)
      if input_difficulty is None:
          abort(400)
      try:
          new_question=Question(question=input_question,answer=input_answer,category=input_category,difficulty=input_difficulty)
          new_question.insert()
          questions=Question.query.order_by(Question.id).all()
          curr_questions=paginate_questions(request,questions)
          return jsonify({'success':True,
          'questions':curr_questions,
          'total_questions':len(Question.query.all()),
          'created':new_question.id})
      except:
        abort(422)

  '''
  Done:
  Create a POST endpoint to get questions based on a search term.
  It should return any questions for whom the search term
  is a substring of the question.

  TEST: Search by any phrase. The questions list will update to include
  only question that include that string within their question.
  Try using the word "title" to start.
  '''
  @app.route('/search', methods=['POST'])
  def search_question():
      body=request.get_json()
      if not body :
          abort(400)
      term=body.get('searchTerm',None)

      #checking if user doesn't provide search term
      if term is None:
          abort(400)

      questions=Question.query.filter(Question.question.ilike(f'%{term}%')).all()

      #if no question found
      if not questions:
          abort(404)
      questions_to_be_returned=[question.format() for question in questions ]
      curr_category=[]

      for question in questions_to_be_returned:
          curr_category.append(question['category'])

      return jsonify({'success':True,'questions':questions_to_be_returned,'total_questions':len(Question.query.all()),'currentCategory':curr_category})
  '''


  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
  '''
  #DONE

  @app.route('/categories/<int:category_id>/questions')
  def get_questions_by_category(category_id):

      questions=Question.query.filter(Question.category==category_id).order_by(Question.id).all()

      if not questions:
          abort(404)

      curr_questions=paginate_questions(request,questions)

      return jsonify({'success':True,'questions':curr_questions,'total_questions':len(Question.query.all()),'current_category':category_id})
  '''
  @Done:
  Create a POST endpoint to get questions to play the quiz.
  This endpoint should take category and previous question parameters
  and return a random questions within the given category,
  if provided, and that is not one of the previous questions.

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not.
  '''
  @app.route('/play',methods=['POST'])
  def play():
      body=request.get_json()
      if not body:
          abort(400)

      prev_ques=body.get('previous_questions',None)
      quizCategory=body.get('quiz_category',None)

      questions=[]
      #if no category given
      if not quizCategory:
          if prev_ques:
              questions=Question.query.filter(not_(Question.id.in_(prev_ques))).all()
          else:
              questions=Question.query.all()

      elif  quizCategory['type']=='click':
          #checking if user chooses ALL
          questions=Question.query.all()
      else:
          #if no prev_ques
          if not prev_ques:
              questions=Question.query.filter(Question.category==quizCategory['id']).all()
          else:
              questions=Question.query.filter(Question.category==quizCategory['id']).filter(Question.id.notin_(prev_ques)).all()

      questions_to_return=[question.format() for question in questions ]
      rand_question=random.choice(questions_to_return)
      return jsonify({'success':True,'question':rand_question})

  #404 error handler#
  @app.errorhandler(404)
  def not_found(error):
      return (jsonify({'success': False, 'error': 404,
              'message': 'resource not found'}), 404)


# 422 error handler#

  @app.errorhandler(422)
  def unprocessable(error):
      return (jsonify({'success': False, 'error': 422,
              'message': 'unprocessable'}), 422)


    # 400 error handler #

  @app.errorhandler(400)
  def bad_request(error):
      return (jsonify({'success': False, 'error': 400,
              'message': 'bad request'}), 400)


# 405 error handler#

  @app.errorhandler(405)
  def not_allowed(error):
      return (jsonify({'success': False, 'error': 405,
              'message': 'not allowed'}), 405)

  return app
