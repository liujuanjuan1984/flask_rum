from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length

# 表单组件


class PortForm(FlaskForm):
    port = IntegerField("port of quorum", validators=[DataRequired()])
    submit = SubmitField("提交")


class CommentForm(FlaskForm):
    text = TextAreaField("评价种子网络", validators=[DataRequired(), Length(2, 1000)])
    stars = IntegerField("评分 1-5", validators=[DataRequired()])
    submit = SubmitField("提交")


# seed 提交种子
class SeedForm(FlaskForm):
    seed = TextAreaField("提交种子", validators=[DataRequired(), Length(200, 2000)])
    submit = SubmitField("提交")
