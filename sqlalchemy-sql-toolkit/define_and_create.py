from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey

from engine_and_connect import engine

metadata = MetaData()

users = Table(
    'users', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(20)),
    Column('fullname', String(50)),
)

addresses = Table(
    'addresses', metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', None, ForeignKey('users.id')),
    Column('email_address', String(50), nullable=False),
)

if __name__ == '__main__':
    metadata.create_all(engine)

    conn = engine.connect()

    conn.execute(users.insert(), [
        {'name': 'jack', 'fullname': 'Jack Jones'},
        {'name': 'wendy', 'fullname': 'Wendy Williams'},
    ])

    conn.execute(addresses.insert(), [
        {'user_id': 1, 'email_address': 'jack@yahoo.com'},
        {'user_id': 1, 'email_address': 'jack@msn.com'},
        {'user_id': 2, 'email_address': 'www@www.org'},
        {'user_id': 2, 'email_address': 'wendy@aol.com'},
    ])

    conn.close()
