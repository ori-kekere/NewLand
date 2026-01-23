-- User table
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(125) UNIQUE,
    username VARCHAR(60) UNIQUE,
    password VARCHAR(100),
    date_created DATETIME,
    bio TEXT DEFAULT "",
    profile_pic VARCHAR(300) DEFAULT "default.png",
    profile_image VARCHAR(150),
    CHECK (length(email) <= 125),
    CHECK (length(username) <= 60),
    CHECK (length(password) <= 100),
    CHECK (length(profile_pic) <= 300),
    CHECK (length(profile_image) <= 150)
);

-- Follow table
CREATE TABLE follow (
    id INTEGER PRIMARY KEY,
    follower_id INTEGER,
    followed_id INTEGER,
    FOREIGN KEY (follower_id) REFERENCES user (id),
    FOREIGN KEY (followed_id) REFERENCES user (id)
);

-- Post table
CREATE TABLE post (
    id INTEGER PRIMARY KEY,
    text TEXT NOT NULL,
    date_created DATETIME,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user (id) ON DELETE CASCADE
);

-- Comment table
CREATE TABLE comment (
    id INTEGER PRIMARY KEY,
    text VARCHAR(225) NOT NULL,
    date_created DATETIME,
    user_id INTEGER NOT NULL,
    post_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user (id) ON DELETE CASCADE,
    FOREIGN KEY (post_id) REFERENCES post (id) ON DELETE CASCADE,
    CHECK (length(text) <= 225)
);

-- Art table
CREATE TABLE art (
    id INTEGER PRIMARY KEY,
    title VARCHAR(150),
    art VARCHAR(150),
    date_created DATETIME,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user (id) ON DELETE CASCADE,
    CHECK (length(title) <= 150),
    CHECK (length(art) <= 150)
);

-- ArtComment table
CREATE TABLE art_comment (
    id INTEGER PRIMARY KEY,
    text VARCHAR(225) NOT NULL,
    date_created DATETIME,
    user_id INTEGER NOT NULL,
    art_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user (id) ON DELETE CASCADE,
    FOREIGN KEY (art_id) REFERENCES art (id) ON DELETE CASCADE,
    CHECK (length(text) <= 225)
);

-- Video table
CREATE TABLE video (
    id INTEGER PRIMARY KEY,
    title VARCHAR(150),
    video VARCHAR(150) NOT NULL,
    date_created DATETIME,
    views INTEGER DEFAULT 0,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user (id) ON DELETE CASCADE,
    CHECK (length(title) <= 150),
    CHECK (length(video) <= 150)
);

-- VideoComment table
CREATE TABLE video_comment (
    id INTEGER PRIMARY KEY,
    text VARCHAR(500) NOT NULL,
    date_created DATETIME,
    user_id INTEGER NOT NULL,
    video_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user (id) ON DELETE CASCADE,
    FOREIGN KEY (video_id) REFERENCES video (id) ON DELETE CASCADE,
    CHECK (length(text) <= 500)
);

-- Like table
CREATE TABLE likes (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    post_id INTEGER NOT NULL,
    post_type VARCHAR(10) NOT NULL,
    date_created DATETIME,
    FOREIGN KEY (user_id) REFERENCES user (id) ON DELETE CASCADE,
    CONSTRAINT unique_like UNIQUE (user_id, post_id, post_type),
    CHECK (length(post_type) <= 10)
);

-- Notification table
CREATE TABLE notification (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    from_user_id INTEGER NOT NULL,
    type VARCHAR(20) NOT NULL,
    object_id INTEGER,
    object_type VARCHAR(20),
    is_read BOOLEAN DEFAULT 0,
    date_created DATETIME,
    FOREIGN KEY (user_id) REFERENCES user (id),
    FOREIGN KEY (from_user_id) REFERENCES user (id),
    CHECK (length(type) <= 20),
    CHECK (length(object_type) <= 20)
);
