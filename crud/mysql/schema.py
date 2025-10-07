import aiomysql


async def create_tables(cursor: aiomysql.Cursor):
    create_table_queries = [
        """
        CREATE TABLE IF NOT EXISTS `api_keys` (
          `id` int(11) NOT NULL AUTO_INCREMENT,
          `user_id` int(11) NOT NULL,
          `api_key` varchar(25) NOT NULL,
          `created_at` datetime NOT NULL DEFAULT current_timestamp(),
          PRIMARY KEY (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
        """,
        """
        CREATE TABLE IF NOT EXISTS `categories` (
          `id` int(11) NOT NULL AUTO_INCREMENT,
          `name` varchar(100) NOT NULL,
          `description` varchar(250) NOT NULL,
          `created_at` datetime DEFAULT current_timestamp(),
          `updated_at` datetime DEFAULT current_timestamp(),
          `parent_id` int(11) DEFAULT NULL,
          PRIMARY KEY (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
        """,
        """
        CREATE TABLE IF NOT EXISTS `comments` (
            `id` int(11) NOT NULL AUTO_INCREMENT,
            `author` varchar(100) NOT NULL,
            `email` varchar(100) NOT NULL,
            `content` varchar(500) NOT NULL,
            `post_id` int(11) NOT NULL,
            `published_at` datetime NOT NULL DEFAULT current_timestamp(),
            PRIMARY KEY (`id`),
            KEY `post_id_idx` (`post_id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
        """,
        """
        CREATE TABLE IF NOT EXISTS `pages` (
          `id` int(11) NOT NULL AUTO_INCREMENT,
          `slug` varchar(50) DEFAULT NULL,
          `image` text DEFAULT NULL,
          `title` varchar(75) NOT NULL,
          `content` text DEFAULT NULL,
          `display` enum('center', 'right', '') DEFAULT 'center',
          `author_id` int(11) DEFAULT NULL,
          `created_at` datetime NOT NULL DEFAULT current_timestamp(),
          `updated_at` datetime NOT NULL DEFAULT current_timestamp(),
          `navbar_title` varchar(100) NOT NULL,
          `meta_title` varchar(100) DEFAULT NULL,
          `meta_description` varchar(200) DEFAULT NULL,
          `meta_keywords` text DEFAULT NULL,
          `meta_robots` enum('index, follow', 'noindex, follow', 'index, nofollow', 'noindex, nofollow') NOT NULL DEFAULT 'index, follow',
          `language` varchar(20) NOT NULL DEFAULT 'en',
          `redirect_url` text DEFAULT NULL,
          `parent_id` int(11) DEFAULT NULL,
          `show_in_menu` tinyint(1) NOT NULL DEFAULT 1,
          `category_id` int(11) DEFAULT NULL,
          PRIMARY KEY (`id`),
          KEY `author_id_idx` (`author_id`),
          KEY `category_id_idx` (`category_id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
        """,
        """
        CREATE TABLE IF NOT EXISTS `posts` (
          `id` int(11) NOT NULL AUTO_INCREMENT,
          `slug` varchar(150) NOT NULL,
          `title` varchar(150) NOT NULL,
          `content` text NOT NULL,
          `excerpt` text DEFAULT NULL,
          `author_id` int(11) DEFAULT NULL,
          `editor_id` int(11) DEFAULT NULL,
          `created_at` datetime NOT NULL DEFAULT current_timestamp(),
          `updated_at` datetime NOT NULL DEFAULT current_timestamp(),
          `published_at` datetime NOT NULL DEFAULT current_timestamp(),
          `status` enum('draft', 'published', 'archived', '') NOT NULL,
          `tags` text DEFAULT NULL,
          `featured_image` text DEFAULT NULL,
          `comments_enabled` tinyint(1) NOT NULL DEFAULT 1,
          `category_id` int(11) DEFAULT NULL,
          PRIMARY KEY (`id`),
          KEY `author_id_idx` (`author_id`),
          KEY `editor_id_idx` (`editor_id`),
          KEY `category_id_idx` (`category_id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
        """,
        """
        CREATE TABLE IF NOT EXISTS `users` (
          `id` int(11) NOT NULL AUTO_INCREMENT,
          `firstname` varchar(200) NOT NULL,
          `lastname` varchar(200) NOT NULL,
          `email` varchar(200) NOT NULL,
          `password_hash` text NOT NULL,
          `permissions` tinyint(1) NOT NULL,
          `profile_picture` text DEFAULT NULL,
          `description` varchar(1000) DEFAULT NULL,
          PRIMARY KEY (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
        """
    ]

    alter_constraints = [
        (
            "comments",
            "comments_ibfk_1",
            """ALTER TABLE `comments` ADD CONSTRAINT `comments_ibfk_1` FOREIGN KEY (`post_id`) REFERENCES `posts` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;"""
        ),
        (
            "pages",
            "pages_ibfk_1",
            """ALTER TABLE `pages` ADD CONSTRAINT `pages_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;"""
        ),
        (
            "pages",
            "pages_ibfk_2",
            """ALTER TABLE `pages` ADD CONSTRAINT `pages_ibfk_2` FOREIGN KEY (`author_id`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE;"""
        ),
        (
            "posts",
            "posts_ibfk_1",
            """ALTER TABLE `posts` ADD CONSTRAINT `posts_ibfk_1` FOREIGN KEY (`author_id`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE;"""
        ),
        (
            "posts",
            "posts_ibfk_2",
            """ALTER TABLE `posts` ADD CONSTRAINT `posts_ibfk_2` FOREIGN KEY (`editor_id`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE;"""
        ),
        (
            "posts",
            "posts_ibfk_3",
            """ALTER TABLE `posts` ADD CONSTRAINT `posts_ibfk_3` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;"""
        ),
    ]

    try:
        for query in create_table_queries:
            await cursor.execute(query)

        for table_name, constraint_name, query in alter_constraints:
            await cursor.execute(
                """SELECT 1 FROM information_schema.TABLE_CONSTRAINTS
                WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND CONSTRAINT_NAME = %s""",
                (table_name, constraint_name)
            )
            exists = await cursor.fetchone()
            if not exists:
                await cursor.execute(query)

        await cursor.execute("SELECT COUNT(*) FROM pages WHERE id = 1")
        row = await cursor.fetchone()
        if row and row[0] == 0:
            await cursor.execute(
                """INSERT INTO pages (id, slug, image, title, content, display, author_id, navbar_title, meta_title, meta_description, meta_keywords, meta_robots, language, redirect_url, parent_id, show_in_menu, category_id)
                VALUES (1, NULL, NULL, 'Homepage', NULL, 'center', NULL, 'Page Name', 'Homepage', 'This is the homepage, where articles are located.', 'here, provide, keywords', 'index, follow', 'en', NULL, NULL, 0, NULL)"""
            )

    except Exception as e:
        await cursor.connection.rollback()
        raise e
