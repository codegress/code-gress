

import endpoints
from protorpc import messages
from google.appengine.ext import ndb

class Testcase(ndb.Model):
	iput = ndb.StringProperty(required = True)
	oput = ndb.StringProperty(required = True)
	points = ndb.IntegerProperty(required = True)
	hint = ndb.StringProperty(default = None)


class Question(ndb.Model):
	title = ndb.StringProperty(required = True)
	description = ndb.TextProperty(required = True)
	image = ndb.StringProperty(repeated = True)
	score = ndb.IntegerProperty()
	author = ndb.UserProperty(required = True)


class TestcaseForm(messages.Message):
	iput = messages.StringField(1, required=True)
	oput = messages.StringField(2, required=True)
	points = messages.IntegerField(3, required=True)
	hint = messages.StringField(4)


class QuestionForm(messages.Message):
	title = messages.StringField(1, required=True)
	description = messages.StringField(2, required=True)
	sample_testcase = messages.MessageField(TestcaseForm, 3, repeated=True)
	testcases = messages.MessageField(TestcaseForm, 4, repeated=True)
	image = messages.StringField(5, repeated=True)
	# websafeKey      = messages.StringField(6)

class QuestionForms(messages.Message):
	items = messages.MessageField(QuestionForm, 1, repeated=True)

class QuestionMiniForm(messages.Message):
	title = messages.StringField(1, required=True)
	handle = messages.StringField(2, required=True)

class QuestionMiniForms(messages.Message):
	items = messages.MessageField(QuestionMiniForm, 1, repeated=True)
		

class TestcaseForms(messages.Message):
	items = messages.MessageField(TestcaseForm, 1, repeated=True)