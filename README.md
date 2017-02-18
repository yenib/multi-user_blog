# Multi user blog

Written in Python 2.7.6 using [Google App Engine][gae-url] and [Jinja2][jinja-url]. It demonstrates how to use the Google App Engine and its [Google Cloud Datastore][gae-gcd-url] built-in service to build web applications.

**Features:**
- register and authenticate users
- Logged users can create, read, update and delete posts and post comments
- Logged users can like and dislike posts

The application can be accessed here: [https://multiuser-blog-154823.appspot.com](https://multiuser-blog-154823.appspot.com)


## Instructions to run the application

It can be deployed in the Google App Engine Standard Environment by following these steps:
  - Create a new Cloud Platform Console project [here](https://console.cloud.google.com/project?_ga=1.157983420.768532589.1478804871).
  - Install and initialize the Google Cloud SDK. Go [here](https://cloud.google.com/sdk/docs/).
  - Deploy the application by following [this](https://cloud.google.com/appengine/docs/python/getting-started/deploying-the-application) guide.

... or it can be ran locally on a computer by installing and initializing the Google Cloud SDK, which will provide a local development server. Follow [this](https://cloud.google.com/sdk/docs/) and [this](https://cloud.google.com/appengine/docs/python/getting-started/creating-guestbook) guides.


## License

Distributed under the [Apache 2.0](http://www.apache.org/licenses/LICENSE-2.0) license.


[gae-url]: https://cloud.google.com/appengine/
[jinja-url]: http://jinja.pocoo.org/docs/2.9/
[gae-gcd-url]: https://cloud.google.com/appengine/docs/python/datastore/