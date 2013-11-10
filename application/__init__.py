"""
Initialize Flask app

"""
from flask import Flask, session, request

from flask_debugtoolbar import DebugToolbarExtension
from gae_mini_profiler import profiler, templatetags
from werkzeug.debug import DebuggedApplication
from models import UserModel, ROLES

from flask_babel import Babel
from flask_login import LoginManager, current_user
from flask_mail import Mail
import gettext
gettext.install(None)

app = Flask('application')
app.config.from_object('application.settings')

# Enable jinja2 loop controls extension
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
app.jinja_env.globals['LANGUAGES'] = app.config['LANGUAGES']
app.jinja_env.globals['current_user'] = current_user
app.jinja_env.globals['ROLES'] = ROLES


#Babel
babel = Babel(app)

@babel.localeselector
def get_locale():
    if 'locale' not in session:
        session['locale'] = request.accept_languages.best_match(app.config['LANGUAGES'])
    return session['locale']

@babel.timezoneselector
def get_timezone():
    if 'timezone' in session:
        return session['timezone']

#login
login_manager = LoginManager(app)
#login_manager.init_app(app)

@login_manager.user_loader
def load_user(userid):
    if userid == None:
        return None
    id = int(userid)
    member = UserModel.get_by_id(id)
    return member

#mail
mail = Mail(app)

@app.context_processor
def inject_profiler():
    return dict(profiler_includes=templatetags.profiler_includes())


#register blueprints
from visitor import visitor
from exhibitor import exhibitor
from admin import admin, init_admin

app.register_blueprint(visitor, url_prefix='/visitors')
app.register_blueprint(exhibitor, url_prefix='/exhibitors')
app.register_blueprint(admin, url_prefix='/admin')

# Pull in URL dispatch routes
import urls

# Flask-DebugToolbar (only enabled when DEBUG=True)
toolbar = DebugToolbarExtension(app)

# Werkzeug Debugger (only enabled when DEBUG=True)
if app.debug:
    app.wsgi_app = DebuggedApplication(app.wsgi_app, evalex=True)

# GAE Mini Profiler (only enabled on dev server)
app.wsgi_app = profiler.ProfilerWSGIMiddleware(app.wsgi_app)

init_admin()
