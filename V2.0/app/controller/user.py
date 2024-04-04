from flask import Blueprint, render_template, request, g, flash
from app.controller.lexer import get_question, push_answer


userBP = Blueprint('user',__name__)


@userBP.route('/homepage', methods=['GET', 'POST'])
def homepage():
    if request.method == 'GET':
        return render_template('homepage.html', title='算经解释器', header='算经解释器')
    else:

        question = request.form.get("question")
        g.question = question
        
        #将用户输入的问题传到其他函数
        get_question(g.question)

        ## 可以在这里调用lexer和parser的函数
        #
        #
        #
        #

        #将答案放到网页上展示
        answer = push_answer()
        flash(str(answer))

        #print(g.question)
        return render_template('homepage.html', title='算经解释器', header='算经解释器')
    