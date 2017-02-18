import main
from model import BlogUser

import webapp2

class RegistrationHandler(main.BaseHandler):
    """ Provides methods to register new blog users. """
    def get(self):
        if self.user:
            self.redirect("/blog")
        else:
            self.render("signup.html")


    def post(self):
        if self.user:
            return self.redirect('/blog')

        username = self.request.get("username")
        pwd = self.request.get("password")
        pwd_verify = self.request.get("verify")
        email = self.request.get("email")
        have_error = False
        
        username_error = ""
        password_error = ""
        verify_password_error=""
        email_error=""

        params = dict(username = username,
                      email = email)

        if not main.valid_username(username):
            params['error_username'] = "That's not a valid username."
            have_error = True
        
        user = BlogUser.by_username(username)
        if user:
            params['error_username'] = "That user already exists."
            have_error = True

        if not main.valid_password(pwd):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        elif pwd != pwd_verify:
            params['error_verify_password'] = "Your passwords didn't match."
            have_error = True

        if not main.valid_email(email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        if have_error:
            self.render('signup.html', **params)
        else:
            pw_hash = main.make_pw_hash(username, pwd)
            new_user = BlogUser.register(username = username,
                                         pw_hash = pw_hash,
                                         email = email)
            new_user.put()
            self.login(new_user)
            self.redirect("/blog")


class LoginHandler(main.BaseHandler):
    """ Provides methods to login blog users. """
    def get(self):
        if self.user:
            self.redirect("/blog")
        else:
            self.render("signin.html")

    def post(self):
        username = self.request.get("username")
        pwd = self.request.get("password")
        error = ""
        
        user = BlogUser.login(username, pwd)
        if user:
            self.login(user)
            self.redirect("/blog")
        else:
            error = "Invalid username or password."
            self.render('signin.html', username = username, error = error)


class LogoutHandler(main.BaseHandler):
    """ Provides methods to logout blog users. """
    def get(self):
        self.logout()
        self.redirect("/blog")


app = webapp2.WSGIApplication([("/signup", RegistrationHandler),
                               ("/signin", LoginHandler),
                               ("/logout", LogoutHandler)],
                              debug=True)


