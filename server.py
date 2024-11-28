from flask import Flask, url_for, session, redirect, render_template
from authlib.integrations.flask_client import OAuth
import json 

app = Flask(__name__)

appConf = {"OAUTH_CLIENT_ID" : "737450155200-hpu148a7qsgr2248s6add4keifhj05sb.apps.googleusercontent.com" ,
           "OAUTH_CLIENT_SECRET": "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",
           "OAUTH_META_URL": "https://accounts.google.com/.well-known/openid-configuration",
           "Flask_SECRET": "cbazomnnjh2hz3uwcoe3cgau9jdp0pkv",
           "FLASK_PORT":5000
}

app.secret_key = appConf.get("Flask_SECRET")


oauth = OAuth(app)
oauth.register("ClickStore",
               client_id = appConf.get("OAUTH_CLIENT_ID"),
               client_secret = appConf.get("OAUTH_CLIENT_SECRET"),
               server_metadata_url = appConf.get("OAUTH_META_URL"),
               client_kwargs = {
                   "scope": "openid profile email"
               }
               )
@app.route("/")
def home():
    return render_template("home.html",
                           session = session.get("user"),
                           pretty = json.dumps(session.get("user"),
                                               indent = 4))

@app.route("/google-login")
def googleLogin():
    redirect_uri = url_for("googleCallback", _external = True)
   #print(f"Redirect URI: {redirect_uri}")
    return oauth.ClickStore.authorize_redirect(redirect_uri = redirect_uri)


@app.route("/signin-google")
def googleCallback():
   token = oauth.ClickStore.authorize_access_token()
   session["user"] = token 
   return redirect(url_for("home"))





if __name__ == "__main__":
    app.run(host="0.0.0.0", port = appConf.get("FLASK_PORT"), debug = True)