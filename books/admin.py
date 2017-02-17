from django.contrib import admin

# Register your models here.

#registration
from books.models import regis
admin.site.register(regis)

#questions
from books.models import questions
admin.site.register(questions)

#answers
from books.models import answers
admin.site.register(answers)

#average ratings of questions
from books.models import avgrating_questions
admin.site.register(avgrating_questions)

#average rating of answers
from books.models import avgrating_answers
admin.site.register(avgrating_answers)

#notification
from books.models import notification
admin.site.register(notification)

