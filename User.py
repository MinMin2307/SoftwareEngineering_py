from Post import Post


class User:
    def __init__(self, first_name, last_name):
        self.id = None
        self.first_name = first_name
        self.last_name = last_name
        self.posts = []

    def add_post(self, image, text):
        post = Post(image, text, self)
        self.posts.append(post)
        return post