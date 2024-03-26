from flask_bootstrap import Bootstrap5
from flask import Flask, render_template, redirect, request, url_for, jsonify
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import StringField,SelectField,SubmitField
import requests
from datetime import datetime as dt
from dotenv import load_dotenv
import os

load_dotenv()

username = os.environ["USERNAME_PIXELA"]
token = os.environ["TOKEN_PIXELA"]
secret_key = os.environ["SECRET_KEY"]
pixela_endpoint = "https://pixe.la/v1/users"

headers = {
    "X-USER-TOKEN" : token
}
class AddGraphForm(FlaskForm):
    graph_id = StringField(label="Enter an id for the graph ^[a-z][a-z0-9-]{1,16}: ", validators=[DataRequired()])
    graph_name=StringField(label="Enter graph's name:", validators=[DataRequired()])
    unit= StringField(label="Enter unit:")
    graph_type = SelectField(label="Chose which unit is allowed: ", choices=[("int", "Integer"), ( "float", "Decimal")])
    color = SelectField(label="Choose color", choices=[("shibafu", "Green"), ("momiji", "Red"), ("sora", "Blue"), ("ichou", "Yellow"), ("ajisai", "Purple"), ("kuro", "Black")])
    timezone = SelectField(label="Enter timezone (tz database name): ", choices=[("MX", "America/Mexico_City")])
    submit = SubmitField()
    
class UpdateTodayPixel(FlaskForm):
    quantity = StringField(label="Please enter quantity: ", validators=[DataRequired()])
    submit = SubmitField()

class UpdateUser(FlaskForm):
    new_token = StringField(label="Please enter a new token", validators=[DataRequired()])
    submit = SubmitField()

app = Flask(__name__)
bootstrap = Bootstrap5(app)
app.config['SECRET_KEY'] = secret_key
app.config['BOOTSTRAP_BOOTSWATCH_THEME'] = 'lux'



@app.route("/", methods=["GET", "POST"])
def home():
    graph_endpoint = f"{pixela_endpoint}/{username}/graphs"
    try:
        response_data = requests.get(url=graph_endpoint, headers=headers).json()["graphs"]
        graphs = [{"id": graph["id"], "name": graph["name"], 'unit':graph["unit"], "timezone":graph["timezone"], "url":f"https://pixe.la/v1/users/{username}/graphs/{graph['id']}.html"} for graph in response_data] 
    except Exception as e:
        return render_template('error.html', error_message="show graphs")       
    return render_template('index.html', all_graphs=graphs)

@app.route("/graph", methods=["GET", "POST"])
def graph():
    graph_id = request.args.get("id")
    today = f"{dt.now().date()}".replace("-", "")
    graph_svg_endpoint = f"{pixela_endpoint}/{username}/graphs/{graph_id}"
    update_pixel_form = UpdateTodayPixel()
    try:
        response_data_svg = requests.get(url=graph_svg_endpoint, headers=headers).text
    except Exception as e:
        return redirect(url_for('home'))
    if request.method == "POST":
        quantity = float(update_pixel_form.quantity.data)
        try:
            pixel_config = {
                    "date" : today,
                    "quantity": str(quantity)
                }
            response = requests.post(url=f"{pixela_endpoint}/{username}/graphs/{graph_id}", json=pixel_config, headers=headers)
            response.raise_for_status()
            return redirect(url_for('home'))
        except Exception as e:
            print(e)
    return render_template("graph.html", id=graph_id,svg_content=response_data_svg, form=update_pixel_form)

@app.route("/delete", methods=["GET", "POST" , "DELETE"])
def delete():
    id = request.args.get('id')
    try:
        response_delete_pixel = requests.delete(url=f"{pixela_endpoint}/{username}/graphs/{id}", headers=headers)
    except Exception as e:
        return render_template('error.html', error_message='delete graph')
    return redirect(url_for('home'))

@app.route('/add_graph', methods=["GET", "POST"])
def add_graph():
    add_graph_endpoint = f"{pixela_endpoint}/{username}/graphs"
    add_graph_form = AddGraphForm()
    if request.method == "POST":
        graph_id = add_graph_form.graph_id.data
        graph_name = add_graph_form.graph_name.data
        unit = add_graph_form.unit.data
        graph_type = add_graph_form.graph_type.data
        color = add_graph_form.color.data
        timezone = add_graph_form.timezone.data
        graph_config = {
        "id" : graph_id,
        "name" : graph_name,
        "unit" : unit,
        "type" : graph_type,
        "color" : color,
        "timezone" : "America/Mexico_City"
    }
        try:
            response = requests.post(url=add_graph_endpoint, json = graph_config, headers=headers)
            print(response.text)
            response.raise_for_status()
            return redirect(url_for('home'))
        except Exception as e:
            print(e)
    return render_template("add_graph.html", form=add_graph_form)

@app.route("/update_user", methods=["GET", "PUT", "POST"])
def update_user():
    update_user_form = UpdateUser()
    if request.method == "POST":
        try:
            token = update_user_form.new_token.data
            response = requests.put(headers=headers, json={"new_token" : token})
            return redirect(url_for('home'))
        except Exception as e:
            return render_template('error.html', error_message=e)
    return render_template("update_user.html", form=update_user_form)

if __name__ == "__main__":
    app.run(debug=True)