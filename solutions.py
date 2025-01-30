import sqlite3

try:
    db = sqlite3.connect('user.db')
    crsr = db.cursor()

    db.execute("DROP TABLE IF EXISTS USER")
    db.execute("DROP TABLE IF EXISTS POST")
    db.execute("DROP TABLE IF EXISTS FOLLOW")
    db.execute("DROP TABLE IF EXISTS LIKE")

    print("Connected to the db")

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
