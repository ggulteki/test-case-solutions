import sqlite3
from typing import List
from dataclasses import dataclass

def init_database():
    try:
        db = sqlite3.connect('user.db')
        crsr = db.cursor()

        db.execute("DROP TABLE IF EXISTS USER")
        db.execute("DROP TABLE IF EXISTS POST")
        db.execute("DROP TABLE IF EXISTS FOLLOW")
        db.execute("DROP TABLE IF EXISTS LIKE")

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

if __name__ == "__main__":
    init_database()
    user_id = 2
    post_ids = [4, 2, 1]
    posts = get_posts(user_id, post_ids)
    print(posts)
