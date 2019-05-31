# from flask_wtf import FlaskForm
# from wtforms import IntegerField, StringField, SubmitField, FloatField
# from wtforms.widgets import TextArea
# from wtforms.validators import DataRequired
#
#
# class CreateNewProject(FlaskForm):
#     title = StringField('Title', validators=[DataRequired()])
#     Description = StringField('Description', validators=[DataRequired()])
#
#     create_button = SubmitField('Create')
#
#
# class CreateNewTask(FlaskForm):
#     hit_title = StringField('HIT Title', validators=[DataRequired()])
#     hit_desc = StringField('Description', widget=TextArea(), validators=[DataRequired()])
#     instructions = StringField('Instructions', widget=TextArea(), validators=[DataRequired()])
#     keywords = StringField('keywords', validators=[DataRequired()])
#     target_workers = IntegerField('Target Workers', validators=[DataRequired()])
#     fix_price = FloatField('Fix Price', validators=[DataRequired()])
#     time_limit = IntegerField('Time limit', validators=[DataRequired()])
#
#     #for production purposes
#     hourly_rate = FloatField('Hourly Rate', validators=[DataRequired()], default=0.0)
#     work_rate = FloatField('Rate per Contribution', validators=[DataRequired()], default=0.0)
#
#     #Qualifications
#     country = StringField('Country', validators=[DataRequired()], default="US")
#     percent_approved = IntegerField('Percent Approved', validators=[DataRequired()], default=97)
#     HITS_approved = IntegerField('# of HITS Approved', validators=[DataRequired()], default=1000)
#
#     # status = StringField('status', validators=[DataRequired()])
#     task_url = StringField('URL for TASK', validators=[DataRequired()], default = 'https://pepperanywhere.herokuapp.com/crowd_task')
#
#     submit = SubmitField('create_task')
