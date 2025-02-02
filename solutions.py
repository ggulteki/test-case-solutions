"""
File Name: solutions.py
Description: InfinitumIT's Backend Case SOLUTIONS
Author: gokberk gultekin
Date: 2/2/2025
"""

import sqlite3
from typing import List
from dataclasses import dataclass
from collections import defaultdict
from collections import deque

# TRANSFORM UNSUED SOLUTIONS BELOW INTO COMMENT BLOCKS BEFORE TRYING ANY SOLUTION TO PREVENT TECHNICAL CONFLICTS

def init_database():
    try:
        db = sqlite3.connect('user.db')
        crsr = db.cursor()

        db.execute("DROP TABLE IF EXISTS USER")
        db.execute("DROP TABLE IF EXISTS POST")
        db.execute("DROP TABLE IF EXISTS FOLLOW")
        db.execute("DROP TABLE IF EXISTS LIKE")
        # create necessary tables for implementing of solution
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

        crsr.execute(user)
        crsr.execute(post)
        crsr.execute(follow)
        crsr.execute(like)
        db.commit()
        print("All tables created successfully")
        # Add example users, posts, likes and follow & following datas for making and testing solution
        sql_statements = [
            "INSERT INTO USER (id, username, email, full_name) VALUES (1, 'alice', 'alice@example.com', 'Alice Smith')",
            "INSERT INTO USER (id, username, email, full_name) VALUES (2, 'bob', 'bob@example.com', 'Bob Johnson')",
            "INSERT INTO USER (id, username, email, full_name) VALUES (3, 'charlie', 'charlie@example.com', 'Charlie Brown')",
            "INSERT INTO POST (description, user_id, image) VALUES ('Hello World!', 1, 'image1.jpg')",
            "INSERT INTO POST (description, user_id, image) VALUES ('My first post!', 2, 'image2.jpg')",
            "INSERT INTO POST (description, user_id, image) VALUES ('Loving this platform!', 1, 'image3.jpg')",
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
        db.commit()

    except sqlite3.Error as e:
        print(f"Error occurred: {e}")
        db.rollback()
    finally:
        if db:
            db.close()

# Solution 1:
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
    created_at: int
    liked: bool

def get_posts(user_id: int, post_ids: List[int]) -> List[Post]:
    db = None
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

        req_user = User(id=req_user_row[0], username=req_user_row[1], full_name=req_user_row[2], profile_picture=req_user_row[3], followed=False) # requester object

        for post_id in post_ids:
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
    except ValueError as ve:
        print(ve)  # Handle the case where the user is not found
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

# Solution 2:
@dataclass
class Post:
    id: int
    owner_id: int

def mix_by_owners(posts: List[Post]) -> List[Post]:

    owner_posts = defaultdict(deque)

    mixed_posts = []
    # Use set() for ensure unique owner_ids
    owner_ids = set()
    # AVG COMPLEXITY IS O(N)
    for post in posts:
        # map posts to their related owner_ids
        owner_posts[post.owner_id].append(post) # O(1)
        owner_ids.add(post.owner_id) # 0(1)
    # AVG COMPLEXITY IS O(N)
    while True:
        add = False
        for owner_id in owner_ids:
            if owner_posts[owner_id]:
                mixed_posts.append(owner_posts[owner_id].popleft()) # O(1)
                add = True
        if not add:
            break
    # OVERALL COMPLEXITY IS O(N)
    return mixed_posts

#
if __name__ == "__main__":
    '''######### uncomment this block to test solution 1 #########
    # Test cases for Q1

    user_id = 2
    post_ids = [2, 3, 1]

    user_id = 2
    post_ids = [4, 2, 1]

    user_id = 4
    post_ids = [2, 3, 1]

    posts = get_posts(user_id, post_ids)
    print(posts)
    '''

# Example Input for Solution 2:
# Note: Question 2 focuses only on algorithm design instead of db access. Therefore, I decided to use the example input shown in the PDF.
'''
Input: [Post(id=1, owner_id=2), Post(id=2, owner_id=2), Post(id=3, owner_id=2), Post(id=5,
owner_id=3), Post(id=7, owner_id=3), Post(id=4, owner_id=4)]

'''
''' ######### uncomment this block to test solution 2 #########
Posts = []
# The Post object is defined above the function signature..
post_1 = Post(id=1, owner_id=2)
Posts.append(post_1)
post_2 = Post(id=2, owner_id=2)
Posts.append(post_2)
post_3 = Post(id=3, owner_id=2)
Posts.append(post_3)
post_4 = Post(id=5, owner_id=3)
Posts.append(post_4)
post_5 = Post(id=7, owner_id=3)
Posts.append(post_5)
post_6 = Post(id=4, owner_id=4)
Posts.append(post_6)


mixed_posts = mix_by_owners(Posts)
print(mixed_posts)
'''
