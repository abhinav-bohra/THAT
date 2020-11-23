from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField,PasswordField,SubmitField,BooleanField,TextAreaField,SelectField
from wtforms.fields.html5 import DateField,TimeField
from wtforms.validators import DataRequired,Length,Email,EqualTo,ValidationError,Optional
from THAT.models import User,Lecture    

class RegistrationForm(FlaskForm):
	username=StringField('Username',validators=[DataRequired(),Length(min=2,max=20)])#field should not be empty and length should be between 2 and 20
	email=StringField('Email',validators=[DataRequired(),Email()])
	user_type=SelectField(
        'User type',
        choices=[('Student', 'Student'), ('Professor', 'Professor')]
    )
	password=PasswordField('Password', validators=[DataRequired(),Length(max=50)]) 
	confirm_password=PasswordField('Confirm Password',validators=[DataRequired(), EqualTo('password')])
	submit=SubmitField("Register")

	def validate_username(self, username):
			user=User.query.filter_by(username=username.data).first()
			if user:
				raise ValidationError('Username already in use. Please choose a different one.');

	def validate_email(self, email):
			user=User.query.filter_by(email=email.data).first()
			if user:
				raise ValidationError('Email already in use. Please choose a different one.');

	def validate_instituteId(self, instituteId):
			user=User.query.filter_by(instituteId=instituteId.data).first()
			if user:
				raise ValidationError('Institute Id is already in use. Please choose a different one.');
		
class UpdateAccountForm(FlaskForm):
	username=StringField('Username',validators=[DataRequired(),Length(min=2,max=20)])#field should not be empty and length should be between 2 and 20
	email=StringField('Email',validators=[DataRequired(),Email()])
	submit=SubmitField("Update")

	def validate_username(self, username):
		if(username.data!=current_user.username):
			user=User.query.filter_by(username=username.data).first()
			if user:
				raise ValidationError('Username already in use. Please choose a different one.');

	def validate_email(self, email):
		if(email.data!=current_user.email):
			user=User.query.filter_by(email=email.data).first()
			if user:
				raise ValidationError('Email already in use. Please choose a different one.');

class LoginForm(FlaskForm):
	username=StringField('Username',validators=[DataRequired(),Length(min=2,max=20)])#field should not be empty and length should be between 2 and 20
	password=PasswordField('Password', validators=[DataRequired()]) 
	remember = BooleanField('Remember Me')
	submit=SubmitField("Login")

class LectureForm(FlaskForm):
	title=StringField('Title',validators=[DataRequired()])
	details=TextAreaField('Lecture-details')
	date=DateField('Date',validators=[DataRequired()],format='%Y-%m-%d')
	starttime=TimeField('Start Time',validators=[Optional()])
	endtime=TimeField('End Time',validators=[Optional()])
	video_path =StringField('Video',validators=[Optional()])
	submit=SubmitField('Submit')

class SearchForm(FlaskForm):
	search=StringField('Enter the Lecture-title',validators=[DataRequired()])
	submit=SubmitField('Search')

class MessageForm(FlaskForm):
	email=StringField('Email',validators=[DataRequired(),Email()])
	message=TextAreaField('Message')
	submit=SubmitField("Send")

class FeedbackForm(FlaskForm):
	email=StringField('Email',validators=[DataRequired(),Email()])
	professor_name=StringField('Professor you are addressing',validators=[DataRequired(),Email()])
	feedback=TextAreaField('Feedback')
	submit=SubmitField("Submit")
