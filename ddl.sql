-- Users
CREATE TABLE users (
	id SERIAL PRIMARY KEY,
	account_id INTEGER,
	reputation INTEGER NOT NULL,
	views INTEGER DEFAULT 0,
	down_votes INTEGER DEFAULT 0,
	up_votes INTEGER DEFAULT 0,
	display_name VARCHAR(255) NOT NULL,
	location VARCHAR(512),
	profile_image_url VARCHAR(255),
	website_url VARCHAR(255),
	about_me TEXT,
	creation_date TIMESTAMP NOT NULL,
	last_access_date TIMESTAMP NOT NULL
);

-- Posts
CREATE TABLE posts (
	id SERIAL PRIMARY KEY,
	owner_user_id INTEGER,
	last_editor_user_id INTEGER,
	post_type_id SMALLINT NOT NULL,
	accepted_answer_id INTEGER,
	score INTEGER NOT NULL,
	parent_id INTEGER,
	view_count INTEGER,
	answer_count INTEGER DEFAULT 0,
	comment_count INTEGER DEFAULT 0,
	owner_display_name VARCHAR(64),
	last_editor_display_name VARCHAR(64),
	title VARCHAR(512),
	tags VARCHAR(512),
	content_license VARCHAR(64) NOT NULL,
	body TEXT,
	favorite_count INTEGER,
	creation_date TIMESTAMP NOT NULL,
	community_owned_date TIMESTAMP,
	closed_date TIMESTAMP,
	last_edit_date TIMESTAMP,
	last_activity_date TIMESTAMP,
	CONSTRAINT post_user
      FOREIGN KEY(owner_user_id) 
	  REFERENCES users(id)
);
CREATE INDEX ix_posts_parent_id ON posts (parent_id);

-- PostLinks
CREATE TABLE post_links (
	id SERIAL PRIMARY KEY,
	related_post_id INTEGER NOT NULL,
	post_id INTEGER NOT NULL,
	link_type_id SMALLINT NOT NULL,
	creation_date TIMESTAMP NOT NULL
);

-- PostHistory
CREATE TABLE post_history (
	id SERIAL PRIMARY KEY,
	post_id INTEGER NOT NULL,
	user_id INTEGER,
	post_history_type_id SMALLINT NOT NULL,
	user_display_name VARCHAR(64),
	content_license VARCHAR(64),
	revision_guid uuid,
	text TEXT,
	comment TEXT,
	creation_date TIMESTAMP NOT NULL,
	CONSTRAINT post_h
      FOREIGN KEY(post_id) 
	  REFERENCES posts(id),
	CONSTRAINT post_h2
      FOREIGN KEY(user_id) 
	  REFERENCES users(id)
);

-- Comments
CREATE TABLE comments (
	id SERIAL PRIMARY KEY,
	post_id INTEGER NOT NULL,
	user_id INTEGER,
	score SMALLINT NOT NULL,
	content_license VARCHAR(64) NOT NULL,
	user_display_name VARCHAR(64),
	text TEXT,
	creation_date TIMESTAMP NOT NULL,
	CONSTRAINT comm1
      FOREIGN KEY(post_id) 
	  REFERENCES posts(id),
	CONSTRAINT comm2
      FOREIGN KEY(user_id) 
	  REFERENCES users(id)
);
CREATE INDEX ix_comments_post_id ON comments (post_id);

-- Votes
CREATE TABLE votes (
	id SERIAL PRIMARY KEY,
	user_id INTEGER,
	post_id INTEGER NOT NULL,
	vote_type_id SMALLINT NOT NULL,
	bounty_amount SMALLINT,
	creation_date TIMESTAMP NOT NULL,
	CONSTRAINT vote2
      FOREIGN KEY(user_id) 
	  REFERENCES users(id)
);

-- Badges
CREATE TABLE badges (
	id SERIAL PRIMARY KEY,
	user_id INTEGER NOT NULL,
	class SMALLINT NOT NULL,
	name VARCHAR(64) NOT NULL,
	tag_based BOOL NOT NULL,
	date TIMESTAMP NOT NULL,
	CONSTRAINT badg
      FOREIGN KEY(user_id) 
	  REFERENCES users(id)
);

-- Tags
CREATE TABLE tags (
	id SERIAL PRIMARY KEY,
	excerpt_post_id INTEGER,
	wiki_post_id INTEGER,
	tag_name VARCHAR(255) NOT NULL,
	count INTEGER DEFAULT 0
);

\COPY users FROM 'Users.csv' DELIMITER ',' CSV HEADER;
\COPY posts FROM 'Posts.csv' DELIMITER ',' CSV HEADER;
\COPY tags FROM 'Tags.csv' DELIMITER ',' CSV HEADER;
\COPY comments FROM 'Comments.csv' DELIMITER ',' CSV HEADER;
\COPY badges FROM 'Badges.csv' DELIMITER ',' CSV HEADER;
\COPY votes FROM 'Votes.csv' DELIMITER ',' CSV HEADER;
\COPY post_links FROM 'PostLinks.csv' DELIMITER ',' CSV HEADER;
\COPY post_history FROM 'PostHistory.csv' DELIMITER ',' CSV HEADER;
