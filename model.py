import main
from google.appengine.ext import ndb


class BlogUser(ndb.Model):
    """ Represents a user of the application. """
    username = ndb.StringProperty(required = True)
    name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    password = ndb.StringProperty(required = True)
    email = ndb.StringProperty()
    dob = ndb.DateProperty()
    created = ndb.DateTimeProperty(auto_now_add = True)

    @classmethod
    def by_id(cls, user_id):
        return BlogUser.get_by_id(user_id)

    @classmethod
    def by_username(cls, username):
        return BlogUser.query().filter(BlogUser.username == username).get()

    @classmethod
    def register(cls, username, pw_hash, email = None):
        return BlogUser(username = username,
                        password = pw_hash,
                        email = email)

    @classmethod
    def login(cls, username, pwd):
        u = BlogUser.by_username(username)
        if u and main.valid_pw(username, pwd, u.password):
            return u


class Comment(ndb.Model):
    """ Represents a post comment. """
    post_id = ndb.KeyProperty(kind='Post')
    user_id = ndb.KeyProperty(kind='BlogUser')
    username = ndb.StringProperty(required = True)
    content = ndb.TextProperty(required = True)
    created = ndb.DateTimeProperty(auto_now_add = True)
    

    @classmethod
    def by_id(cls, comment_id):
        return Comment.get_by_id(comment_id)

    @classmethod
    def by_post(cls, post_key):
        q = Comment.query(Comment.post_id == post_key).order(-Comment.created)
        return q.fetch()

    @classmethod
    def create(cls, content, username, post_key, user_key):
        return Comment(content = content, username = username,
                       post_id = post_key, user_id = user_key)

    def prep_render(self):
        """ Preprocesses the comment for rendering. """
        self._render_content = self.content.replace('\n', '<br>')

    def user_can_edit_delete(self, user):
        """ Checks whether the comment can be edited or deleted by a user. """
        if user:
            c = Comment.query(Comment.post_id == self.post_id).order(
                -Comment.created).get()
            return self.key == c.key and user.username == self.username
        return False

        
class Post(ndb.Model):
    """ Represents a blog post. """
    title = ndb.StringProperty(required = True)
    content = ndb.TextProperty(required = True)
    created = ndb.DateTimeProperty(auto_now_add = True)
    last_modified = ndb.DateTimeProperty(auto_now = True)
    user_id = ndb.IntegerProperty(required = True)
    username = ndb.StringProperty(required = True)
    likes = ndb.KeyProperty(kind = "BlogUser", repeated = True)
    comments = ndb.KeyProperty(kind = "Comment", repeated = True)

    @property
    def likes_count(self):
        return len(self.likes)   

    @classmethod
    def list_all(cls):
        return Post.query().order(-Post.created).fetch()

    @classmethod
    def by_id(cls, post_id):
        return Post.get_by_id(post_id)

    @classmethod
    def by_user(cls, user_id):
        q = Post.query().filter(Post.user_id == user_id).order(-Post.created)
        return q.fetch()

    @classmethod
    def create(cls, title, content, user_id, username):
        return Post(title = title,
                    content = content,
                    user_id = user_id,
                    username = username)

    def delete_comments(self):
        ndb.delete_multi(self.comments)    

    def list_comments(self):
        return Comment.by_post(self.key)

    def comments_count(self):
        return len(self.comments)

    def user_can_like(self, user):
        """ Checks whether a user can like the post. """
        return user and not (user.key.id() == self.user_id or
                             user.key in self.likes)

    def user_can_unlike(self, user):
        """ Checks whether a user can unlike the post. """
        return user and user.key in self.likes

    def prep_render(self):
        """ Preprocesses the post for rendering. """
        self._render_content = self.content.replace('\n', '<br>')

    def prep_render_comments(self):
        """ Preprocesses the post's comment list for rendering. """
        comments = self.list_comments()
        for c in comments:
            c.prep_render()
        return comments
