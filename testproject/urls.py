from django.conf.urls import patterns, include, url
from django.contrib import admin
#import notifications
admin.autodiscover()


urlpatterns = patterns('',

    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$','books.views.login'),
    url(r'^accounts/auth/$','books.views.auth_view'),
    url(r'^accounts/loggedin/$','books.views.tab_1'),
    url(r'^accounts/loggedin/$','books.views.loggedin'),
    url(r'^log/$','books.views.post_question'),
    #url(r'^logtag/(?P<anystring>.+?)/$','books.views.auto_tag'),
    url(r'^log1/(?P<qid>\d+)/$','books.views.follow_question'),

    url(r'^thanks/$','books.views.tab_1'),
    url(r'^thanks/$','books.views.post_question'),
    url(r'^accounts/follow/(?P<uid>\d+)/$','books.views.follow'),
    url(r'^accounts/logout/$','books.views.logout'),
    url(r'^accounts/profile/$','books.views.profile'),
    #url(r'^bookmark/$','books.views.book'),
    #url(r'^accounts/bookmarkq/(?P<id>\d+)/(?P<anystring>.+?)/$','books.views.book_markq'),
    #url(r'^accounts/bookmarka/(?P<id>\d+)/(?P<anystring>.+?)/$','books.views.book_marka'),
    url(r'^accounts/invalid/$','books.views.invalid_login'),

    url(r'^accounts/register/$','books.views.register_user'),
    #url(r'^accounts/register_success/$', 'books.views.register_success'),
    url(r'^tab_2/$','books.views.tab_2'),
    url(r'^tab2/$','books.views.tab2'),
    url(r'^tab_1/$','books.views.tab_1'),
    url(r'^tab_4/$','books.views.tab_4'),
    #passing qid to post answer
    url(r'^post_answer/$','books.views.post_answer'),
    url(r'^post_answer/(?P<qid>\d+)/$','books.views.post_answer'),
    url(r'^post_answer/like/(?P<aid>\d+)/$','books.views.like'),
    url(r'^post_answer/rate_answer/(?P<aid>\d+)/$','books.views.rate_answer'),
    url(r'^quest/rate_question/(?P<qid>\d+)/$','books.views.rate_question'),
    url(r'^single/(?P<qid>\d+)/(?P<id>\d+)/$','books.views.single'),
    url(r'^log/single1/(?P<qid>\d+)/$','books.views.single1'),
    #url(r'^noti_follow/(?P<uid>\d+)/(?P<id>\d+)/$','books.views.noti'),
    url(r'^download/(?P<aid>\d+)/$','books.views.download_qa'),
    url(r'^downloadq/(?P<qid>\d+)/$','books.views.download_q'),
    url(r'^accounts/reviewq/(?P<qid>\d+)/$','books.views.reviewq'),
    url(r'^accounts/reviewa/(?P<aid>\d+)/$','books.views.reviewa'),
    url(r'^accounts/loggedin/word_cloud/(?P<qid>\d+)/$','books.views.word_cloud'),
    url(r'^word_cloud/(?P<qid>\d+)/$','books.views.word_cloud'),
    url(r'^tab_1/word_cloud/(?P<qid>\d+)/$','books.views.word_cloud'),
    url(r'^save/(?P<topic>.+?)/(?P<tag>.+?)/(?P<access>.+?)/(?P<qid>\d+)/$','books.views.saved'),
    url(r'^bookmark/$','books.views.book_id'),
    url(r'^bookmark_label/(?P<anystring>.+?)/$','books.views.book_label'),
    url(r'^accounts/bookmarkq/(?P<qid>\d+)/$','books.views.book_markq'),
    url(r'^accounts/bookmarka/(?P<aid>\d+)/$','books.views.book_marka'),
    url(r'^tab_2/singleq/(?P<id>\d+)/$','books.views.singleq_activities'),
    url(r'^tab_2/singlea/(?P<id>\d+)/$','books.views.singlea_activities'),
    url(r'^deleteq/(?P<qid>\d+)/$','books.views.delete_alert1'),
    #url(r'^deleteq1/(?P<qid>\d+)/$','books.views.delete_alert1'),
    url(r'^deletea/(?P<aid>\d+)/$','books.views.deletea_alert1'),
    #url(r'^deletea1/(?P<aid>\d+)/$','books.views.deletea_alert1'),
    url(r'^edit_question/(?P<qid>\d+)/$','books.views.edit_ques'),
    url(r'^edit_answer/(?P<aid>\d+)/$','books.views.edit_ans'),
    url(r'^edit_sanswer/(?P<aid>\d+)/$','books.views.edit_sans'),
    url(r'^edit_squestion/(?P<qid>\d+)/$','books.views.edit_sques'),
    url(r'^suggest_accept/(?P<qid>\d+)/(?P<id>\d+)/','books.views.edit_accept'),
    url(r'^suggest_reject/(?P<qid>\d+)/(?P<id>\d+)/','books.views.edit_reject')
    #url(r'^save/(?P<topic>.+?)/(?P<tag>.+?)/(?P<qid>\d+)/$','books.views.saved')
    #url(r'^notification/',include ('notification.urls')),
    #editing of question
    #url('^edit/(?P<qid>\d+)/$', 'books.views.edit'),
    )