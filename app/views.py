##My Personal Boiler Plate for all FLASK Apps ##
from app.models import User, Server
from flask_openid import OpenID
import re, requests, time, datetime, json
from app import app, engine, db_session
from flask import url_for, render_template, flash, g, session, redirect, request
from subprocess import (PIPE, Popen)
from squery import SourceQuery
import MySQLdb
db = MySQLdb.connect("","root","","gamecp")
cursor = db.cursor()


## Get human readable date ##
dateList = []
today = datetime.date.today()
dateList.append(today)

## Useful if you need to access os cmd's ##
def cmd(command):
  return Popen(command, shell=True, stdout=PIPE)


## Set up db and OA options ##
con = engine.connect()
app.secret_key = 'super secret key'
STEAM_API_KEY = "1A15D2C82402F944CF5625FC011EF14C"
open_id = OpenID(app)
_steam_id_re = re.compile('steamcommunity.com/openid/id/(.*?)$')


## Boiler plate for steam OA ##

def get_steam_userinfo(steam_id):
    options = {
        'key': STEAM_API_KEY,
        'steamids': steam_id
    }
    url = 'http://api.steampowered.com/ISteamUser/' \
          'GetPlayerSummaries/v0001'

    r = requests.get(url, params=options)
    rv = r.json()
    return rv['response']['players']['player'][0] or {}

@app.route('/login')
@open_id.loginhandler
def login():
    if g.user is not None:
        flash("You already have a team!")
        return redirect(open_id.get_next_url())
    return open_id.try_login('http://steamcommunity.com/openid')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('admin', None)
    return redirect(open_id.get_next_url())


@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])

@open_id.after_login
def create_or_login(response):
    match = _steam_id_re.search(response.identity_url)
    g.user = User.get_or_create(match.group(1))
    steamdata = get_steam_userinfo(g.user.steam_id)
    g.user.nickname = steamdata['personaname']
    db_session.commit()
    session['user_id'] = g.user.user_id
    output = redirect(open_id.get_next_url())
    return output


@app.before_request
def before_request():
    g.server = None
    if 'hostname' in session:
        g.server = Server.query.get(session['hostname'])


@app.route('/', methods=['GET', 'POST'])
def index():
## Begin code ##

## Set your 'server' table to empty
    g.server = None

## Here I mapped the server list manually the first time, this method should be updated to mysqldb ^^
    #serverlist = {"69.30.232.146:25451","69.30.232.146:25449","69.30.232.146:25461","69.30.232.146:25461","69.30.232.146:25459","69.30.232.146:25457","69.30.232.146:25455","69.30.232.146:25453","69.30.232.146:25447"}
    #serverlist = {"64.182.125.141:27017","64.182.125.141:27015","64.182.125.141:27019","64.182.125.142:27022","64.182.125.142:27018","64.182.125.140:27015","64.182.210.44:27015","64.182.210.36:27015","64.182.125.140:27016","64.182.210.44:27017","64.182.210.36:27016","64.182.210.44:27018","64.182.125.140:27018","64.182.125.140:27017","64.182.210.36:27017","64.182.210.36:27018","64.182.125.140:27019","64.182.125.142:27015","64.182.210.38:27016","64.182.125.142:27016","64.182.210.46:27015","64.182.210.38:27015","64.182.210.45:27016","64.182.210.37:27016","64.182.125.141:27017","64.182.210.37:27017","64.182.210.37:27019","64.182.210.45:27019"}
## Now we build a list of servers from the DB
    rl = []

## run through every server in the list and query its data

    rl = sList()

    output = render_template('index.html',datas=rl)
    return output


def sList():
## empty list, check db, add found items to list, return list
    serverlist = []
    sql = "SELECT * FROM usergames WHERE active = '1'"
    cursor.execute(sql)
    results = cursor.fetchall()
    for row in results:
        sip = row[3]
        sport = row[4]
        serverlist += "%s:%s"%(sip,sport)

        for x in serverlist:
            ## filtering the ip from the list into the required format
            ip, separator, port = x.rpartition(':')
            assert separator # separator (`:`) must be present
            port = int(port) # convert to integer
            sq = SourceQuery(ip,port)
            server = sq.getInfo()
            try:
                g.server = Server.get_or_create(server['Hostname'])
                g.server.ip = ip
                g.server.port = port
                g.server.type = server['GameDesc']
                g.server.map = server['Map']
                g.server.hostname = server['Hostname']
                g.server.maxplayers = server['MaxPlayers']
                g.server.curplayers = server['Players']
                ##now that we set up our session and database, we commit it
                db_session.commit()
            except:
                print "server offline"
    serverlist = []
    for server in Server.query.filter(Server.hostname.isnot(None)):
        serverlist += [server]
    serverlist.sort(key=lambda x: -int(x.curplayers))
    return serverlist


