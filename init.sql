CREATE TABLE categories (
    id SERIAL UNIQUE,
    category VARCHAR(30) UNIQUE NOT NULL,
    slug VARCHAR(30) UNIQUE NOT NULL
);

CREATE TABLE posts (
    id SERIAL UNIQUE,
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL,
    body TEXT,
    date_pub DATE NOT NULL DEFAULT CURRENT_DATE,
    category_id int REFERENCES categories (id) ON DELETE CASCADE
);

INSERT INTO categories (category, slug) VALUES ('First','first');
INSERT INTO categories (category, slug) VALUES ('Another cat', 'second-tag');
INSERT INTO categories (category, slug) VALUES ('Last cat!', 'last-cat');


INSERT INTO posts (title, slug, body, category_id)
VALUES ('First', 'first','Login: admin
Password: 1234567', 1);

INSERT INTO posts (title, slug, body, category_id)
VALUES ('Second post', 'second-post', 'Все смешалось в доме Облонских. Жена узнала, что муж был в связи с бывшею в их
доме француженкою-гувернанткой, и объявила мужу, что не может жить с ним в одном доме. Положение это продолжалось
уже третий день и мучительно чувствовалось и самими супругами, и всеми членами семьи, и домочадцами.', 2);

INSERT INTO posts (title, slug, body, category_id)
VALUES ('Third post', 'third-post', 'Все члены семьи и домочадцы чувствовали, что нет смысла в их сожительстве и
что на каждом постоялом дворе случайно сошедшиеся люди более связаны между собой, чем они, члены семьи и домочадцы
Облонских. Жена не выходила из своих комнат, мужа третий день не было дома.', 3);
