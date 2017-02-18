import main
from model import Post
from model import Comment
from model import BlogUser

import webapp2


class PostsListHandler(main.BaseHandler):
    """ Provides methods to show lists of blog posts. """
    def get(self, user_id = ""):
        if user_id:
            posts = Post.by_user(long(user_id))
        else:
            posts = Post.list_all()

        self.render('posts_list.html', posts = posts)


class NewPostHandler(main.BaseHandler):
    """ Provides methods to create blog posts. """
    def get(self):
        if not self.user:
            return self.redirect("/signin")

        self.render("new_post.html")    

    def post(self):
        if not self.user:
            return self.redirect('/signin')

        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            p = Post.create(title = subject, content = content,
                            user_id = self.user.key.id(),
                            username = self.user.username)
            p.put()
            self.redirect('/post/%s' % str(p.key.id()))
        else:
            error = "subject and content, please!"
            self.render("new_post.html", subject=subject, content=content,
                        error=error)


class PostPageHandler(main.BaseHandler):
    """ Provides methods to show posts's data. """
    def get(self, post_id):
        p = Post.by_id(long(post_id))
        if p:
            p.prep_render()
            self.render("post.html", post = p)
        else:
            self.render_error("404")


class EditPostHandler(main.BaseHandler):
    """ Provides methods to update posts's data. """
    def get(self, post_id):
        if not self.user:
            return self.redirect('/signin')
            
        p = Post.by_id(long(post_id))
        if not p:
           return self.render_error("404")
           
        if self.user.key.id() != p.user_id:
            return self.render_error("403")

        subject = p.title
        content = p.content
        pid = post_id
        self.render("edit_post.html", subject=subject, content=content,
                    pid = pid)


    def post(self, post_id):
        if not self.user:
            return self.redirect('/signin')

        p = Post.by_id(long(post_id))
        if not p:
           return self.render_error("404") 

        if self.user.key.id() != p.user_id:
            return self.render_error("403")
            
        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            p.title = subject
            p.content = content
            p.put()
            self.redirect('/post/%s' % str(p.key.id()))
        else:
            pid = post_id 
            error = "subject and content, please!"
            self.render("edit_post.html", subject = subject,
                        content = content, pid = pid, error = error)
            
            

class DeletePostHandler(main.BaseHandler):
    """ Provides methods to delete posts. """
    def post(self, post_id):
        if not self.user:
            return self.redirect("/signin")
            
        p = Post.by_id(long(post_id))
        if not p:
           return self.render_error("404")
           
        if self.user.key.id() != p.user_id:
            return self.render_error("403")

        p.delete_comments()
        p.key.delete()
        self.redirect("/blog")    


class NewCommentHandler(main.BaseHandler):
    """ Provides methods to create posts comments. """
    def post(self, post_id):
        if not self.user:
            return self.redirect("/signin")
            
        p = Post.by_id(long(post_id))
        if not p:
            return self.render_error("404")
            
        content = self.request.get('comment_content')
        if content:
            c = Comment.create(content = content,
                               username = self.user.username,
                               post_key = p.key,
                               user_key = self.user.key)
            c_key = c.put()
            p.comments.append(c.key)
            p.put()
            self.redirect("/post/%s" % post_id)
        else:
            p.prep_render()
            error_comment = "Write some words, please!"
            self.render("post.html", post = p,
                        error_comment = error_comment)
            

class EditCommentHandler(main.BaseHandler):
    """ Provides methods to update posts comments. """
    def get(self, comment_id):
        if not self.user:
            return self.redirect('/signin')
            
        c = Comment.by_id(long(comment_id))
        if not c:
            return self.render_error("404")

        if c.user_can_edit_delete(self.user):
            p = Post.by_id(long(c.post_id.id()))
            p.prep_render()
            self.render("edit_comment.html", post = p, comment = c)
        else:
            self.render_error("403")


    def post(self, comment_id):
        if not self.user:
            return self.redirect('/signin')

        c = Comment.by_id(long(comment_id))
        if not c:
            return self.render_error("404")

        if not c.user_can_edit_delete(self.user):
            return self.render_error("403")
            
        content = self.request.get('comment_content')
        if content:
            c.content = content
            c.put()
            self.redirect("/post/%s" % c.post_id.id())
        else:
            p = Post.by_id(long(c.post_id.id()))
            p.prep_render()
            c.content = ""
            error_comment = "Write some words, please!"
            self.render("edit_comment.html", post = p, comment = c,
                        error_comment = error_comment)
            

class DeleteCommentHandler(main.BaseHandler):
    """ Provides methods to delete posts comments. """
    def post(self, comment_id):
        if not self.user:
            return self.redirect("/signin")
            
        c = Comment.by_id(long(comment_id))
        if not c:
            return self.render_error("404")

        if c.user_can_edit_delete(self.user):
            p = Post.by_id(c.post_id.id())
            p.comments.remove(c.key)
            p.put()
            c.key.delete()
            self.redirect("/post/%s" % p.key.id())
        else:
            self.render_error("403")    
    


class LikePostHandler(main.BaseHandler):
    """ Provides methods to like posts. """
    def post(self, post_id):
        if not self.user:
            return self.redirect("/signin")

        p = Post.by_id(long(post_id))
        if not p:
           return self.render_error("404") 

        if p.user_can_like(self.user):
            p.likes.append(self.user.key)
            p.put()
            self.redirect("/post/%s" % post_id)
        else:
            self.render_error("403")



class UnlikePostHandler(main.BaseHandler):
    """ Provides methods to unlike posts. """
    def post(self, post_id):
        if not self.user:
            return self.redirect("/signin")

        p = Post.by_id(long(post_id))
        if not p:
            return self.render_error("404")

        if p.user_can_unlike(self.user):
            p.likes.remove(self.user.key)
            p.put()
            self.redirect("/post/%s" % post_id)
        else:
            self.render_error("403")    
        


                
app = webapp2.WSGIApplication([(r"/post/new", NewPostHandler),
                               (r"/post/([0-9]+)", PostPageHandler),
                               (r"/post/([0-9]+)/edit", EditPostHandler),
                               (r"/post/([0-9]+)/delete", DeletePostHandler),
                               (r"/", PostsListHandler),
                               (r"/blog/?", PostsListHandler),
                               (r"/blog/([0-9]+)/?", PostsListHandler),
                               (r"/comment/([0-9]+)/new", NewCommentHandler),
                               (r"/comment/([0-9]+)/edit", EditCommentHandler),
                               (r"/comment/([0-9]+)/delete", DeleteCommentHandler),
                               (r"/post/([0-9]+)/like", LikePostHandler),
                               (r"/post/([0-9]+)/unlike", UnlikePostHandler)],
                              debug=True)
