from flask import Flask, render_template

app = Flask(__name__)



@app.route('/')
def home():
    return render_template('index.html')

@app.route('/catalog/<string:category_name>/items')
def show_category_items(category_name):
    return render_template('view_items.html')

@app.route('/catalog/<string:category_name>/<string:item_name>')
def show_category_individual_item(category_name, item_name):
    return render_template('view_individual_item.html')

@app.route('/catalog/item/add')
def add_item():
    return render_template('add_item.html')

@app.route('/catalog/<string:item_name>/edit')
def edit_item(item_name):
    return render_template('edit_item.html')

@app.route('/catalog/<string:item_name>/delete')
def delete_item(item_name):
    return render_template('delete_item.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)