import sqlite3

import pandas as pd


def data_import(db_file, db_table, data_file):
    connections = sqlite3.connect(db_file)
    sql = f'DELETE FROM {db_table}'
    cur = connections.cursor()
    cur.execute(sql)
    connections.commit()
    import_file = pd.read_csv(data_file)
    import_file.to_sql(db_table, connections,
                       if_exists='append', index=False)
    connections.close()
    print(f'{data_file} successfully imported')


category = data_import('db.sqlite3', 'reviews_category',
                       'static/data/category.csv')
comments = data_import('db.sqlite3', 'reviews_comment',
                       'static/data/comments.csv')
genre = data_import('db.sqlite3', 'reviews_genre', 'static/data/genre.csv')
genre_title = data_import('db.sqlite3', 'reviews_title_genre',
                                  'static/data/genre_title.csv')
rewiew = data_import('db.sqlite3', 'reviews_review', 'static/data/review.csv')
titles = data_import('db.sqlite3', 'reviews_title', 'static/data/titles.csv')
users = data_import('db.sqlite3', 'reviews_user', 'static/data/users.csv')