CREATE TABLE categories (
    id SERIAL UNIQUE,
    category VARCHAR(30) UNIQUE NOT NULL,
    slug VARCHAR(30) UNIQUE NOT NULL
);

CREATE TABLE posts (
    id SERIAL UNIQUE,
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL,
    body TEXT
    category_id int REFERENCES categories (id) ON DELETE CASCADE
);

INSERT INTO categories (category, slug) VALUES ('First','first');
INSERT INTO categories (category, slug) VALUES ('Another cat', 'second-tag');
INSERT INTO categories (category, slug) VALUES ('Last cat!', 'last-cat');


INSERT INTO posts (title, slug, body, category_id)
VALUES ('First', 'first','',
1);

INSERT INTO posts (title, slug, body)
VALUES ('Second post', 'second-post', 'Еще какой-то текст, не имеющий особого смысла, но необходимый для заполнения', 2);

INSERT INTO posts (title, slug, body)
VALUES ('Third post', 'third-post', 'Последний текст, не имеющий особого смысла, но необходимый для заполнения', 3);






