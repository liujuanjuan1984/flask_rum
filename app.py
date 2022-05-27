import dataclasses
import datetime
import os
import sys
import uuid

import filetype
from flask import (Flask, flash, redirect, render_template, request,
                   send_from_directory, url_for)
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from flaskwebgui import FlaskUI
from officy import JsonFile
from rumpy import RumClient
from rumpy.utils import timestamp_to_datetime as ts2dt
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from wtforms import (IntegerField, SelectMultipleField, StringField,
                     SubmitField, TextAreaField)
from wtforms.validators import DataRequired, Length


class UserConfig:
    def __init__(self):
        self.filepath = os.path.join( os.path.dirname(__file__), "user_config.json") 
        self.config = JsonFile(self.filepath).read({})

    def check_user_config(self,port=None):
        seed = self.config.get("seed",{})
        port = port or self.config.get("port",0)
        is_port_correct = self.check_rum_port(port)
        self.rum = RumClient(port=port)
        if is_port_correct :
            self.update_file("port",port)
            _create_ = True
            if self.rum.group.is_seed(seed):
                _create_ = False 
                self.rum.group_id = seed.get("group_id")
                if not self.rum.group.is_joined():
                    self.rum.group.join(seed)
            if  _create_:
                # 创建种子网络用于数据的上传和下载
                seed = self.rum.group.create(f"ishare_{datetime.date.today()}")
                self.rum.group.join(seed)
                self.update_file("seed",seed)
        return is_port_correct,port,self.rum
        

    def check_rum_port(self,port):
        try:
            rum = RumClient(port=port)
            node_id = rum.node.id
            assert type(node_id) == str 
            node_id.startswith("16")
            is_port_correct = True 
        except Exception as e :
            print(e)
            is_port_correct = False 
        print("check_rum_port",port,is_port_correct)
        return is_port_correct
            

    def update_file(self, key,value):
        user_config = JsonFile(self.filepath).read({})
        user_config.update({key:value})
        JsonFile(self.filepath).write(user_config)

        

app = Flask(__name__, template_folder="templates")
app.config["SECRET_KEY"] = uuid.uuid4().hex
Bootstrap(app)
is_port_correct,port,rum  = UserConfig().check_user_config()

ui = FlaskUI(app, width=1024, height=680, host="0.0.0.0")

# 使用pyinstaller打包成单文件需要处理路径问题
app_path = ""
if hasattr(sys, "_MEIPASS"):  # 如果是单个EXE文件执行的时候sys中会存在这个_MEIPASS变量作为当前的工作根路径
    app_path = os.path.join(sys._MEIPASS)


class PortForm(FlaskForm):
    port = IntegerField("port of quorum", validators=[DataRequired()])
    submit = SubmitField("提交")

class CommentForm(FlaskForm):
    title = TextAreaField("标题？", validators=[DataRequired(), Length(2, 50)])
    text = TextAreaField("有什么想说的？", validators=[DataRequired(), Length(2, 3000)])
    groups = SelectMultipleField( choices=[('5d53968c-3b48-44c5-953f-0abe0b7ad73d', '待办清单'), ('4e784292-6a65-471e-9f80-e91202e3358c', '刘娟娟的朋友圈'), ('cfb42114-0ee1-429b-86e5-7659108972be', '杰克深的朋友圈'), ('3bb7a3be-d145-44af-94cf-e64b992ff8f0', '去中心微博')])
    submit = SubmitField("提交")

@app.route("/")
def home():
    print(is_port_correct,port)
    if not is_port_correct:
        return redirect(url_for("add_quorum_port"))
    else:
        return redirect(url_for("get_quorum_groups",port=int(port)))
    return redirect(url_for("dev_logs"))

@app.route("/logs/")
def dev_logs():
    return render_template("dev_logs.html")



@app.route("/port/add/", methods=["GET", "POST"])
def add_quorum_port():
    global rum 
    form = PortForm()
    if form.validate_on_submit():
        port = form.port.data
        is_port_correct,port,rum = UserConfig().check_user_config(port)
        if is_port_correct:
            flash(f"Your quorum port is:{port}.")
            return redirect(url_for("get_quorum_groups", port=int(port)))
        else:
            flash(f"Opps. Your quorum port is:{port}, cannot be connected.")
            return redirect(url_for("add_quorum_port"))
    return render_template("quorum_port.html", form=form)

@app.route("/groups/", methods=["GET", "POST"])
def get_quorum_groups():
    group_ids = rum.node.groups_id 
    return render_template("groups.html", group_ids=group_ids)

@app.route("/groups/post", methods=["GET", "POST"])
def post_to_groups():
    global rum 
    form = CommentForm()
    if form.validate_on_submit():
        title = form.title.data
        text = form.text.data
        groups = form.groups.data
        for gid in groups:
            rum.group_id = gid 
            resp = rum.group.send_note(content=text,name=title)
            if "trx_id" in resp:
                flash(f"动态已发布到种子网络 {gid}")
        return redirect(url_for("post_to_groups"))
    return render_template("groups_post.html", form=form)


@dataclasses.dataclass 
class TrxView:
    group_id:str 
    trx_id:str 
    text:str 
    timestamp:str 

@app.route("/timeline", methods=["GET", "POST"])
def timeline_mix():
    global rum 
    gids = rum.node.groups_id
    trxsview = []
    for gid in gids:
        rum.group_id = gid 
        if  rum.group.info().app_key in [ "group_timeline","group_post"]:
            trxs = rum.group.content_trxs(is_reverse=True,num=200)
            for trx in trxs:
                _ts =  str(datetime.datetime.now() + datetime.timedelta(hours=-2))
                ts = str(ts2dt(trx["TimeStamp"]))
                if ts <= _ts :
                    continue
                obj, can_post = rum.group.trx_to_newobj(trx, nicknames={})
                if not can_post:
                    continue

                trxsview.append(TrxView(**{"group_id":gid,
                    "trx_id":trx['TrxId'],
                    "text": obj["content"],
                    "timestamp":ts 
                    })) 

    return render_template("timeline.html", trxsview=trxsview)



if __name__ == "__main__":
    ui.run()
    #app.run(debug=True)

    #静态资源修改不需要重启
    #app.jinja_env.auto_reload = True
    #app.run(debug=True)