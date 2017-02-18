import os
import jinja2
import webapp2

import random
import string
import re
import hashlib
import hmac

from model import BlogUser


#initialize jinja2
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

# validation functions
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)

# hashing functions
def make_salt(length = 5):
    return "".join(random.choice(string.ascii_letters + string.digits)
                   for x in xrange(length))
    
def make_pw_hash(name, pwd, salt = None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pwd + salt).hexdigest()
    return "%s,%s" % (salt, h)

def valid_pw(name, pwd, h):
    salt = h.split(',')[0]
    return make_pw_hash(name, pwd, salt) == h


# cookie functions
secret = make_salt(32)
def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val


def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)


class BaseHandler(webapp2.RequestHandler):
    """ Provides common methods. """
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def render_error(self, err_type):
        """ Renders error pages. """
        page_title = ""
        page_text = ""
        if err_type == "404":
            page_title = app_messages["error_404_page_title"]
            page_text = app_messages["error_404_page_text"]

        if err_type == "403":
            page_title = app_messages["error_403_page_title"]
            page_text = app_messages["error_403_page_text"]    

        self.render("error.html", page_title = page_title,
                            page_text = page_text)    

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))
        
    def read_secure_cookie(self, name):
        """ Checks whether a cookie exists and is valid. """
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        """ Sets an authentication cookie. """
        self.set_secure_cookie('user_id', str(user.key.id()))

    def logout(self):
        """ Unsets an authentication cookie. """
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')    

    def initialize(self, *a, **kw):
        """
        Extends per request initialization to make commonly used data
        readily available.
        """
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and BlogUser.by_id(long(uid))
            


app_messages = dict(error_404_page_title = "Page not Found",
                    error_404_page_text = "Page wasn't found :'(",
                    error_403_page_title = "Access Denied",
                    error_403_page_text = ("You don't have access to see this "
                                           "page :-["))
