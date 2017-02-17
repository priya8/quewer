# from __future__ import unicode_literals
from __future__ import division
from numpy.ma import append
from django.template import Template, Context
import re, collections
import math
import string
from collections import Counter
from random import randint
from django.core.context_processors import csrf
from books.models import questions
from books.models import avgrating_answers
from books.models import answers
from books.models import regis
from books.models import avgrating_questions
from books.Spell import spell_me
from django.utils import timezone
from datetime import datetime
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from books.forms import MyRegistrationForm
#from django.db.models import Avg
from django.template import Context, Template
import ast
#from notification.models import Notification
#from django.db.models.signals import post_save
#from notifications import notify
from books.models import notification
from books.models import book_mark
from books.models import reviewing_ques
from books.models import reviewing_ans
from books.models import newsfeed_score
from books.models import myscore
from django.db.models import Sum
import urllib
import nltk
from nltk.stem import WordNetLemmatizer
import random
from django.template import Template
import json
import pickle
from nltk import pos_tag
import numpy
import enchant, difflib
from books.Spell import spell_me
from enchant.checker import SpellChecker
from nltk.corpus import stopwords
from django.contrib import messages
#import textblob
#from textblob import TextBlob
from nltk import word_tokenize
#import language_check
from django.template import Library, Template
#from django.utils import simplejson
from django.core.serializers import serialize
from django.db.models.query import QuerySet
from django.utils.safestring import mark_safe
#from textblob._text import Context
from books.text import textsummarizer
from books.profanity import profanity_filter

#tool = language_check.LanguageTool('en-US')

register = Library()


def jsonify(object):
    if isinstance(object, QuerySet):
        return mark_safe(serialize('json', object))
    return mark_safe(simplejson.dumps(object))


register.filter('jsonify', jsonify)
jsonify.is_safe = True

#newsfeed interest
def tab_1(request):
    #answers followers
    af = []
    ay = []
    questions1 = []
    #list of qid's of answers
    an_list = []
    uid = request.session['ra_no']
    #whole row of info of user from 's' table
    fol_list = regis.objects.get(uid=uid)
    #All the qids posted by me
    myqlist = questions.objects.filter(uid_id=uid).filter(access="interest").values_list('topic', flat=True).distinct()
    books_list = questions.objects.all().order_by('-timestamp')
    avg = avgrating_answers.objects.all().order_by('-avg_rating')
    avg1 = avgrating_questions.objects.all()
    revq = reviewing_ques.objects.all()
    reva = reviewing_ans.objects.all()
    ans_list = answers.objects.all().order_by('-timestamp')
    an_list += answers.objects.values_list('qid_id', flat=True).distinct()
    #All the qids for which persons('u') have answered, whom user's(currently logged in) is following
    #for u in fol_list.tracking:
        #af += answers.objects.filter(uid_id=u).values_list('qid_id', flat=True).distinct()

    interest = newsfeed_score.objects.filter(uid_id=uid).values_list('word').order_by('score')[:100]

    books_list1 = questions.objects.all().order_by('-timestamp')
    for k in interest:
        questions1 += questions.objects.filter(topic=k).values_list('qid').distinct()
    #return HttpResponse(questions1)

    for a in interest:
        questions1 += questions.objects.filter(tag=a)

    for a in questions1:
        qid = a.qid
        ay += answers.objects.filter(qid_id=qid)

    return render(request, 'newsfeed.html',
                  {'interest': interest, 'questions1': questions1, 'ay': ay, 'revq': revq, 'reva': reva,
                   'books_list': books_list, 'full_name': request.session['full_name'],
                   'ra_no': request.session['ra_no'], 'ans_list': ans_list, 'avg': avg, 'avg1': avg1, 'uid': uid,
                   'fol_list': fol_list, 'myqlist': myqlist, 'af': af, 'an_list': an_list})

#randomized Newsfeed
"""
def loggedin_random(request):
     #answers followers
     af = []
     ay = []
     questions1 = []
     #list of qid's of answers
     an_list = []
     uid = request.session['ra_no']
     books_list = questions.objects.all().order_by('-timestamp')
     avg = avgrating_answers.objects.all().order_by('-avg_rating')
     avg1 = avgrating_questions.objects.all()
     revq = reviewing_ques.objects.all()
     reva = reviewing_ans.objects.all()
     ans_list = answers.objects.all().order_by('-timestamp')
     an_list += answers.objects.values_list('qid_id',flat=True).distinct()

     random.shuffle(list(books_list))


     return render(request,'newsfeed_random.html',{'revq':revq,'reva':reva,'books_list': books_list,'full_name':request.session['full_name'],'ra_no':request.session['ra_no'],'ans_list':ans_list,'avg':avg,'avg1':avg1,'uid':uid,'af':af,'an_list':an_list})
"""

#activities
def tab_2(request):
    dictionary = {}
    di = {}
    b_list = []
    r_list = []

    #currently logged in user's (ra_no) posted questions and its respective answers
    a_list = questions.objects.filter(uid=request.session['ra_no']).order_by('-timestamp')
    for p in a_list:
        b_list += answers.objects.filter(qid_id=p.qid)
    b_list = set(b_list)

    #start of trending topics
    t_list = [definition.encode("utf8") for definition in
              questions.objects.filter(uid=request.session['ra_no']).values_list('topic', flat=True).distinct()]
    for k in t_list:
        r_list.append(questions.objects.filter(uid=request.session['ra_no']).filter(topic=k).count())

    dictionary = dict(zip(t_list, r_list))
    di = sorted(dictionary, key=dictionary.get, reverse=True)
    # end of trending topics

    #currently logged in user's (ra_no) posted answers and its respective questions
    c_list = []
    d_list1 = answers.objects.filter(uid=request.session['ra_no']).order_by('-timestamp')
    d_list2 = answers.objects.filter(uid=request.session['ra_no']).order_by('-timestamp')
    ques_ans_list = []
    for questi in d_list1:
        ques_ans_list += questions.objects.filter(qid=questi.qid_id).order_by('-timestamp')
    d_list = answers.objects.filter(uid=request.session['ra_no']).order_by('-timestamp')
    for p in d_list:
        c_list += questions.objects.filter(qid=p.qid_id)
    c_list = set(c_list)

    dictionary_timestamp = {}
    for a in a_list:
        dictionary_timestamp.update({a.qid: a.timestamp})
    for a in d_list:
        dictionary_timestamp.update({a.aid: a.timestamp})
    dictionary_answers = dict(zip(d_list2, ques_ans_list))
    qid_list = questions.objects.filter().order_by('-timestamp')

    #rating questions or answers
    dictionary_rate = {}
    p = []
    avg_list = avgrating_questions.objects.all().values_list('qid_id')
    for t in avg_list:
        p += t

    for p1 in p:
        please = questions.objects.get(qid=p1)

        al = avgrating_questions.objects.get(qid_id=p1)
        if request.session['ra_no'] in al.uid:
            avg_uid = avgrating_questions.objects.get(qid=p1)
            avg_uid_list = avg_uid.uid
            avg_rate = avgrating_questions.objects.get(qid=p1)
            avg_rate_list = avg_rate.q_rating
            dict_uid_rate = dict(zip(avg_uid_list, avg_rate_list))
            #return HttpResponse(dict_uid_rate)
            for k, v in dict_uid_rate.iteritems():

                if k == request.session['ra_no']:
                    rate = v
                    #return HttpResponse(rate)
                    dictionary_rate.update({please.question: rate})



    #Following
    q_follow_list = []
    me = regis.objects.get(uid=request.session['ra_no'])
    follow_quest = me.tracking_ques
    if follow_quest:
     for que in follow_quest:
        try:
         q1 = questions.objects.get(qid=que)
         q_follow_list.append(q1.question)
        except questions.DoesNotExist:
           q_follow_list = []

    return render(request, 'activities.html',
                  {'full_name': request.session['full_name'], 'q_follow_list': q_follow_list,
                   'dictionary_rate': dictionary_rate.iteritems(), 'ra_no': request.session['ra_no'],
                   'qid_list': qid_list, 'd_list2': d_list2,
                   'ques_ans_list': ques_ans_list, 'dictionary_answers': dictionary_answers, 'b_list': b_list,
                   'c_list': c_list, 'd_list1': d_list1, 'd_list': d_list, 't_list': t_list, 'r_list': r_list,
                   'dictionary': dictionary, 'di': di, 'a_list': a_list,'count':request.session['count'],
                   'dictionary_timestamp': sorted(dictionary_timestamp.iteritems(), reverse=True)})


#myscore
"""
def tab_4(request):

    #for secured
    secured_questions = {}
    qid_list = []
    qrate_list = []

    #secured questions
    # All qids questioned by me
    qid_list += questions.objects.filter(uid_id=request.session['ra_no']).values_list('qid', flat=True).distinct()
    # rates of all the qid_list in qrate_list
    for x in qid_list:
        qrate_list += questions.objects.filter(qid=x).values_list('rate1', flat=True).distinct()
    #combining two lists into dict
    secured_questions = dict(zip(qid_list, qrate_list))

    #secured answers
    aid_list = []
    arate_list = []
    #All aids answered by me
    aid_list += answers.objects.filter(uid_id=request.session['ra_no']).values_list('aid', flat=True).distinct()
    # rates of all the aid_list in arate_list
    for y in aid_list:
        arate_list += answers.objects.filter(aid=y).values_list('rate', flat=True).distinct()
    #combining two lists into dict
    secured_answers = dict(zip(aid_list, arate_list))
    #----------------------------------------------------------------------------------------------

    # given(questions)
    uid_rating = {}
    qid_list_avgq = []
    givenq = {}
    #given questions
    #all qid from avgrating_questions table
    qid_list_avgq += avgrating_questions.objects.values_list('qid_id', flat=True).distinct()

    for a in qid_list_avgq:

        uid_avgq = avgrating_questions.objects.get(qid_id=a)
        rate_avgq = avgrating_questions.objects.get(qid_id=a)
        #all uids of each of the qids
        uid_as_list = uid_avgq.uid
        #all rates of each of the qids
        rate_as_list = rate_avgq.q_rating
        #combining two lists into dict
        uid_rating = dict(zip(uid_as_list, rate_as_list))
        #all qids and rates into dict rated by me
        for uid, rating in uid_rating.iteritems():
            if uid == request.session['ra_no']:
                givenq.update({a: rating})


    #given answers
    uid_rating_ans = {}
    aid_list_avga = []
    given_ans = {}

    #all aid from avgrating_answers table
    aid_list_avga += avgrating_answers.objects.values_list('aid_id', flat=True).distinct()

    for b in aid_list_avga:
        #b contains aid(one at a time)
        uid_avga = avgrating_answers.objects.get(aid_id=b)
        rate_avga = avgrating_answers.objects.get(aid_id=b)
        #all uids of each of the aids
        uid_as_list_ans = uid_avga.uid
        #all rates of each of the aids
        rate_as_list_ans = rate_avga.avg_rating
        #combining two lists into dict
        uid_rating_ans = dict(zip(uid_as_list_ans, rate_as_list_ans))
        #all aids and rates into dict rated by me
        for uid_ans, rating_ans in uid_rating_ans.iteritems():
            if uid_ans == request.session['ra_no']:
                given_ans.update({b: rating_ans})

    return render(request, 'myscore.html',
                  {'given_ans': sorted(given_ans.iteritems()), 'givenq': sorted(givenq.iteritems()),
                   'arate_list': arate_list, 'aid_list': aid_list, 'qrate_list': qrate_list, 'qid_list': qid_list,
                   'full_name': request.session['full_name'], 'ra_no': request.session['ra_no'],'count':request.session['count'],
                   'qdata': sorted(secured_questions.iteritems()), 'adata': sorted(secured_answers.iteritems())})
"""

def tab_4(request):
   score = 100
   total_users = regis.objects.all().count()

   s = myscore.objects.filter(uid_id =request.session['ra_no'])
   for a in s:
     if a.rate != None:
       score = score+int(a.rate)

   if total_users <= 99:

       if score>=100 and score<500:
              medal = "Bronze"
              return render(request,'myscore.html',{'score':score,'medal':medal,'full_name': request.session['full_name'],'count':request.session['count']})
       if score>=500 and score<1000:
              medal = "Silver"
              return render(request,'myscore.html',{'score':score,'medal':medal,'full_name': request.session['full_name'],'count':request.session['count']})
       if score>=1000:
              medal = "Gold"
              return render(request,'myscore.html',{'score':score,'medal':medal,'full_name': request.session['full_name'],'count':request.session['count']})

   else:
      gold1   = math.ceil(total_users/100)
      silver1 = math.ceil(total_users*2/100)
      silver2 = math.ceil(total_users*3/100)
      bronze1 = math.ceil(total_users*5/100)

      myscore1 = myscore.objects.values('uid_id').annotate(dcount = Sum('rate')).order_by('-dcount')[:gold1-1]
      for ms1 in myscore1:
       if request.session['ra_no'] == ms1['uid_id']:
            medal = "Gold"
            return render(request,'myscore.html',{'score':score,'medal':medal,'full_name': request.session['full_name'],'count':request.session['count']})


      myscore2= myscore.objects.values('uid_id').annotate(dcount=Sum('rate')).order_by('-dcount')[silver1-1:silver2-1]
      for ms2 in myscore2:
       if request.session['ra_no'] == ms2['uid_id']:
            medal = "Silver"
            return render(request,'myscore.html',{'score':score,'medal':medal,'full_name': request.session['full_name'],'count':request.session['count']})



      myscore3 = myscore.objects.values('uid_id').annotate(dcount=Sum('rate')).order_by('-dcount')[silver2:bronze1-1]
      for ms3 in myscore3:
       if request.session['ra_no'] == ms3['uid_id']:
            medal = "Bronze"
            return render(request,'myscore.html',{'score':score,'medal':medal,'full_name': request.session['full_name'],'count':request.session['count']})


      medal="Newbie"
      return render(request,'myscore.html',{'score':score,'medal':medal,'full_name': request.session['full_name'],'count':request.session['count']})




def auto_tag(request, anystring):
    str1 = ''


    tag_list = {}

    tag_final = []


    stop = stopwords.words('english')
    non_stop = [i for i in anystring.split() if i not in stop]
    non_stop = (' ').join(non_stop)



    #for line in anystring1: # for each line
    words = pos_tag(non_stop.strip().split())  # all words on the line
    #return HttpResponse(words)
    for word1, word2 in zip(words, words[1:]):  # iterate through pairs


        if word1[1] == 'NNP' and word2[1] == 'NNP' or word1[1] == 'NNPS' and word2[1] == 'NNP' or word1[1] == 'NNP' and word2[1] == 'NNPS':  # test the pair

            tag_final += word1[0] + word2[0]
        if word1[1] == 'JJ' and word2[1][1] == 'N':  # test the pair

            tag_final += word1[0] + word2[0]
        if word1[1] == 'NN' or word1[1] == 'NNP' or word1[1] == 'NNS' or word1[1] == 'NNPS':
            for x in tag_final:

                if word1[0].lower().find(x.lower()) != -1:
                    tag_final += word1[0]
            
    #return HttpResponse(tag_final)

    str1 = (',').join(tag_final)
    #return HttpResponse(tag_final)



    #Topic
    """
    qid_list += questions.objects.values_list('qid', flat=True).distinct()
    for qid in qid_list:
        each_tag = questions.objects.get(qid=qid)
        tag_list.update({qid: each_tag.tag})
    #tag_ques1 = [token for token, pos in tag_ques if pos.startswith('N')]
    #return HttpResponse(tag_ques1)
    topics_list = []
    for key, value in tag_list.iteritems():

        match = set(tag_final) & set(value.split(","))
        count1 = float(len(match)) / float(len(tag_final))
        #return HttpResponse(count1)
        if float(count1) >= 0.95:
            topics_list1 = questions.objects.get(qid=key)
            topics_list.append(topics_list1.topic)

        elif float(count1) >= 0.7:
            topics_list1 = questions.objects.get(qid=key)
            topics_list.append(topics_list1.topic)
    """

    return render(request, 'newsfeed.html', {'anystring': anystring, 'tag_ques': str1,
                                             'tag_list': tag_list.iteritems(),'tag_final':tag_final})


"""
def edit(request,qid):
    if 'ques_edit' in request.GET and request.GET['ques_edit']:
      ques_edit = request.GET['ques_edit']
      b = questions.object.get(qid=qid)
      b.question = ques_edit
      b.save()
      return HttpResponseRedirect('/thanks/')
"""



#storing the question in database
def post_question(request):
    if 'ques' in request.GET and request.GET['ques']:
        ques = request.GET['ques']
        ques_tag = ques
    if 'topic' in request.GET and request.GET['topic']:
        topic = request.GET['topic']
    #if 'tags' in request.GET and request.GET['tags']:
        #tag = request.GET['tags']
    if 'access' in request.GET and request.GET['access']:
        access = request.GET['access']
        rand_no = randint(00000000, 99999999);
        qid = rand_no
    request.session['ques'] = ques
    #if access == "0":
         #html = "<html><head><script type='text/javascript'> alert('please select access specifier'); window.location = '/thanks/';</script></head></html>"
         #return HttpResponse(html)


    #profanity

    bad_words = []
    question_list = ques.split()
    for each in question_list:
        #c = profanity_filter.Filter(each, clean_word='unicorn')
        #w = c.clean()
        #word = str(w)
        bad_names = [line.strip() for line in open('bad_words.txt')]
        if str(each) in bad_names or '*' in list(str(each)):
            bad_words.append(str(each))
    if len(bad_words) != 0:
     return HttpResponse(
                "<html><head><script type='text/javascript'> alert('Kindly Restrict the usage of following words in your question: \t' + %s);window.location = '/thanks/';</script></head></html>" % bad_words)

    #contractions
    dict_contract={}
    with open("contractions.txt", "r") as f:
      for line in f:
          list_d = line.split(',')
          dict_contract.update({list_d[0]:list_d[1]})


    for k,v in dict_contract.iteritems():
          if k in ques:
             ques = string.replace(ques,k,v)



    #autotag
    tag_final=[]
    tag_list=[]
    # type of the following variables is string
    str_noun=''
    str_verb=''
    str_adj=''
    str_final=''
    # type of the following variables are boolean
    flag_n = 0
    flag_none = 0
    wl = WordNetLemmatizer()
    #who and what same operations to be performed ,hence in same list( NOT USED )
    list_who=['who','what',"what's",'whom','whose','explain','compare','differentiate','comprehend','define','elaborate']
    list_when=['when','are','is','can','could','will','would','shall','should','do','did',"doesn't","didn't"]
    list_how=['how','list','which']
    list_why=['why','reason','discuss']
    list_type=list_who + list_when + list_how + list_why

    # removing the last character from the question ( either . or ?)
    if ques_tag[-1] == '?' or ques_tag[-1] == '.':
      ques_tag = ques_tag[:-1]
    #splitting up the question into many lines on ?, . & ()
    ques_tag = re.split('[?.()]', ques_tag)
    tag=''

    #for each of the lines from the above split question, Replacing ? and . by blank
    for lines in ques_tag:
      lines.replace("?","")
      lines.replace(".","")
    stop=stopwords.words('english')
    final_tag1=[]
    #each line
    for line in ques_tag:
        flag_n=0
        #flag_who=0
        #flag_how=0
        #flag_when=0
        #flag_why=0
        str_noun=''
        str_verb=''
        str_adj=''
        str_caps=''
        str_num=''
        tag_verb=[]
        tag_adj=[]
        tag_num=[]

        words = pos_tag(line.strip().split())

#nouns
        #words = [ ('Modi', 'NN') ], i = Modi, j = NN
        for i,j in words:

            if j[0] != 'N':
                flag_n=0

#verbs
                # if it is a verb and not a stop word
                if j[0] == 'V' and i.lower() not in stop:
                 #if the length of the verb is more than 5. Eg: threw is a verb. len( threw ) >=5.
                 if len(i) >= 5:
                  tag_verb.append(wl.lemmatize(i,'v'))



            if wl.lemmatize(i,'v').lower() not in stop:
             if j == 'NNP' or j == 'NN' or j == 'NNPS' or j == 'NNS':

                if flag_n == 0:
                    if str_noun == '':
                        flag_n=1
                        str_noun = i
                    else:
                        str_noun = str_noun + ',' + i
                        flag_n=1
                else:
                    str_noun = str_noun + ' ' + i
                    flag_n=1

            if i.isupper() and len(i)>1:
             str_caps=str_caps+','+i


        if len(tag_verb)>0:
            str_verb = (',').join(tag_verb)
            str_verb = ',' + str_verb


 #adj and noun one after another
        for word1, word2 in zip(words, words[1:]):  # iterate through pairs
            if word1[1].startswith('J',0,len(word1[1])) and word2[1].startswith('NN',0,len(word2[1])) and word1[0].lower() not in stop: # test the pair
                if word2[0] in str_noun:
                 str_noun.replace(word2[0],'')
                 tag_adj.append(word1[0] +' '+ word2[0])

            if word1[1]=='CD' and word2[1].startswith('NN',0,len(word2[1])) : # test the pair
                if word2[0] in str_noun:
                 str_noun.replace(word2[0],'')
                 tag_num.append(word1[0] +' '+ word2[0])
        if len(tag_adj)>0:
            str_adj = (',').join(tag_adj)
            str_adj = ',' + str_adj
        if len(tag_num)>0:
            str_num = (',').join(tag_num)
            str_num = ',' + str_num

        str_final1 = str_caps+str_noun + str_verb+str_adj+str_num

#question type
   #question type


        tag_list += str_final1.split(',')
        #for x in tag_list:
         #if x.lower() in list_type:
          #tag_list.remove(x)


    tag_list1 = sorted(tag_list, key = len)
    list_tag = [y for x,y in enumerate(tag_list1) if all(y not in z for z in tag_list1[x + 1:])]
    final_tag = list(set(tag_list1) & set(list_tag))

    for tags in sorted(final_tag, key=lambda tags : len(tags), reverse=True):
     final_tag1.append(tags)

#tag
    tag = (',').join(final_tag1[:5])
    for caps in final_tag1:
     if caps not in tag and len(caps)>1:
      if caps.isupper() or caps in str_num:
       tag = tag + ',' + caps
#--------------------------tag--------------------------------------------------


    #similar questions(error rate + Spell Checking)

    #putting the question typed to a list
    ques_list = ques.split()

    #removing stop words from the question to calculate the error rate
    stop = stopwords.words('english')
    non_stop = [i for i in ques.split() if i not in stop]

    #error_words list has the list of error words from the question typed-in
    error_words = []
    chkr = SpellChecker("en_US")
    chkr.set_text(ques)
    for err in chkr:
        error_words.append(err.word)

    #error_rate = no of wrong words / no of right words in the question(apart from stop words)
    p_ques = pos_tag(non_stop)
    noun_ques = [s for s in p_ques if s[1] == 'NN' or s[1] == 'NNS' or s[1] == 'NNP' or s[1] == 'NNPS']
    verb_ques = [s for s in p_ques if
                 s[1] == 'VB' or s[1] == 'VBD' or s[1] == 'VBG' or s[1] == 'VBN' or s[1] == 'VBP' or s[1] == 'VBZ']
    prop_noun = len([s for s in p_ques if s[1] == 'NNP'])
    adjective_ques = [s for s in p_ques if s[1] == 'JJ' or s[1] == 'JJR' or s[1] == 'JJS']
    p = len(error_words) - prop_noun
    error_rate = float(p) / float(len(ques_list))

    if float(error_rate) > 0.25 or noun_ques == None and verb_ques == None:

        #print invalid on screen

        html = "<html><head><script type='text/javascript'> alert('Invalid Question'); window.location = '/thanks/';</script></head></html>"
        return HttpResponse(html)
    else:

        #Spell Checker using language_check
        #matches = tool.check(ques)
        #r = language_check.correct(ques, matches)





      #return HttpResponse(re)
      #matches = tool.check(ques)
      #r = language_check.correct(ques, matches)
        rr = []
        propernouns = []
        #r = spell_me.correct_text(str(ques))
        for each in ques.split():
             tagged_sent = pos_tag(ques.split())
             propernouns = [word for word,pos in tagged_sent if pos == 'NNP']
             if each not in propernouns:
              each = spell_me.correct_text(str(each))

             rr.append(each)
        r = " ".join(rr)
        #return HttpResponse("".join(r))

        """Similar Questions """
        #tokenzie the corrected string (question)
        text = nltk.word_tokenize(r)

        #apply part of speech tagger to the tokenized question
        p = pos_tag(text)



        #get the type of question
        WH_ques = [s for s in p if s[1] == 'WH']

        """get all qid's from questions table to apply pos_tag to each of the question and compare with the pos of
         question in hand
        """
        all_qid = []

        #all qid's
        all_qid += questions.objects.values_list('qid', flat=True)

        flag = 0

        #get the count of the topic in Db. if 0, then store the question in hand into DB
        topic_exist = questions.objects.filter(topic=topic).count()

        if topic_exist == 0:

            flag = 1
            rate = 0
            #saving into database
            b = questions(rate1=rate, qid=qid, question=r, topic=topic, tag=tag, access=access,
                          timestamp=timezone.now(), uid_id=request.session['ra_no'])
            b.save()

            #saving avgrating of this question into avgrating_questions table
            a2 = avgrating_questions(qid_id=qid, avg_rating=rate)
            a2.save()

            a3 = reviewing_ques(qid_id=qid)
            a3.save()

            #saving into notification table
            n = notification(message="question added ", timestamp=timezone.now(), created_on=qid,
                             creator=request.session['ra_no'], created_as=qid, viewed=False)
            n.save()

            #score for topic in newsfeed entry table
            try:
                sim_topic = newsfeed_score.objects.get(word=topic, uid_id=request.session['ra_no'])
                k = sim_topic.score
                s = ast.literal_eval(k)
                s = s + 10
                sim_topic.delete()
                a4 = newsfeed_score(uid_id=request.session['ra_no'], word=topic, score=s)
                a4.save()
            except:
                a5 = newsfeed_score(uid_id=request.session['ra_no'], word=topic, score=10)
                a5.save()

            tags = tag.split(',')
            for a in tags:
                try:
                    sim_tags = newsfeed_score.objects.get(word=a, uid_id=request.session['ra_no'])
                    k = sim_tags.score
                    s = ast.literal_eval(k)
                    s = s + 5
                    sim_tags.delete()
                    a4 = newsfeed_score(uid_id=request.session['ra_no'], word=a, score=s)
                    a4.save()
                except:
                    a5 = newsfeed_score(uid_id=request.session['ra_no'], word=a, score=5)
                    a5.save()

            return HttpResponseRedirect('/thanks/')



        #get the count of the tag in Db. if 0, then store the question in hand into DB

        elif topic_exist != 0:

            #list of qid's whose tags match with that of the tag in the interface
            sim_qid = []

            count_tag = 0
            #convert into list, eg: 'india,love,country' = ['india','love','country']
            tag_interface = tag.split(',')
            #return HttpResponse(tag_interface)
            topic_all = []
            #get all the topic, and find the particular tags
            topic_all = questions.objects.filter(topic=topic).values_list('topic', flat=True)

            for each_topic in topic_all:

                #for each topic, get the tag
                tags_list = questions.objects.filter(topic=each_topic)
                #return HttpResponse(tags_list)
                for t in tags_list:
                 get_tag = t.tag
                #convert the tag into list, eg: 'india,love,country' = ['india','love','country']
                 tag_db = get_tag.split(',')
                 count_tag=0
                 #return HttpResponse(tag_db)
                #get the count of the matched tags
                 for each_tag in tag_interface:
                   #return HttpResponse(tag_db)
                   for each_db in tag_db:

                    if each_tag in each_db:

                        count_tag = count_tag + 1
                   if float(count_tag) / float(len(tag_interface)) >= 0.5:
                    #if more than 95%, append the qid to the list
                      sim_qid.append(t.qid)

            tags_unmatch = float(count_tag) / len(tag_interface)
            if tags_unmatch < 0.4:
                flag = 1
                rate = 0
                #saving into database
                b = questions(rate1=rate, qid=qid, question=r, topic=topic, tag=tag, access=access,
                              timestamp=timezone.now(), uid_id=request.session['ra_no'])
                b.save()

                #saving avgrating of this question into avgrating_questions table
                a2 = avgrating_questions(qid_id=qid, avg_rating=rate)
                a2.save()

                a3 = reviewing_ques(qid_id=qid)
                a3.save()

                #saving into notification table
                n = notification(message="question added ", timestamp=timezone.now(), created_on=qid,
                                 creator=request.session['ra_no'], created_as=qid, viewed=False)
                n.save()

                #score for topic in newsfeed entry table

                try:
                    sim_topic = newsfeed_score.objects.get(word=topic, uid_id=request.session['ra_no'])
                    k = sim_topic.score
                    s = ast.literal_eval(k)
                    s = s + 10
                    sim_topic.delete()
                    a4 = newsfeed_score(uid_id=request.session['ra_no'], word=topic, score=s)
                    a4.save()
                except:
                    a5 = newsfeed_score(uid_id=request.session['ra_no'], word=topic, score=10)
                    a5.save()

                tags = tag.split(',')

                for a in tags:
                    try:
                        sim_tags = newsfeed_score.objects.get(word=a, uid_id=request.session['ra_no'])
                        k = sim_tags.score
                        s = ast.literal_eval(k)
                        s = s + 5
                        sim_tags.delete()
                        a4 = newsfeed_score(uid_id=request.session['ra_no'], word=a, score=s)
                        a4.save()
                    except:
                        a5 = newsfeed_score(uid_id=request.session['ra_no'], word=a, score=5)
                        a5.save()

                return HttpResponseRedirect('/thanks/')


            else:
                stop = stopwords.words('english')
                question_pos = []
                non_stopdb = []
                similar_questions = []
                list_similar = []
                b = {}
                for qidd in sim_qid:
                    #get each question
                    question_pos = questions.objects.filter(qid=qidd).values_list('question', flat=True)

                    #return HttpResponse(question_pos)
                    #tokenize each question
                    #tokenized_question = nltk.word_tokenize(str(question_pos))
                    for q in question_pos:
                        #return HttpResponse(q)
                        #question_pos = questions.objects.get(qid=qidd)
                        non_stopdb += [i for i in q.split() if i not in stop]
                        #apply part of speech tagger to the tokenized question
                        posed_question = pos_tag(non_stopdb)
                        #return HttpResponse(question_pos)

                        #get the noun from each question (in DB)
                        noun_each = [s for s in posed_question if
                                     s[1] == 'NN' or s[1] == 'NNS' or s[1] == 'NNP' or s[1] == 'NNPS']

                        #get verb
                        verb_each = [s for s in posed_question if
                                     s[1] == 'VB' or s[1] == 'VBD' or s[1] == 'VBG' or s[1] == 'VBN' or s[1] == 'VBP' or
                                     s[1] == 'VBZ']

                        #get adjective
                        adjective_each = [s for s in posed_question if s[1] == 'ADJ' or s[1] == 'JJR' or s[1] == 'JJS']

                        #get the WH type
                        WH_each = [s for s in posed_question if s[1] == 'WH']

                        #compare
                        noun_match = set(noun_ques) & set(noun_each)
                        verb_match = set(verb_ques) & set(verb_each)
                        adj_match = set(adjective_ques) & set(adjective_each)
                        WH_match = set(WH_ques) & set(WH_each)

                        if noun_match or verb_match:
                            if len(noun_match) / max(len(noun_ques), len(noun_each)) >= 0.5:
                                #if all(noun, verb and adjective) same, add to similar questions
                                b.update({qidd: q})
                k = []
                for qid1, question2 in b.iteritems():
                    html = "<li><a href='single1/%s' target='_blank' style='color:white;'>%s</a></li>" % (qid1, question2)
                    k.append(html)
                if k:

                 h = """
                            <html><head>
                            <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Bootstrap -->
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.2/css/bootstrap.min.css">

<!-- Optional theme -->
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.2/css/bootstrap-theme.min.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-select/1.6.3/css/bootstrap-select.min.css">
<style>

.navbar-default{

   background: #CC3232;
 }

</style>

<!-- Latest compiled and minified JavaScript -->
<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.2/js/bootstrap.min.js"></script>


                            <script type='text/javascript'> </script></head><body>
                            <div class="navbar navbar-default navbar-fixed-top" style="min-height: 60px;" role="navigation">

<!--end of side menu-->

    <!--top navbar contents-->
    <div class="container">
            <div class="navbar-header">
                <a class="navbar-brand" href="#" style="color:#FFFFFF;"><b>Similar Questions</b></a>
            </div>

   <!--<button type="button" style="color:white;float:right;margin-top:15px;" class="close" onclick="location.href = '/thanks/';"
      aria-hidden="true">
      &times;
   </button>-->


    </div>
    <!--end of top navbar contents--->
</div>
                           <div class="container"> <div class="panel panel-default" style="margin-left:40px;margin-top:80px;background:#CC3232;color:white;"><div class="panel-heading" style="background:#CC3232;overflow:hidden;"><ul class="list-unstyled">%s</ul>
                                        <div class="row pull-right">

                                             <div class="col-md-12">
                                                <div class="ui-group-buttons">
                                                        <a href="#" class="btn btn-success" id="accept" onclick="location.href = '/save/%s/%s/%s/%s/';" role="button">Agree</a>
                                                        <div class="or"></div>
                                                         <a href="3" class="btn btn-danger" id="decline" onclick="location.href = '/thanks/';"  role="button">Disagree</a>
                                                </div>
                                             </div>
                                        </div>
<!--<button type="button" class="btn btn-default pull-right" style="color:#CC3232;" onclick="location.href = '/save/%s/%s/%s/%s/';">My Question is new</button>--></div></div></div>
                            <script src="//ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js"></script>
   <script src="//netdna.bootstrapcdn.com/bootstrap/3.0.0/js/bootstrap.min.js"></script>
<script src="//cdnjs.cloudflare.com/ajax/libs/bootstrap-select/1.6.3/js/bootstrap-select.min.js"></script></body></html>
                                    """ % ('\n'.join(k), topic, tag,access, qid)
                 return HttpResponse(h)
                else:
                 rate=0
                 b = questions(rate1=rate, qid=qid, question=r, topic=topic, tag=tag, access=access,
                              timestamp=timezone.now(), uid_id=request.session['ra_no'])
                 b.save()

                #saving avgrating of this question into avgrating_questions table
                 a2 = avgrating_questions(qid_id=qid, avg_rating=rate)
                 a2.save()

                 a3 = reviewing_ques(qid_id=qid)
                 a3.save()

                 #saving into notification table
                 n = notification(message="question added ", timestamp=timezone.now(), created_on=qid,
                                 creator=request.session['ra_no'], created_as=qid, viewed=False)
                 n.save()


                 try:
                   sim_topic = newsfeed_score.objects.get(word=topic, uid_id=request.session['ra_no'])
                   k = sim_topic.score
                   s = ast.literal_eval(k)
                   s = s + 10
                   sim_topic.delete()
                   a4 = newsfeed_score(uid_id=request.session['ra_no'], word=topic, score=s)
                   a4.save()
                 except:
                   a5 = newsfeed_score(uid_id=request.session['ra_no'], word=topic, score=10)
                   a5.save()

                 tags = tag.split(',')
                 for a in tags:
                  try:
                    sim_tags = newsfeed_score.objects.get(word=a, uid_id=request.session['ra_no'])
                    k = sim_tags.score
                    s = ast.literal_eval(k)
                    s = s + 5
                    sim_tags.delete()
                    a4 = newsfeed_score(uid_id=request.session['ra_no'], word=a, score=s)
                    a4.save()
                  except:
                    a5 = newsfeed_score(uid_id=request.session['ra_no'], word=a, score=5)
                    a5.save()



                return HttpResponseRedirect('/thanks/')


#procedure after following question
def follow_question(request, qid):
    y_list = []
    q_list = []
    pre = request.session['ra_no']
    ques1 = questions.objects.get(qid = qid)
    user = ques1.uid_id
    if user == pre:
        return HttpResponse(
            "<html><head><script type='text/javascript'> alert('You cannot follow the question you have posted'); window.location = '/thanks/';</script></head></html>")

    q_list += questions.objects.filter(uid_id=pre).values_list('qid', flat=True).distinct()
    if qid not in q_list:
        #updating the tracking_question in 's' table
        a = regis.objects.get(uid=pre)
        a.tracking_ques.append(qid)
        a.save()

        #updating tracked_by in question table
        q1 = questions.objects.get(qid=qid)
        f_list = q1.tracked_by
        for x in f_list:
            q = ast.literal_eval(x)
            y_list.append(q)
        if int(pre) not in y_list:
            q1.tracked_by.append(pre)
            q1.save()
            return HttpResponseRedirect('/thanks/')
        else:
            return HttpResponse(
            "<html><head><script type='text/javascript'> alert('You have already followed this question'); window.location = '/thanks/';</script></head></html>")

    else:
        return HttpResponseRedirect('/thanks/')





#login
def login(request):
    c = {}
    c.update(csrf(request))
    return render_to_response('login.html', c)


#authentication of email id and password while logging in
def auth_view(request):
    try:
        n = request.POST['username']
        m = regis.objects.get(email=n)
        ra_no = m.uid
        request.session['ra_no'] = ra_no
        full_name = m.username
        request.session['full_name'] = full_name

        if m.password1 == request.POST['password']:

            return HttpResponseRedirect('/accounts/loggedin')

        else:
            return HttpResponse(
                "<script>alert('Kindly recheck your password');window.location = '/accounts/register/';</script>")

    except:
        return HttpResponse(
            "<script>alert('Kindly recheck your email id');window.location = '/accounts/register/';</script>")


def loggedin(request):
    HttpResponseRedirect('/accounts/loggedin')


def invalid_login(request):
    return render_to_response('invalid_login.html')


#register the user (forms.py & register.html)
def register_user(request):
    if request.method == 'POST':
        form = MyRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse(
                "<html><head><script type='text/javascript'> alert('Registration done successfully. Check your mail.'); window.location = '/accounts/register/';</script></head></html>")

    else:
        form = MyRegistrationForm()
    args = {}
    args.update(csrf(request))
    args['form'] = form
    return render_to_response('register.html', args)


#def register_success(request):
#return render_to_response('register_success.html')





def post_answer(request, qid):
    rate = 0
    q = 0
    count = 0
    if 'textbox' in request.GET and request.GET['textbox']:
        answer = request.GET['textbox']

        #if 'topic1' in request.GET and request.GET['topic1']:
        #topic = request.GET['topic1']
        #if 'tag1' in request.GET and request.GET['tag1']:
        #tag = request.GET['tag1']
        #if 'submitanswer' in request.GET and request.GET['submitanswer']:
        #qid = request.GET['submitanswer']

        #if answer == None:
        #return HttpResponse("<html><head><script type='text/javascript'> alert('Type to Answer');window.location = '/thanks/';</script></head></html>")

    #contractions
    dict_contract={}
    with open("contractions.txt", "r") as r:
      for line in r:
          list_d = line.split(',')
          dict_contract.update({list_d[0]:list_d[1]})


    for k,v in dict_contract.iteritems():
          if k in answer:
             answer = string.replace(answer,k,v)







    bad_words = []
    answer_list = answer.split()
    for each in answer_list:
        #c = profanity_filter.Filter(each, clean_word='unicorn')
        #w = c.clean()
        #word = str(w)
        bad_names = [line.strip() for line in open('bad_words.txt')]
        if str(each) in bad_names or '*' in list(str(each)):

            bad_words.append(str(each))
    if len(bad_words) != 0:
            return HttpResponse("<html><head><script type='text/javascript'> alert('Kindly Restrict the usage of following words in your answer: \t' + %s);window.location = '/thanks/';</script></head></html>" % bad_words)



    random_no = randint(0000000, 9999999);
    aid = random_no
    #qid = request.GET.get('qid')
    #qid = request.session['qid']

    #if 'clicked_id' in request.GET and request.GET['clicked_id']:
    #qid = request.GET['clicked_id']

    if 'rate' in request.GET and request.GET['rate']:
        rate = request.GET['rate']

    q1 = questions.objects.get(qid=qid)
    summarized_answer = textsummarizer.summarized(q1.question, answer)



    #return HttpResponse(qid)
    d = answers(rate=rate, aid=aid, answer=answer, answer_summary=summarized_answer, timestamp=timezone.now(),
                uid_id=request.session['ra_no'], qid_id=qid)
    d.save()

    #saving avgrating of this answer into avgrating_answers table
    a2 = avgrating_answers(aid_id=aid, avg_rating=q)
    a2.save()

    a3 = reviewing_ans(aid_id=aid, qid_id=qid)
    a3.save()
    #saving into notification table
    n = notification(message="answer added to your question", timestamp=timezone.now(),
                     creator=request.session['ra_no'], created_on=qid, created_as=aid, viewed=False)
    n.save()

    #n = notification(message="answer added",timestamp=timezone.now(),creator=request.session['ra_no'],created_on=qid,created_as=aid,viewed=False)
    #n.save()



    try:
     sim_topic = newsfeed_score.objects.get(word=q1.topic,uid_id=request.session['ra_no'])
     k=sim_topic.score
     s = ast.literal_eval(k)
     s=s+5
     sim_topic.delete()
     a4 = newsfeed_score(uid_id=request.session['ra_no'],word=q1.topic,score=s)
     a4.save()
    except:
     a5 = newsfeed_score(uid_id=request.session['ra_no'],word=q1.topic,score=5)
     a5.save()

    tags =q1.tag.split(',')

  #return HttpResponse(tags)

    for a in tags:
      try:
       sim_tags = newsfeed_score.objects.get(word=a,uid_id=request.session['ra_no'])
       k=sim_tags.score
       s = ast.literal_eval(k)
       s=s+1
       sim_tags.delete()
       a4 = newsfeed_score(uid_id=request.session['ra_no'],word=a,score=s)
       a4.save()
      except:
       a5 = newsfeed_score(uid_id=request.session['ra_no'],word=a,score=1)
       a5.save()

    return HttpResponseRedirect('/thanks/')


#rating of answer
def rate_answer(request, aid):
    indiv_rating_a = []
    y_list = []
    a1 = answers.objects.get(aid=aid)
    av = avgrating_answers.objects.get(aid_id=aid)
    pre_user = request.session['ra_no']
    if pre_user != a1.uid_id:
        u_list = av.uid
        for x in u_list:
            q = ast.literal_eval(x)
            y_list.append(q)

        r_list = av.a_rating

        if int(pre_user) not in y_list:  # this
            if 'rate' in request.GET and request.GET['rate']:
                r = request.GET['rate']
                av.a_rating.append(r)
                av.aid_id = aid
                av.uid.append(request.session['ra_no'])
                for y in r_list:
                    s = ast.literal_eval(y)
                    indiv_rating_a.append(s)
                av.avg_rating = sum(indiv_rating_a) / float(len(indiv_rating_a))
                a1.rate = sum(indiv_rating_a) / float(len(indiv_rating_a))
                a1.save()
                av.save()
                ms = myscore(uid_id=a1.uid_id,rate=r,date=timezone.now())
                ms.save()
                n = notification(message="Rating of your answer ", timestamp=timezone.now(), creator=pre_user,
                                 created_on=a1.qid_id, created_ona=aid, created_as=r, viewed=False)
                n.save()

                return HttpResponseRedirect('/thanks/')
        elif int(pre_user) in y_list:  #this is that
            return HttpResponse(
                "<html><head><script type='text/javascript'> alert('You have already rated this answer'); window.location = '/thanks/';</script></head></html>")
    elif pre_user == a1.uid_id:
        return HttpResponse(
            "<html><head><script type='text/javascript'> alert('You cannot rate the answer you have posted'); window.location = '/thanks/';</script></head></html>")


#rating of question
def rate_question(request, qid):
    yes = 0
    y_list = []
    p_list = []
    indiv_rating_q = []
    a1 = questions.objects.get(qid=qid)
    av = avgrating_questions.objects.get(qid_id=qid)
    pre_user = request.session['ra_no']
    if pre_user != a1.uid_id:

        u_list = av.uid
        for x in u_list:
            q = ast.literal_eval(x)
            y_list.append(q)

        r_list = av.q_rating

        if int(pre_user) not in y_list:  # this
            if 'rateq' in request.GET and request.GET['rateq']:
                r = request.GET['rateq']
                av.q_rating.append(r)
                av.qid_id = qid
                av.uid.append(request.session['ra_no'])
                for y in r_list:
                    s = ast.literal_eval(y)
                    indiv_rating_q.append(s)
                av.avg_rating = sum(indiv_rating_q) / float(len(indiv_rating_q))
                a1.rate1 = sum(indiv_rating_q) / float(len(indiv_rating_q))
                a1.save()
                av.save()
                ms = myscore(uid_id=a1.uid_id,rate=r,date=timezone.now())
                ms.save()
                n = notification(message="Rating of your question ", timestamp=timezone.now(), creator=pre_user,
                                 created_on=qid, created_as=r, viewed=False)
                n.save()
                return HttpResponseRedirect('/thanks/')
        elif int(pre_user) in y_list:  #this is that

            return HttpResponse(
                "<html><head><script type='text/javascript'> alert('You have already rated this Question'); window.location = '/thanks/';</script></head></html>")



    elif pre_user == a1.uid_id:
        return HttpResponse(
            "<html><head><script type='text/javascript'> alert('You cannot rate the question you have posted'); window.location = '/thanks/';</script></head></html>")





def tab2(request):
    qid_list = []
    user = request.session['ra_no']
    q_list = questions.objects.filter(uid_id=user).values_list('qid', flat=True).distinct()

    #for following a person all his questions,answers are notified
    f_list = regis.objects.get(uid=user)
    #notifications for answering or rating ur questions

    #rating ur answers
    a_list = answers.objects.filter(uid_id=user).values_list('aid', flat=True).distinct()

    per_list = notification.objects.all().order_by('-timestamp')
    a = regis.objects.get(uid=user)
    track_ques = a.tracking_ques
    count=0
    count_list = notification.objects.filter(viewed=0)
    for c in count_list:
        if c.created_on in q_list and user != c.creator or c.created_on == user or c.created_ona in a_list or c.created_on in track_ques:
            count=count+1
        request.session['count'] = count

    return render(request, 'noti1.html',
                  {'full_name': request.session['full_name'],'count':request.session['count'],'f_list': f_list, 'q_list': q_list, 'per_list': per_list,
                   'a_list': a_list, 'user': user, 'qid_list': qid_list, 'track_ques': track_ques})


def single(request, qid, id):
    n = notification.objects.get(id=id)
    n.viewed = 1
    n.save()
    suggest_ques=""
    suggest_ans = ""
    try:
     q = questions.objects.get(qid=qid)
     a = answers.objects.filter(qid_id=qid)
     suggest_ques = n.suggested
    except:
     a=answers.objects.filter(aid=qid)
     for a1 in a:
      q=questions.objects.get(qid=a1.qid_id)
     suggest_ans = n.suggested
    user = request.session['ra_no']

    return render(request, 'notification.html', {'suggest_ans':suggest_ans,'full_name': request.session['full_name'], 'q': q, 'a': a,'count':request.session['count'],'suggest_ques':suggest_ques,'id':id})


def single1(request, qid):
    q = questions.objects.get(qid=qid)
    a = answers.objects.filter(qid_id=qid)

    return render(request, 'similar_questions.html', {'q': q, 'a': a,'full_name': request.session['full_name']})

def singleq_activities(request,id):
    q = questions.objects.get(qid=id)
    a = answers.objects.filter(qid_id=id)


    return render(request,'activities_single.html',{'full_name': request.session['full_name'],'q':q,'a':a,'count':request.session['count']})

def singlea_activities(request,id):
    a = answers.objects.get(aid=id)
    q = questions.objects.get(qid=a.qid_id)


    return render(request,'activities_asingle.html',{'full_name': request.session['full_name'],'q':q,'a':a,'count':request.session['count']})


"""
def noti(request,uid,id):
    n = notification.objects.get(id=id)
    n.viewed=1
    n.save()
    msg = n.message
    return render(request,'notification1.html',{'full_name':request.session['full_name'],'msg':msg,'uid':uid})
"""

"""
def book_markq(request,id,anystring):
    pre = request.session['ra_no']
    s = book_mark(uid_id=pre,qid_id=id,aid_id=null,label=anystring)
    s.save()
    return HttpResponseRedirect('/thanks/')

def book_marka(request,id,anystring):
    pre = request.session['ra_no']
    s = book_mark(uid_id=pre,qid_id="",aid_id=id,label=anystring)
    s.save()
    return HttpResponseRedirect('/thanks/')

def book(request):

    q_list = []
    ques_list = []
    a_list = []
    pre = request.session['ra_no']
    p = regis.objects.get(uid=pre)
    for x in p.book_markq:
      q_list += questions.objects.filter(qid=x)
    for y in q_list:
      a_list += answers.objects.filter(qid_id=y.qid)
    #q_list = set(q_list)
      #q_list += questions.objects.filter(qid=x.qid_id)
    #for q in q_list:
        #ques_list += questions.objects.filter(qid=q)
    #for a in ques_list:
            #ans_list += answers.objects.filter(qid_id=a.qid).filter(uid_id=id)


    return render(request,'book.html',{'q_list':q_list,'id':id,'ques_list':ques_list,'a_list':a_list})

    q_list = []
    a_list = []
    id = request.session['ra_no']
    p = book_mark.objects.get(uid_id=id)
    for x in p.qid:
        q_list += questions.objects.filter(qid=x)
    for y in q_list:
        a_list += answers.objects.filter(qid_id=y.qid)


    for z in p.aid:
        a_list += answers.objects.filter(aid=z)
    for k in a_list:
        q_list += questions.objects.filter(qid=k.qid_id)
    q_list = set(q_list)
    a_list = set(a_list)



    return render(request,'book.html',{'full_name':request.session['full_name'],'q_list':q_list,'a_list':a_list})
"""


def book_markq(request, qid):
    try:
        book_mark1 = book_mark.objects.get(qid_id=qid)
        #return HttpResponse(book_mark1)
        user = book_mark1.uid_id
        if user == request.session['ra_no']:
            return HttpResponse(
                "<html><head><script type='text/javascript'> alert('You have already bookmarked this question'); window.location = '/thanks/';</script></head></html>")
        else:
            label = ""
            if 'label' in request.GET and request.GET['label']:
                label = request.GET['label']
            pre = request.session['ra_no']
            s = book_mark(uid_id=pre, qid_id=qid, aid_id="null", label=label)
            s.save()
            return HttpResponseRedirect('/thanks/')
    except:
        label = ""
        if 'label' in request.GET and request.GET['label']:
            label = request.GET['label']
        pre = request.session['ra_no']
        s = book_mark(uid_id=pre, qid_id=qid, aid_id="null", label=label)
        s.save()
        return HttpResponseRedirect('/thanks/')


def book_marka(request, aid):
    """
    label=""
    if 'labela' in request.GET and request.GET['labela']:
        label = request.GET['labela']
    pre = request.session['ra_no']
    s = book_mark(uid_id=pre,qid_id="null",aid_id=aid,label=label)
    s.save()

    return HttpResponseRedirect('/thanks/')
    """
    try:
        book_mark1 = book_mark.objects.get(aid_id=aid)
        user = book_mark1.uid_id
        if user == request.session['ra_no']:
            return HttpResponse(
                "<html><head><script type='text/javascript'> alert('You have already bookmarked this Answer'); window.location = '/thanks/';</script></head></html>")
        else:
            label = ""
            if 'labela' in request.GET and request.GET['labela']:
                label = request.GET['labela']
            pre = request.session['ra_no']
            s = book_mark(uid_id=pre, qid_id="null", aid_id=aid, label=label)
            s.save()
            return HttpResponseRedirect('/thanks/')
    except:
        label = ""
        if 'labela' in request.GET and request.GET['labela']:
            label = request.GET['labela']
        pre = request.session['ra_no']
        s = book_mark(uid_id=pre, qid_id="null", aid_id=aid, label=label)
        s.save()
        return HttpResponseRedirect('/thanks/')


def book_id(request):
    q1_list = []
    a1_list = []
    a2_list = []
    label_list = {}
    label_list_table = []
    id = request.session['ra_no']
    p = book_mark.objects.filter(uid=id)
    if p:
     for p1 in p:
        if p1.qid_id != "null":
            q2_list = questions.objects.get(qid=p1.qid_id)
            try:
                a2_list = answers.objects.filter(qid_id=q2_list.qid)
            except answers.DoesNotExist:
                a2_list = ""
            q1_list.append(q2_list)
            for an2 in a2_list:
             a1_list.append(an2)

        if p1.aid_id != "null":
            a3_list = answers.objects.get(aid=p1.aid_id)
            q3_list = questions.objects.get(qid=a3_list.qid_id)
            q1_list.append(q3_list)
            a1_list.append(a3_list)
    q4_list = set(q1_list)
    a4_list = set(a1_list)

    for l in p:
        if l.qid_id != "null":
            label_list.update({l.qid_id: l.label})
        else:
            label_list.update({l.aid_id: l.label})

    for l1 in p:
        label_list_table.append(l1.label)
    return render(request, 'book.html',
                  {'full_name': request.session['full_name'], 'q_list': q4_list, 'a_list': a4_list,'count':request.session['count'],
                   'label_list': label_list.iteritems(), 'label_list_table': set(label_list_table)})


def book_label(request, anystring):
    q1_list = []
    a1_list = []
    label_list = {}
    label_list_table = []
    id = request.session['ra_no']
    p = book_mark.objects.filter(uid=id).filter(label=anystring)
    for p1 in p:
        if p1.qid_id != "null":
            q2_list = questions.objects.get(qid=p1.qid_id)
            try:
                a2_list = answers.objects.filter(qid_id=q2_list.qid)
            except answers.DoesNotExist:
                a2_list = ""
            q1_list.append(q2_list)
            for an2 in a2_list:
             a1_list.append(an2)

        if p1.aid_id != "null":
            a3_list = answers.objects.get(aid=p1.aid_id)
            q3_list = questions.objects.get(qid=a3_list.qid_id)
            q1_list.append(q3_list)
            a1_list.append(a3_list)
    q4_list = set(q1_list)
    a4_list = set(a1_list)

    for l in p:
        if l.qid_id != "null":
            label_list.update({l.qid_id: l.label})
        else:
            label_list.update({l.aid_id: l.label})
    p_all = book_mark.objects.filter(uid=id)
    for l1 in p_all:
        label_list_table.append(l1.label)
    return render(request, 'book1.html',
                  {'full_name': request.session['full_name'], 'q_list': q4_list, 'a_list': a4_list,'count':request.session['count'],
                   'label_list': label_list.iteritems(), 'label_list_table': set(label_list_table)})


def download_qa(request, aid):
    get_answer = answers.objects.get(aid=aid)
    get_question = questions.objects.get(qid=get_answer.qid_id)

    file_name = 'RAL.txt'
    with open(file_name, 'a') as fout:
        fout.write("\n"+"Your Downloaded Answer"+"\n")
        fout.write("\n"+"Question"+"\n")
        fout.write(get_question.question+"\n")
        fout.write("\n"+"Answer"+"\n")
        fout.write("\n"+get_answer.answer+"\n")
    fout.close()
    testfile = urllib.URLopener()
    testfile.retrieve("/home/kruthika/Documents/python/django-kruthika/testproject/RAL.txt",
                      "/home/kruthika/Downloads/RAL_download.txt")

    return HttpResponseRedirect('/thanks/')

def download_q(request, qid):
    answer_list = []
    get_question = questions.objects.get(qid=qid)
    #get_question = answers.objects.get(qid=get_answer.qid_id)
    answer_list += answers.objects.filter(qid_id=qid).values_list('answer', flat=True)

    file_name = 'RALq.txt'
    with open(file_name, 'a') as fout:
        fout.write("\n"+"Your Downloaded Question"+"\n")
        fout.write("\n"+"Question"+"\n")
        fout.write(get_question.question+"\n")
        fout.write("\n"+"Answer"+"\n")
        for answer in answer_list:

            fout.write("\n"+"".join(answer)+"\n")
        #fout.write(answer_list)
    fout.close()
    testfile = urllib.URLopener()
    testfile.retrieve("/home/kruthika/Documents/python/django-kruthika/testproject/RALq.txt",
                      "/home/kruthika/Downloads/RALq_download.txt")

    return HttpResponseRedirect('/thanks/')

#review ques
def reviewq(request, qid):
    p = []

    r_list = []
    u_list = []
    ques = questions.objects.get(qid=qid)
    d = reviewing_ques.objects.get(qid_id=qid)
    reviewguy = request.session['ra_no']
    if ques.uid_id == reviewguy:
        return HttpResponseRedirect('/thanks/')
    else:
        if 'review1' in request.GET and request.GET['review1']:
            n = request.GET['review1']
            p = pos_tag(n.split())
            r = [s for s in p if
                 s[1] == 'ADJ' or s[1] == 'JJR' or s[1] == 'JJS' or s[1] == 'JJ' or s[1] == 'NN' or s[1] == 'NNS' or s[
                     1] == 'NNP' or s[1] == 'NNPS']
            #return render(request,'wordcloud.html',{'p':p})
            r_list = d.remarks
            u_list = d.uids
            #if reviewguy not in u_list:
            d.uids.append(reviewguy)
            for k, j in r:
                d.remarks.append(k)
                d.save()
            return HttpResponseRedirect('/thanks/')
            #else:
                #return HttpResponseRedirect('/thanks/')

        return HttpResponseRedirect('/thanks/')


#create dictionary of words with count for word cloud
def word_cloud(request, qid):
    af = []
    ay = []
    questions1 = []
    #list of qid's of answers
    an_list = []
    uid = request.session['ra_no']
    #whole row of info of user from 's' table
    fol_list = regis.objects.get(uid=uid)
    #All the qids posted by me
    myqlist = questions.objects.filter(uid_id=uid).filter(access="interest").values_list('topic', flat=True).distinct()
    books_list = questions.objects.all().order_by('-timestamp')
    avg = avgrating_answers.objects.all().order_by('-avg_rating')
    avg1 = avgrating_questions.objects.all()
    revq = reviewing_ques.objects.all()
    reva = reviewing_ans.objects.all()
    ans_list = answers.objects.all().order_by('-timestamp')
    an_list += answers.objects.values_list('qid_id', flat=True).distinct()
    #All the qids for which persons('u') have answered, whom user's(currently logged in) is following
    #for u in fol_list.tracking:
        #af += answers.objects.filter(uid_id=u).values_list('qid_id', flat=True).distinct()

    interest = newsfeed_score.objects.filter(uid_id=uid).values_list('word').order_by('score')[:100]

    books_list1 = questions.objects.all().order_by('-timestamp')
    for k in interest:
        questions1 += questions.objects.filter(topic=k).values_list('qid').distinct()
    #return HttpResponse(questions1)

    for a in interest:
        questions1 += questions.objects.filter(tag=a)

    for a in questions1:
        qid = a.qid
        ay += answers.objects.filter(qid_id=qid)


    r_list = []
    q_list = []
    k_list = []
    p = []
    counts = {}
    reviewguy = request.session['ra_no']
    r = reviewing_ques.objects.filter(qid_id=qid)
    for p in r:
        r_list += p.remarks

    q = reviewing_ans.objects.filter(qid_id=qid)
    for p in q:
        q_list += p.remarks

    k_list = r_list + q_list
    counts = Counter(k_list)

    return render(request, 'newsfeed.html',
                  {'interest': interest, 'questions1': questions1, 'ay': ay, 'revq': revq, 'reva': reva,
                   'books_list': books_list, 'full_name': request.session['full_name'],
                   'ra_no': request.session['ra_no'], 'ans_list': ans_list, 'avg': avg, 'avg1': avg1, 'uid': uid,
                   'fol_list': fol_list, 'myqlist': myqlist, 'af': af, 'an_list': an_list, 'counts': counts.iteritems(), 'reviewguy': reviewguy})



#review answer
def reviewa(request, aid):
    r_list = []
    u_list = []
    ques = answers.objects.get(aid=aid)
    d = reviewing_ans.objects.get(aid_id=aid)
    reviewguy = request.session['ra_no']
    if ques.uid_id == reviewguy:
        return HttpResponseRedirect('/thanks/')
    else:
        if 'review2' in request.GET and request.GET['review2']:
            n = request.GET['review2']
            p = pos_tag(n.split())
            r = [s for s in p if
                 s[1] == 'ADJ' or s[1] == 'JJR' or s[1] == 'JJS' or s[1] == 'JJ' or s[1] == 'NN' or s[1] == 'NNS' or s[
                     1] == 'NNP' or s[1] == 'NNPS']
            r_list = d.remarks
            u_list = d.uids
            if reviewguy not in u_list:
                d.uids.append(reviewguy)
                for k, j in r:
                    d.remarks.append(k)
                d.save()
                return HttpResponseRedirect('/thanks/')
            else:
                return HttpResponseRedirect('/thanks/')

        return HttpResponseRedirect('/thanks/')


def saved(request, topic, tag,access, qid):
    rate = 0
    #ques = "Kruthika"
    #saving into database

    b = questions(rate1=rate, qid=qid, question=request.session['ques'], topic=topic, tag=tag, access=access,
                  timestamp=timezone.now(), uid_id=request.session['ra_no'])
    b.save()

    #saving avgrating of this question into avgrating_questions table
    a2 = avgrating_questions(qid_id=qid, avg_rating=rate)
    a2.save()

    a3 = reviewing_ques(qid_id=qid)
    a3.save()

    #saving into notification table
    n = notification(message="question added ", timestamp=timezone.now(), created_on=qid,
                     creator=request.session['ra_no'], created_as=qid, viewed=False)
    n.save()

    #score for topic in newsfeed entry table

    try:
        sim_topic = newsfeed_score.objects.get(word=topic, uid_id=request.session['ra_no'])
        k = sim_topic.score
        s = ast.literal_eval(k)
        s = s + 10
        sim_topic.delete()
        a4 = newsfeed_score(uid_id=request.session['ra_no'], word=topic, score=s)
        a4.save()
    except:
        a5 = newsfeed_score(uid_id=request.session['ra_no'], word=topic, score=10)
        a5.save()

    tags = tag.split(',')

    for a in tags:
        try:
            sim_tags = newsfeed_score.objects.get(word=a, uid_id=request.session['ra_no'])
            k = sim_tags.score
            s = ast.literal_eval(k)
            s = s + 5
            sim_tags.delete()
            a4 = newsfeed_score(uid_id=request.session['ra_no'], word=a, score=s)
            a4.save()
        except:
            a5 = newsfeed_score(uid_id=request.session['ra_no'], word=a, score=5)
            a5.save()
    return HttpResponseRedirect('/thanks/')



"""
def delete_alert(request,qid):
    qid1 = qid
    return HttpResponse("<html><head><script type='text/javascript'> alert('Are you sure of deleting?');window.location = '/deleteq1/%s';</script></head></html>" %qid1)
"""
def delete_alert1(request,qid):
    ques1 = questions.objects.get(qid = qid)

    ques1.delete()

    return HttpResponse("<html><head><script type='text/javascript'> alert('Question deleted');window.location = '/tab_2/';</script></head></html>")

"""
def deletea_alert(request,aid):
    aid1 = aid
    return HttpResponse("<html><head><script type='text/javascript'> alert('Are you sure of deleting?');window.location = '/deletea1/%s';</script></head></html>" %aid1)
"""

def deletea_alert1(request,aid):
    ans = answers.objects.get(aid = aid)

    ans.delete()

    return HttpResponse("<html><head><script type='text/javascript'> alert('Answer deleted');window.location = '/tab_2/';</script></head></html>")

def edit_ques(request,qid):

    a1 = questions.objects.get(qid =qid)

    if 'edit_question' in request.GET and request.GET['edit_question']:
        ques = request.GET['edit_question']
    #return HttpResponse(ques)
    #profanity

    bad_words = []
    question_list = ques.split()
    for each in question_list:
        bad_names = [line.strip() for line in open('bad_words.txt')]
        if str(each) in bad_names or '*' in list(str(each)):
            bad_words.append(str(each))
    if len(bad_words) != 0:
     return HttpResponse(
                "<html><head><script type='text/javascript'> alert('Kindly Restrict the usage of following words in your question: \t' + %s);window.location = '/tab_2';</script></head></html>" % bad_words)


    a1.question = ques
    a1.save()

    return HttpResponseRedirect('/tab_2/')

def edit_ans(request,aid):

    a2 = answers.objects.get(aid =aid)

    if 'edit_answer' in request.GET and request.GET['edit_answer']:
        ans = request.GET['edit_answer']

    bad_words = []
    question_list = ans.split()
    for each in question_list:
        bad_names = [line.strip() for line in open('bad_words.txt')]
        if str(each) in bad_names or '*' in list(str(each)):
            bad_words.append(str(each))
    if len(bad_words) != 0:
     return HttpResponse(
                "<html><head><script type='text/javascript'> alert('Kindly Restrict the usage of following words in your question: \t' + %s);window.location = '/tab_2';</script></head></html>" % bad_words)


    a2.answer = ans
    a2.save()

    return HttpResponseRedirect('/tab_2/')



def edit_sques(request,qid):

    q1 = questions.objects.get(qid =qid)
    user = q1.uid_id
    if 'suggest_question' in request.GET and request.GET['suggest_question']:
        ques_suggest = request.GET['suggest_question']

    #profanity

    bad_words = []
    question_list = ques_suggest.split()
    for each in question_list:
        bad_names = [line.strip() for line in open('bad_words.txt')]
        if str(each) in bad_names or '*' in list(str(each)):
            bad_words.append(str(each))
    if len(bad_words) != 0:
     return HttpResponse(
                "<html><head><script type='text/javascript'> alert('Kindly Restrict the usage of following words in your question: \t' + %s);window.location = '/tab_1/';</script></head></html>" % bad_words)



    b1 = notification(message="Your Question received a suggest",timestamp =timezone.now(),creator =request.session['ra_no'],created_on = qid,created_ona = "",created_as="",suggested=ques_suggest)
    b1.save()
    return HttpResponseRedirect('/thanks/')






#editing answers suggested ones
def edit_sans(request,aid):

    a1 = answers.objects.get(aid =aid)
    user = a1.uid_id
    if 'edit_answer' in request.GET and request.GET['edit_answer']:
        ans_suggest = request.GET['edit_answer']

    #profanity

    bad_words = []
    question_list = ans_suggest.split()
    for each in question_list:
        bad_names = [line.strip() for line in open('bad_words.txt')]
        if str(each) in bad_names or '*' in list(str(each)):
            bad_words.append(str(each))
    if len(bad_words) != 0:
     return HttpResponse(
                "<html><head><script type='text/javascript'> alert('Kindly Restrict the usage of following words in your question: \t' + %s);window.location = '/tab_1';</script></head></html>" % bad_words)



    b1 = notification(message="Your Answer received a suggest",timestamp =timezone.now(),creator =request.session['ra_no'],created_on = aid,created_ona = aid,created_as="",suggested=ans_suggest)
    b1.save()
    return HttpResponseRedirect('/thanks/')

#edit accept
def edit_accept(request,qid,id):
     n = notification.objects.get(id=id)
     try:
      q1 = questions.objects.get(qid =qid)
      q1.question = n.suggested
      q1.save()
      r = "Your question has been edited"
     except:
      a1 = answers.objects.get(aid=qid)
      a1.answer = n.suggested
      a1.save()
      r = "Your answer has been edited"

     s1 = myscore(uid_id = n.creator,rate = 10,date=datetime.today())
     s1.save()
     #further may change
     b1 = notification(message="Your suggestion has been accepted",timestamp =timezone.now(),creator =request.session['ra_no'],created_on =n.creator ,created_ona = "",created_as="",suggested="")
     b1.save()
     n.delete()


     return HttpResponse(
                "<html><head><script type='text/javascript'> alert('%s');window.location = '/thanks/';</script></head></html>"%r)

#edit reject
def edit_reject(request,qid,id):
     n = notification.objects.get(id=id)
     m = myscore(uid_id=n.creator,rate = -5,date=datetime.today())
     m.save()
     b1 = notification(message="Your suggestion has been rejected",timestamp =timezone.now(),creator =request.session['ra_no'],created_on =n.creator ,created_ona = "",created_as="",suggested="")
     b1.save()
     n.delete()
     return HttpResponseRedirect('/thanks/')
