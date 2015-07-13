import unittest
import os
import json
from urlparse import urlparse

#from flask.ext.restless import APIManager

# Configure our app to use the testing databse
os.environ["CONFIG_PATH"] = "posts.config.TestingConfig"

from posts import app
from posts import models
from posts.database import Base, engine, session

class TestAPI(unittest.TestCase):
    """ Tests for the posts API """

    def setUp(self):
        """ Test setup """
        self.client = app.test_client()
        #apimanager = APIManager(app)
        #apimanager.create_api(post, methods=['GET', 'POST', 'DELETE'])
        # Set up the tables in the database
        Base.metadata.create_all(engine)
        
    def testGetEmptyPosts(self):
        """ Getting posts from an empty database """
        response = self.client.get("/api/posts",
            headers=[("Accept", "application/json")]
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")

        data = json.loads(response.data)
        self.assertEqual(data, [])
        
    def testGetPosts(self):
        """ Getting posts from a populated database """
        postA = models.Post(title="Example Post A", body="Just a test")
        postB = models.Post(title="Example Post B", body="Still a test")

        session.add_all([postA, postB])
        session.commit()

        response = self.client.get("/api/posts",
            headers=[("Accept", "application/json")]
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")

        data = json.loads(response.data)
        self.assertEqual(len(data), 2)

        postA = data[0]
        self.assertEqual(postA["title"], "Example Post A")
        self.assertEqual(postA["body"], "Just a test")

        postB = data[1]
        self.assertEqual(postB["title"], "Example Post B")
        self.assertEqual(postB["body"], "Still a test")
        
    def testGetPost(self):
        """ Getting a single post from a populated database """
        postA = models.Post(title="Example Post A", body="Just a test")
        postB = models.Post(title="Example Post B", body="Still a test")

        session.add_all([postA, postB])
        session.commit()

        response = self.client.get("/api/posts/{}".format(postB.id), headers=[("Accept", "application/json")])

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")

        post = json.loads(response.data)
        self.assertEqual(post["title"], "Example Post B")
        self.assertEqual(post["body"], "Still a test")
        
    def testDeletePost(self):
        """ Deleting a single post from a populated database """
        
        # Adding posts to delete one
        postA = models.Post(title="Example Post A", body="Just a test")
        postB = models.Post(title="Example Post B", body="Still a test")
        session.add_all([postA, postB])
        session.commit()
        
        # Deleting the post
        response = self.client.delete("/api/posts/{}".format(postB.id), headers=[("Accept", "application/json")])
        #tests for response after deletion
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.mimetype, "application/json")
        
        # Trying to get the post after deletion
        response = self.client.delete("/api/posts/{}".format(postB.id), headers=[("Accept", "application/json")])
        # Tests for response when trying to get a post after deletion
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.mimetype, "application/json")
        post = json.loads(response.data)
        self.assertEqual(post["message"], 'Could not find post with id 2')
        
    def testGetPostsWithTitle(self):
        """ Filtering posts by title """
        
        # Adding all the posts
        postA = models.Post(title="Post with bells", body="Just a bells test")
        postB = models.Post(title="Post with whistles", body="Still a whistles test")
        postC = models.Post(title="Post with bells and whistles", body="Another bells test")
        session.add_all([postA, postB, postC])
        session.commit()

        # Getting a response for posts with title like "whistles"
        response = self.client.get("/api/posts?title_like=whistles", headers=[("Accept", "application/json")])

        # Testing the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        # Getting the posts back
        posts = json.loads(response.data)
        # Testing that we got 2 posts back
        self.assertEqual(len(posts), 2)
        # Testing the content of the posts returned
        post = posts[0]
        self.assertEqual(post["title"], "Post with whistles")
        self.assertEqual(post["body"], "Still a whistles test")
        post = posts[1]
        self.assertEqual(post["title"], "Post with bells and whistles")
        self.assertEqual(post["body"], "Another bells test")
    
    def testGetPostsWithBody(self):
        """ Filtering posts by body """
        
        # Adding all the posts
        postA = models.Post(title="Post with bells", body="Just a bells test")
        postB = models.Post(title="Post with whistles", body="Still a whistles test")
        postC = models.Post(title="Post with bells and whistles", body="Another bells test")
        session.add_all([postA, postB, postC])
        session.commit()

        # Getting the response for posts with body like "bells"
        response = self.client.get("/api/posts?body_like=bells", headers=[("Accept", "application/json")])
        
        # Testing the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        # Getting the posts back
        posts = json.loads(response.data)
        #Testing that we got 2 posts back
        self.assertEqual(len(posts), 2)
        # Testing the content of the posts returned
        post = posts[0]
        self.assertEqual(post["title"], "Post with bells")
        self.assertEqual(post["body"], "Just a bells test")
        post = posts[1]
        self.assertEqual(post["title"], "Post with bells and whistles")
        self.assertEqual(post["body"], "Another bells test")
        
    def testGetPostsWithTitleAndBody(self):
        """ Filtering posts by title and body """

        # Adding all the posts
        postA = models.Post(title="Post with bells", body="Just a bells test")
        postB = models.Post(title="Post with whistles", body="Another whistles test")
        postC = models.Post(title="Post with bells and whistles", body="Another bells test")
        session.add_all([postA, postB, postC])
        session.commit()
        
        # Getting response for posts with title like "whistles" and body like "bells"
        response = self.client.get("/api/posts?title_like=whistles&body_like=bells", headers=[("Accept", "application/json")])
        # Testing the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        # Getting the posts back
        posts = json.loads(response.data)
        # Getting the post back
        self.assertEqual(len(posts), 1)
        # Testing the content of the post returned
        post = posts[0]
        self.assertEqual(post["title"], "Post with bells and whistles" )
        self.assertEqual(post["body"], "Another bells test" )        
        
    def testGetNonExistentPost(self):
        """ Getting a single post which doesn't exist """
        response = self.client.get("/api/posts/1", headers=[("Accept", "application/json")])

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.mimetype, "application/json")

        data = json.loads(response.data)
        self.assertEqual(data["message"], "Could not find post with id 1")
        
    def testUnsupportedAcceptHeader(self):
        response = self.client.get("/api/posts",
            headers=[("Accept", "application/xml")]
        )

        self.assertEqual(response.status_code, 406)
        self.assertEqual(response.mimetype, "application/json")

        data = json.loads(response.data)
        self.assertEqual(data["message"],
                         "Request must accept application/json data")
    
    def tearDown(self):
        """ Test teardown """
        session.close()
        # Remove the tables and their data from the database
        Base.metadata.drop_all(engine)

if __name__ == "__main__":
    unittest.main()
