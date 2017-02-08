#################################--------------#################################
# Author: Karthik Chaganti
# Descr: The file that reads from DB and populates the views in the website
#################################--------------#################################

from flask import render_template, request
from flask import jsonify
from app import app
from cassandra.cluster import Cluster

# Connect to cassandra
cluster = Cluster(["ec2-34-198-185-77.compute-1.amazonaws.com"])
session = cluster.connect("stockportfolio")
session.default_fetch_size = None

def get_user_data(userid):
    # Read user's data from cassandra dB
    hist_trades = session.execute("SELECT tickername, tradequantity,tickerprice,total_val,tradetype,tradetime FROM db_trades_stream  WHERE userId=%s ORDER BY tradetime DESC LIMIT 5", parameters=[userid])
    port_list   = session.execute("SELECT tickername, tickerquant, tickervalue FROM db_user_portfolio WHERE userid=%s", parameters=[userid])
    port_total  = session.execute("SELECT portfolio_count, portfolio_value FROM db_user_portcount WHERE userid=%s", parameters=[userid])
    return [hist_trades,port_list,port_total]

def get_user_json_data(userid):

    hist_trades, port_list, port_total = get_user_data
    hist_trades_json = [{"tickername":row.tickername, "tradequantity":row.tradequantity,"tickerprice":row.tickerprice,"total_val":row.total_val,"tradetype":row.tradetype,"tradetime":row.tradetime}for row in hist_trades]
    port_list_json   = [{"tickername":row.tickername,"tickerquant":tickerquant,"tickervalue":tickervalue} for row in port_list]
    port_total_json  = [{"portfolio_count":portfolio_count,"portfolio_value":portfolio_value} from row in port_total]

    return jsonify(hist_trades = hist_trades_json,port_list=port_list_json,port_total=port_total_json)

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/slides')
def slides():
    return render_template("slides.html")

@app.route('/userid')
def get_user():
    user=request.args.get("userid")
    hist_trades,port_list,port_total = get_user_data(request.args.get("userid"))
    return render_template("userid.html", userid=userid, hist_trades = hist_trades, port_list = port_list, port_total = port_total)