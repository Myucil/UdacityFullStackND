import os
import jinja2
import webapp2
import re
import hmac
import hashlib
import random

from string import letters

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
    autoescape = True)


# Global function for rendering a string which does not inherit from the class Handler

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)


# functions for hashing and validating password hashing

secret = 'aaarfh-this_is-sooooo_secreteeeeeer-than_anything-ion'

def make_secure_val(val):
    return "%s|%s" % (val, hmac.new(secret, val).hexdigest())

def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val


# class that handles rendering and writing and can be used in other classes that inherit from it

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))


# class that renders a start page, just for the sake of it

class Entrance(Handler):
    def get(self):
        self.render("entrance.html")


# Functions for hashing and salting

def make_salt():
    return ''.join(random.choice(letters) for x in range(5))

def make_pw_hash(name, pw, salt = None):
    if not salt:
        salt = make_salt()
    hashstring = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, hashstring)

def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)

def users_key(group = 'default'):
    return db.Key.from_path('users', group)


# class that creates the basic database specifics for a user

class User(db.Model):
    name = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)
    email = db.StringProperty()

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent = users_key())

    @classmethod
    def by_name(cls, name):
        u = User.all().filter('name =', name).get()
        return u

    @classmethod
    def register(cls, name, pw, email=None):
        pw_hash = make_pw_hash(name, pw)
        return User(parent = users_key(),
                    name = name,
                    pw_hash = pw_hash,
                    email = email)

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and valid_pw(name, pw, u.pw_hash):
            return u


# class that creates the basic database specifics for a blog post

def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

class Posts(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    author = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

    def render(self):
        self.render_text = self.content.replace('\n', '<br>')
        return render_str("post.html", p = self)


# class that shows a newly created blog post

class PostHandler(Handler):
    def get(self, post_id):
        key = db.Key.from_path('Posts', int(post_id), parent = blog_key())
        p = db.get(key)

        if not p:
            self.error(404)
            return

        self.render("permalink.html", p = p)


# class that renders a form page for creating a new blog post

class NewPost(Handler):
    def get(self):
        if self.user:
            self.render("newpost.html")
        else:
            error = "You need to be logged in to write a new post!"
            self.render('login.html', error=error)

    def post(self):
        if not self.user:
            self.redirect("/blog")

        subject = self.request.get("subject")
        content = self.request.get("content")
        author = self.user.name

        if subject and content:
            p = Posts(parent = blog_key(), author=author, subject=subject, content=content)
            p.put()
            self.redirect("/blog/%s" % str(p.key().id()))
        else:
            error = "You have to fill in both subject and content fields!"
            self.render("newpost.html", subject=subject, content=content, error=error)


# class that opens an existing post for editing

class EditPost(Handler):
    def get(self, post_id):
        key = db.Key.from_path('Posts', int(post_id), parent = blog_key())
        p = db.get(key)

        if self.user.name == p.author:
            self.render("edit.html", p=p, subject=p.subject, content=p.content)
        else:
            error = "You need to be logged in to edit your post!"
            self.render('login.html', error=error)

    def post(self):

        subject = self.request.get("subject")
        content = self.request.get("content")
        author = self.user.name

        if subject and content:
            p = Posts(parent = blog_key(), author=author, subject=subject, content=content)
            p.put()
            self.redirect("/blog/%s" % str(p.key().id()))
        else:
            error = "You have to fill in both subject and content fields!"
            self.render("edit.html", p=p, subject=subject, content=content, error=error)


# functions that check username, password and email for correct syntax in the signup form

username_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and username_RE.match(username)

password_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and password_RE.match(password)

email_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or email_RE.match(email)


# class that renders the signup form and uses the functions above to check signup syntax

class SignUpHandler(Handler):
    def get(self):
        self.render('signup.html')

    def post(self):
        error_msg = False
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')

        params = dict(username = self.username, email = self.email)

        if not valid_username(self.username):
            params['username_error'] = "Username is invalid."
            error_msg = True

        if not valid_password(self.password):
            params['password_error'] = "Password is invalid."
            error_msg = True
        elif self.password != self.verify:
            params['verify_error'] = "Passwords didn't match."
            error_msg = True

        if not valid_email(self.email):
            params['email_error'] = "Email is invalid."
            error_msg = True

        if error_msg:
            self.render('signup.html', **params)
        else:
            self.done()

    def done(self, *a, **kw):
        raise NotImplementedError


# class for registering a user, if the user is new and unique

class Register(SignUpHandler):
    def done(self):
        u = User.by_name(self.username)
        if u:
            message = 'A user with that name already exists'
            self.render('signup.html', username_error = message)
        else:
            u = User.register(self.username, self.password, self.email)
            u.put()

            self.login(u)
            self.redirect('/blog/welcome')


# login class

class Login(Handler):
    def get(self):
        self.render('login.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        u = User.login(username, password)
        if u:
            self.login(u)
            self.redirect('/blog/welcome')
        else:
            message = 'Invalid login'
            self.render('login.html', error = message)


# logout class

class Logout(Handler):
    def get(self):
        self.logout()
        self.redirect('/blog/signup')


# class that renders a welcome page when a new user has signed up

class WelcomeHandler(Handler):
    def get(self):
        if self.user:
            self.render('welcome.html', username = self.user.name)
        else:
            self.redirect('/blog/signup')


# class that renders the main blog page

class MainPage(Handler):
    def render_blog(self):
        posts = db.GqlQuery("SELECT * FROM Posts ORDER BY created DESC LIMIT 10")
        self.render("blog.html", posts=posts)

    def get(self):
        self.render_blog()



app = webapp2.WSGIApplication([('/', Entrance),
                               ('/blog', MainPage),
                               ('/blog/newpost', NewPost),
                               ('/blog/edit/([0-9]+)', EditPost),
                               ('/blog/([0-9]+)', PostHandler),
                               ('/blog/signup', Register),
                               ('/blog/welcome', WelcomeHandler),
                               ('/blog/login', Login),
                               ('/blog/logout', Logout)
                             ],
                             debug=True)

