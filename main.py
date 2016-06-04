#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import endpoints
from protorpc import remote
from protorpc import messages
from protorpc import message_types

from google.appengine.ext import ndb

from models import Question
from models import TestcaseForm
from models import QuestionForm
from models import QuestionForms
from models import QuestionMiniForm
from models import QuestionMiniForms
from models import Submission
from models import SubmissionForm
from models import SubmissionForms
from models import Testcase
from models import TestcaseForms


EMAIL_SCOPE = endpoints.EMAIL_SCOPE
API_EXPLORER_CLIENT_ID = endpoints.API_EXPLORER_CLIENT_ID
WEB_CLIENT_ID='602783917304-5epdo5rivihkj4c6oe62a8vf863kuk3r.apps.googleusercontent.com'


QUES_GET_REQUEST = endpoints.ResourceContainer(
    message_types.VoidMessage,)

SUB_POST_REQUEST = endpoints.ResourceContainer(
	SubmissionForm,
	websafekey = messages.StringField(1, required=True))


@endpoints.api(name='codegress', version='v2', 
	allowed_client_ids=[WEB_CLIENT_ID, API_EXPLORER_CLIENT_ID],
	scopes=[EMAIL_SCOPE])
class CodegressApi(remote.Service):
	

	def _addQuestionObject(self, request):
		user = endpoints.get_current_user()
		if not user:
			raise endpoints.UnauthorizedException("Not an anuthorized user")
		data = {field.name: getattr(request, field.name) for field in request.all_fields()}
		testcases = data['sample_testcase'] + data['testcases']
		del data['sample_testcase']
		del data['testcases']
		q_key = ndb.Key(Question, data['title'])
		data['key'] = q_key
		data['author'] = user
		data['queskey'] = q_key.urlsafe()
		tc = []
		for test in testcases:
			tc.append(Testcase(iput=test.iput,
												 oput=test.oput,
												 points=test.points,
												 hint=test.hint))
		Question(**data).put()
		self._addTestcases(q_key, tc)
		return request

	
	def _addTestcases(self, parent_key, testcases):
		t_ids = Testcase.allocate_ids(size=len(testcases), parent=parent_key)
		for i in range(0, len(t_ids)):
			t_key = ndb.Key(Testcase, t_ids[i], parent = parent_key)
			testcases[i].key = t_key
			testcases[i].put()
		return

	@endpoints.method(QuestionForm, QuestionForm, 
		path='addQuestion',
		http_method='POST',
		name='addQuestion')
	def addQuestion(self, request):
		return self._addQuestionObject(request)


	def _getQuestions(self):
		ques = Question.query()
		return self._copyQuestiontoForm(ques)

	def _copyQuestiontoForm(self, ques):
		return QuestionMiniForms(items=[self._copyToQuestionMiniForm(q) for q in ques])

	def _copyToQuestionMiniForm(self, q):
		return QuestionMiniForm(title=q.title, handle=q.author.email())
			
	def _addSubmission(self, request):
		user = endpoints.get_current_user()
		if not user:
			raise endpoints.UnauthorizedException("Please login to continue")
		data = {field.name: getattr(request, field.name) for field in request.all_fields()}
		q_key = ndb.Key(urlsafe=request.websafekey)
		del data['websafekey']
		s_id = Submission.allocate_ids(size = 1, parent=q_key)[0]
		s_key = ndb.Key(Submission, s_id, parent=q_key)
		data['key'] = s_key
		data['user'] = user
		data['subskey'] = s_key.urlsafe()
		Submission(**data).put()
		return SubmissionForm(code=data['code'], score=data['score'], 
						language=data['language'])

	def _copyToSubmissionForms(self, query):
		return SubmissionForms(items = [self._copyToSubmissionForm(q) for q in query])
			
	def _copyToSubmissionForm(self, sub):
		return SubmissionForm(code=sub.code, score=sub.score,
													language=sub.language)

	@endpoints.method(QUES_GET_REQUEST, QuestionMiniForms,
		path='getAllQuestions',
		http_method='POST',
		name='getAllQuestions')
	def getAllQuestions(self, request):
		return self._getQuestions()

	@endpoints.method(SUB_POST_REQUEST, SubmissionForm,
		path='codeSubmit',
		http_method='POST',
		name='codeSubmit')
	def codeSubmit(self, request):
		return self._addSubmission(request)

	@endpoints.method(message_types.VoidMessage, SubmissionForms,
		path='getSubmissions',
		http_method='GET',
		name='getSubmissions')
	def getSubmissions(self):
		submissions = Submission.query()
		return self._copyToSubmissionForms(submissions)

api = endpoints.api_server([CodegressApi]) # register API