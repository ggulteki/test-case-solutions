"""
File Name: solutions.py
Description: InfinitumIT's Backend Case SOLUTIONS
Author: gokberk gultekin
Date: 2/2/2025
"""

import sqlite3
from time import sleep
from typing import List
from dataclasses import dataclass
from collections import defaultdict
from collections import deque

# User and Post objects for a simple implementation of the problems.
@dataclass
class User:
    id: int
    username: str
    full_name: str
    profile_picture: str
    followed: bool

@dataclass
class Post:
    id: int
    description: str
    owner: User
    image: str
    created_at: str
    liked: bool

# Database initialization function for solutions. I chose SQLite3 because of its simplicity.
def init_database():
    try:
        db = sqlite3.connect('user.db')
        crsr = db.cursor()

        # Drop existing tables to ensure a fresh database setup.
        db.execute("DROP TABLE IF EXISTS USER")
        db.execute("DROP TABLE IF EXISTS POST")
        db.execute("DROP TABLE IF EXISTS FOLLOW")
        db.execute("DROP TABLE IF EXISTS LIKE")

        # Create necessary tables for the solutions implementation
        user = """ CREATE TABLE USER (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL,
                    full_name VARCHAR(25) NOT NULL,
                    profile_picture VARCHAR(255),
                    bio VARCHAR(255),
                    created_at DATE DEFAULT (datetime('now','localtime'))
                )"""

        post = """ CREATE TABLE POST (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    description VARCHAR(255) NOT NULL,
                    user_id INTEGER NOT NULL,
                    image VARCHAR(255),
                    created_at DATE DEFAULT (datetime('now','localtime')),
                    FOREIGN KEY (user_id) REFERENCES USER(id) ON DELETE CASCADE
                )"""

        follow = """ CREATE TABLE FOLLOW (
                    follower_id INT NOT NULL,
                    following_id INT NOT NULL,
                    created_at DATE DEFAULT (datetime('now','localtime')),
                    PRIMARY KEY (follower_id, following_id),
                    FOREIGN KEY (follower_id) REFERENCES USER(id) ON DELETE CASCADE,
                    FOREIGN KEY (following_id) REFERENCES USER(id) ON DELETE CASCADE
                )"""

        like = """ CREATE TABLE LIKE (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    post_id INT NOT NULL,
                    user_id INT NOT NULL,
                    created_at DATE DEFAULT (datetime('now','localtime')),
                    FOREIGN KEY (post_id) REFERENCES POST(id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES USER(id) ON DELETE CASCADE
                )"""

        # Execute the queries to create the tables.
        crsr.execute(user)
        crsr.execute(post)
        crsr.execute(follow)
        crsr.execute(like)

        # Save changes to the database
        db.commit()

        print("All tables created successfully")

        # Add example users, posts, likes and follow & following datas for making and testing solution
        sql_statements = [
            "INSERT INTO USER (username, email, full_name) VALUES ('alice', 'alice@example.com', 'Alice Smith')",
            "INSERT INTO USER (username, email, full_name) VALUES ('bob', 'bob@example.com', 'Bob Johnson')",
            "INSERT INTO USER (username, email, full_name) VALUES ('charlie', 'charlie@example.com', 'Charlie Brown')",
            "INSERT INTO USER (username, email, full_name) VALUES ('david', 'david@example.com', 'David Howard')",
            "INSERT INTO POST (description, user_id, image) VALUES ('My first post!', 2, 'image1.jpg')",
            "INSERT INTO POST (description, user_id, image) VALUES ('Hello!', 2, 'image2.jpg')",
            "INSERT INTO POST (description, user_id, image) VALUES ('Loving this platform!', 2, 'image3.jpg')",
            "INSERT INTO POST (description, user_id, image) VALUES ('Hi Everyone!', 4, 'image1.jpg')",
            "INSERT INTO POST (description, user_id, image) VALUES ('Awesome!', 3, 'image2.jpg')",
            "INSERT INTO POST (description, user_id, image) VALUES ('Hola!', 1, 'image3.jpg')",
            "INSERT INTO POST (description, user_id, image) VALUES ('Love.', 3, 'image3.jpg')",
            "INSERT INTO FOLLOW (follower_id, following_id) VALUES (1, 2)",
            "INSERT INTO FOLLOW (follower_id, following_id) VALUES (1, 3)",
            "INSERT INTO FOLLOW (follower_id, following_id) VALUES (2, 3)",
            "INSERT INTO LIKE (post_id, user_id) VALUES (1, 2)",
            "INSERT INTO LIKE (post_id, user_id) VALUES (2, 1)",
            "INSERT INTO LIKE (post_id, user_id) VALUES (3, 3)"
        ]

        # Execute each SQL statement individually
        for statement in sql_statements:
            crsr.execute(statement)
            # 1 second interval to ensure different created_at values for solution 3
            sleep(1)

        db.commit()

    # Error handling for any database processes
    except sqlite3.Error as e:
        print(f"Error occurred: {e}")
        # Undo last modifications and restore the database
        db.rollback()

    finally:
        if db:
            # Terminate the database connection after all processes have been completed successfully.
            db.close()

"""Solution 1:"""

def get_posts(user_id: int, post_ids: List[int]) -> List[Post]:

    # Remove duplicates from post_ids if they exist
    unique_ids = list(dict.fromkeys(post_ids))

    out = []

    try:
        db = sqlite3.connect('user.db')
        crsr = db.cursor()

        # Get the requesting user
        crsr.execute("SELECT id, username, full_name, profile_picture FROM USER WHERE id = ?", (user_id,))
        req_user_row = crsr.fetchone()

        # Error handle for non-existing user
        if req_user_row is None:
            raise ValueError("User not found")
        # Requester object
        req_user = User(id=req_user_row[0], username=req_user_row[1], full_name=req_user_row[2], profile_picture=req_user_row[3], followed=False)

        for post_id in unique_ids:
            crsr.execute("SELECT id, description, user_id, image, created_at FROM POST WHERE id = ?", (post_id,))
            post_row = crsr.fetchone()
            if post_row is None:
                out.append(None)
                continue

            # post object
            post = Post(id=post_row[0], description=post_row[1], owner=None, image=post_row[3], created_at=post_row[4], liked=False)

            # Get the owner user
            crsr.execute("SELECT id, username, full_name, profile_picture FROM USER WHERE id = ?", (post_row[2],))
            own_row = crsr.fetchone()

            # owner object
            owner = User(id=own_row[0], username=own_row[1], full_name=own_row[2], profile_picture=own_row[3], followed=False)

            post.owner = owner

            # Detect owner followed
            crsr.execute("SELECT follower_id FROM FOLLOW WHERE follower_id = ? AND following_id = ?", (req_user.id, owner.id))
            followed_out = crsr.fetchone()
            if followed_out is not None:
                owner.followed = True

            # Detect liked requester
            crsr.execute("SELECT id FROM LIKE WHERE post_id = ? AND user_id = ?", (post.id, req_user.id,))
            like_out = crsr.fetchone()
            if like_out is not None:
                post.liked = True

            out.append(post)

    except sqlite3.Error as e:
        print(f"Error executing query: {e}")
        if db:
            db.rollback()

    # Handle the case where the user is not found
    except ValueError as ve:
        print(ve)

    finally:
        if db:
            db.close()

    return out

# My limitations in guaranteeing the worst-case O(N) time complexity:

# DO:

# Use single-pass loops (O(N)).
# Use hash maps or sets if they improve lookup efficiency.
# Use linear-time sorting (if applicable, e.g., counting sort).

# AVOID:

# Nested loops that cause O(N²) complexity.
# Sorting unless absolutely necessary (O(N log N)).
# Recursive solutions without memoization, as they might have exponential time complexity.
# Unoptimized hash table operations, which can degrade to O(N) in the worst case.

"""Solution 2:"""

def mix_by_owners(posts: List[Post]) -> List[Post]:

    # Initialize a deque dictionary for efficiently mapping owners to posts
    owner_posts = defaultdict(deque)

    # Initialize a list for the function's output
    mixed_posts = []

    # O(N)
    for post in posts:
        # map owner to posts
        owner_posts[post.owner].append(post) # O(1)

    # Retrieve unique owner_ids into a deque using the keys() method from the dictionary
    # Deque operations are more efficient than lists; that's why I used a deque here.
    owner_ids = deque(owner_posts.keys())

    # O(N)
    while owner_ids:
        # Retrieve the current owner ID from the deque
        owner = owner_ids.popleft()

        # Add the related post for the current owner ID to the output list
        mixed_posts.append(owner_posts[owner].popleft())

        # Check for multiple posts for the current owner_id to ensure all posts have been processed
        # If current owner_id is related to multiple posts, append it to the right end of the owner_ids to solve this problem
        if owner_posts[owner]:
            owner_ids.append(owner)

    # Total worst-case time complexity is: O(N)
    return mixed_posts

""" Solution 3: """

def merge_posts(list_of_posts: List[List[Post]]) -> List[Post]:

    merged_posts = []
    # AVG COMPLEXITY IS O(N)
    for list_of_post in list_of_posts:
        # Add elements from the inner lists to the output list
        merged_posts.extend(list_of_post)

    merged_posts.reverse() # O(N)

    # OVERALL COMPLEXITY IS O(N)
    return merged_posts


# NOTE: THERE ARE THREE TEST BLOCKS FOR SOLUTIONS. UNCOMMENT THE RELATED TEST BLOCK FOR TESTING THE SOLUTION

def main():

    init_database()

    """TEST CASE FOR Q1"""

    """

    user_id = 1
    post_ids = [10, 3, 2, 4, 3]

    posts = get_posts(user_id, post_ids)

    print(posts)

    """


    """TEST CASE FOR Q2"""

    """

    # Get necessary posts for perform Q2 Example
    user_id = 1
    post_ids = [1, 2, 3, 4, 5, 7]
    posts = get_posts(user_id, post_ids)

    # Delete unnecessary attributes to ensure the structure assumption for question 2
    for post in posts:
        post.owner = post.owner.id
        post.description = None
        post.image = None
        post.created_at = None
        post.liked = None

    # Sort the posts to ensure the first assumption for question 2 is met
    sorted_posts = sorted(posts, key=lambda post: (post.owner, post.id))

    # Print the solution to the terminal
    print(sorted_posts)
    print(" ")
    print(" ")
    print(mix_by_owners(sorted_posts))

    """


    """TEST CASE FOR Q3"""

    """

    # Get all posts from db for Q3 Example

    user_id = 1

    post_ids = [1, 2, 3, 4, 5, 6, 7]
    posts_lists = []

    # Get nested list
    for post_id in post_ids:
        posts_lists.append(get_posts(user_id, [post_id]))

    # Delete unnecessary attributes to ensure the structure assumption for question 3
    for posts_list in posts_lists:
        for post in  posts_list:
            post.owner = None
            post.liked = None

    merged_posts = merge_posts(posts_lists)

    print(merged_posts)

    """

if __name__ == "__main__":
    main()
