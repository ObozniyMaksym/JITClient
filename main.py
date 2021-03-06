import os
import requests
from json import dumps, loads
from math import ceil
from flask import render_template, Flask, send_from_directory, request, make_response, Markup
from config import Config

def load_dishes():
    dishes_request = requests.get("{}/get/dishes".format(Config.API_URL))
    return loads(dishes_request.text)["res"]

def get_dish_id_map():
    dishes = load_dishes()

    dishes_map = {}
    for dish in dishes:
        dishes_map[dish.get("id")] = dish
    return dishes_map

def get_ingredient_title_map():
    ingredients_request = requests.get("{}/get/ingredients".format(Config.API_URL))
    ingrediets = loads(ingredients_request.text)["res"]

    ingredient_map = {}
    for ingredient in ingrediets:
        ingredient_map[ingredient.get("id")] = ingredient.get("title")

    return ingredient_map

app = Flask(__name__)

@app.route("/vendor/<path:p>")
def vendor_handle(p):
    return send_from_directory("design/vendor", p)

@app.route("/css/<path:p>")
def css_handle(p):
    return send_from_directory("design/css", p)

@app.route("/js/<path:p>")
def js_handle(p):
    return send_from_directory("design/js", p)

@app.route("/include/<path:p>")
def include_handle(p):
    return send_from_directory("design/include", p)

@app.route("/fonts/<path:p>")
def fonts_handle(p):
    return send_from_directory("design/fonts", p)

@app.route("/images/<path:p>")
def images_handle(p):
    return send_from_directory("design/images", p)

@app.route("/third-party-scripts/<path:p>")
def third_party_scripts_handle(p):
    return send_from_directory("third-party-scripts", p)

with open("templates/components/header.html") as fin:
    header_html = Markup(fin.read())

with open("templates/components/cart_header.html") as fin:
    cart_header_html = Markup(fin.read())

with open("templates/components/footer.html") as fin:
    footer_html = Markup(fin.read())

@app.route("/cart")
def cart_handle():
    dishes_list = load_dishes()

    in_cart = {}
    try:
        in_cart = loads(list(request.cookies.keys())[0])
        in_cart_new = {}
        for key in in_cart.keys():
            in_cart_new[int(key)] = in_cart[key]
        in_cart = in_cart_new
    except Exception as _:
        try:
            in_cart = loads(list(request.cookies.keys())[1])
            in_cart_new = {}
            for key in in_cart.keys():
                in_cart_new[int(key)] = in_cart[key]
            in_cart = in_cart_new
        except Exception as _:
            pass

    return render_template("cart.html",
        api_url=Config.API_URL,
        in_cart_dishes=in_cart,
        dishes_list=get_dish_id_map(),
        header=cart_header_html,
        footer=footer_html,
        show_cart_icon=False)

@app.route("/product")
def product_handle():
    dishes = load_dishes()

    tag = request.args.get("tag")
    if tag:
        dishes = list(filter(lambda dish: tag in dish.get("tags"), dishes))

    sort_type = request.args.get("sort_type")
    if sort_type:
        if sort_type == "low_to_hight":
            dishes = sorted(dishes, key=lambda dish : dish.get("cost"))
        elif sort_type == "hight_to_low":
            dishes = sorted(dishes, key=lambda dish : dish.get("cost"), reverse=True)
        elif sort_type == "alphabetically":
            dishes = sorted(dishes, key=lambda dish : dish.get("title"))

    return render_template(
        "product.html",
        dishes=dishes,
        api_url=Config.API_URL,
        header=header_html,
        footer=footer_html)

@app.route("/track")
def track_handle():
    return render_template(
        "track.html",
        api_url=Config.API_URL,
        header=header_html,
        footer=footer_html
    )


@app.route("/")
def index_handle():
    return product_handle()


@app.route("/product_info")
def product_info_handle():

    try:
        required_id = int(request.args.get("id"))
    except:
        return "<h1>Мужские гинеталии</h1>"

    dishes_list = load_dishes()

    try:
        required_dish = list(filter(lambda dish : dish["id"] == required_id, dishes_list))[0]
    except:
        return "<h1>Женские гинеталии</h1>"

    return render_template(
        "productinfo.html",
        header = header_html,
        footer = footer_html,
        dish = required_dish,
        ingredients = get_ingredient_title_map(),
        api_url = Config.API_URL
    )


@app.route("/about")
def contact_handle():
    return render_template("about.html",
        header = header_html,
        footer = footer_html,
        api_url=Config.API_URL)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)