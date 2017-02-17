from django.db import models
from django.db.models import Model
from django.core.exceptions import ValidationError
from django.core.exceptions import NON_FIELD_ERRORS


# Listfied helps in storing data in form of list
#ast helps in storing or retriving data as avl trees
import ast
class ListField(models.TextField):
    __metaclass__ = models.SubfieldBase
    description = "Stores a python list"

    def __init__(self, *args, **kwargs):
        super(ListField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            value = []

        if isinstance(value, list):
            return value

        return ast.literal_eval(value)

    def get_prep_value(self, value):
        if value is None:
            return value

        return unicode(value)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)

#table 'regis' = Registration Table which stores basic info of user
class regis(models.Model):
    username = models.CharField(max_length=150)
    dob = models.CharField(max_length=100)
    email = models.EmailField()
    password1 = models.CharField(max_length=10)
    password2 = models.CharField(max_length=10)
    mobile = models.CharField(max_length=10)
    education = models.CharField(max_length=10)
    institute = models.CharField(max_length=10)
    uid = models.CharField(max_length=10,primary_key=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    # tracking is followers of user
    #tracking = ListField()
    #tracked_by contains uid of persons followed by user
    #tracked_by = ListField()
    #qid of questions followed by user
    tracking_ques = ListField()
    book_markq = ListField()
    book_marka = ListField()

    def __unicode__(self):
        return u'%s %s %s %s %s %s' % (self.username,self.email,self.password1,self.password2,self.random,self.follow)

class questions(models.Model):
    # question id
    qid = models.CharField(max_length=10,primary_key=True)
    #questions posted
    question = models.CharField(max_length=150)
    #question's topic
    topic = models.CharField(max_length=100)
    #question's tag
    tag = models.CharField(max_length=100)
    #question's access specifier
    access = models.CharField(max_length=10)
    timestamp = models.DateTimeField(auto_now_add=True)
    #uid of the user posting the question. s= registration table
    uid = models.ForeignKey(regis)
    #rating of the question(not avg rate)
    rate1 = models.IntegerField(max_length=10)
    # uid of users following this question
    tracked_by = ListField()


    def __unicode__(self):
        return u'%s %s %s %s %s %s %s %s %s' % (self.qid,self.question,self.topic,self.tag,self.access,self.timestamp,self.uid,self.rate1,self.tracked_by)

class answers(models.Model):
    # id of the answer
    aid = models.CharField(max_length=10,primary_key=True)
    #answers
    answer = models.TextField(max_length=1000)
    answer_summary = models.CharField(max_length=500)
    timestamp = models.DateTimeField(auto_now_add=True)
    #uid of the user posting/posted the answer
    uid = models.ForeignKey(regis)
    # question qid for which this is answered
    qid = models.ForeignKey(questions)
    #rating of answer
    rate = models.IntegerField(max_length=10)
    #uid of users following this answer



    def __unicode__(self):
        return u'%s %s %s %s %s %s %s %s %s' % (self.aid,self.answer,self.topic,self.tag,self.access,self.timestamp,self.uid,self.qid,self.rate)

# stores avg rating calculated of answers in avgrating_answers table
class avgrating_answers(models.Model):
    #uid holds list of user's id who have rated the answers
    uid = ListField()
    #aid holds the answer's id of the answers rated
    aid = models.ForeignKey(answers)
    #avgrating holds calculated value of rates
    avg_rating = models.CharField(max_length=20)
    # number of times an answer is rated[helps in calculating the average rating]
    a_rating = ListField()
    #count=models.IntegerField(max_length=10)

    def __unicode__(self):
        return u'%s %s %s %s' % (self.uid,self.aid,self.avg_rating)

# stores avg rating calculated of questions in avgrating_questions table
class avgrating_questions(models.Model):
    #uid holds list of user's id who have rated the questions
    uid = ListField()
    #qid holds the question's id of the questions rated
    qid = models.ForeignKey(questions)
    #avgrating holds calculated value of rates
    avg_rating = models.CharField(max_length=20)
    # number of times a question is rated[helps in calculating the average rating]
    q_rating = ListField()
    #count=models.IntegerField(max_length=10)
    def __unicode__(self):
        return u'%s %s %s %s' % (self.uid,self.qid,self.avg_rating)

class notification(models.Model):
    #message displayed as notification
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    #creator of any activity which leads to a notification
    creator = models.CharField(max_length=10)
    #activity on which,notification is created (for questions or answers,their id is stored)
    created_on = models.CharField(max_length=10)
    created_ona = models.CharField(max_length=10)
    #aid of answer or the rating count of q or a is stored as per the notification
    created_as = models.CharField(max_length=10)
    #if user has viewed it or not ,if yes then value is 1 else 0
    viewed = models.BooleanField(default=False)
    #save suggested Q & A
    suggested = models.CharField(max_length=1000)
    def __unicode__(self):
        return u'%s %s %s %s %s %s' % (self.message,self.timestamp,self.creator,self.created_on,self.viewed,self.suggested)

class reviewing_ques(models.Model):
    #qid being reviewed
    qid = models.ForeignKey(questions)
    #list of uids commented
    uids = ListField()
    #list of comments
    remarks = ListField()

    def __unicode__(self):
        return u'%s %s %s ' % (self.qid,self.uids,self.remarks)


class reviewing_ans(models.Model):
    #aid being reviewed
    qid = models.ForeignKey(questions)
    aid = models.ForeignKey(answers)
    #list of uids commented
    uids = ListField()
    #list of comments
    remarks = ListField()
    def __unicode__(self):
        return u'%s %s %s %s' % (self.qid,self.aid,self.uids,self.remarks)

class book_mark(models.Model):

    uid = models.ForeignKey(regis)
    aid = models.ForeignKey(answers)
    qid = models.ForeignKey(questions)
    label = models.CharField(max_length=30)
    def __unicode__(self):
        return u'%s %s %s %s' % (self.uid,self.aid,self.qid,self.label)


class newsfeed_score(models.Model):
    #uid
    uid = models.ForeignKey(regis)
    #word
    word= models.CharField(max_length=20)
    #score
    score = models.CharField(max_length=10)

    def __unicode__(self):
        return u'%s %s %s ' % (self.uid,self.word,self.score)

class myscore(models.Model):
    #uid
    uid = models.ForeignKey(regis)
    #score
    rate= models.CharField(max_length=20)
    #datefield
    date = models.DateField(max_length=10)

    def __unicode__(self):
        return u'%s %s %s ' % (self.uid,self.rate,self.date)
