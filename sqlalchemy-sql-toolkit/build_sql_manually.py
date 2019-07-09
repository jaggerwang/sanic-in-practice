from sqlalchemy import JSON, String, Integer
from sqlalchemy.dialects import mysql
from sqlalchemy.sql import (
    select, and_, or_, not_, func, cast, type_coerce, text, bindparam, table,
    literal_column
)

from define_and_create import engine, metadata, users, addresses


if __name__ == '__main__':
    conn = engine.connect()

    a1 = addresses.alias()
    a2 = addresses.alias()
    s = select([users]).\
        where(and_(
            users.c.id == a1.c.user_id,
            users.c.id == a2.c.user_id,
            a1.c.email_address == 'jack@msn.com',
            a2.c.email_address == 'jack@yahoo.com'
        ))
    print(s)

    s = select([(users.c.fullname + ", " + addresses.c.email_address).
                label('title')])
    print(s)

    print(users.c.id == addresses.c.user_id)
    print(users.c.id == 7)
    print((users.c.id == 7).compile().params)
    print(users.c.id != 7)
    print(users.c.name == None)
    print('fred' > users.c.name)
    print(users.c.id + addresses.c.id)
    print(users.c.name + users.c.fullname)
    print(users.c.name.op('tiddlywinks')('foo'))

    s = and_(
        users.c.name.like('j%'),
        users.c.id == addresses.c.user_id,
        or_(
            addresses.c.email_address == 'wendy@aol.com',
            addresses.c.email_address == 'jack@yahoo.com'
        ),
        not_(users.c.id > 5)
    )
    print(s)

    s = users.c.name.like('j%') &\
        (users.c.id == addresses.c.user_id) &\
        ((addresses.c.email_address == 'wendy@aol.com') |
         (addresses.c.email_address == 'jack@yahoo.com')) &\
        ~(users.c.id > 5)
    print(s)

    s = select([(users.c.fullname + ", " + addresses.c.email_address).
                label('title')]).\
        where(users.c.id == addresses.c.user_id).\
        where(users.c.name.between('m', 'z')).\
        where(or_(
            addresses.c.email_address.like('%@aol.com'),
            addresses.c.email_address.like('%@msn.com')
        ))
    print(s)

    print(func.now())
    print(func.concat('x', 'y'))
    print(func.xyz_my_goofy_function())
    print(func.current_timestamp())

    s = select([func.max(addresses.c.email_address, type_=String).
                label('maxemail')])
    print(s)

    s = select([cast(users.c.id, String)])
    print(s)

    s = select([
        type_coerce(
            {'some_key': {'foo': 'bar'}}, JSON
        )['some_key']
    ])
    print(s.compile(dialect=mysql.dialect()))

    s = text(
        "SELECT CONCAT(users.fullname, ', ', addresses.email_address) AS title "
        "FROM users, addresses "
        "WHERE users.id = addresses.user_id "
        "AND users.name BETWEEN :x AND :y "
        "AND (addresses.email_address LIKE :e1 "
        "OR addresses.email_address LIKE :e2)"
    )
    print(s)
    conn.execute(s, x='m', y='z', e1='%@aol.com', e2='%@msn.com').fetchall()

    s = text("SELECT * FROM users WHERE users.name BETWEEN :x AND :y")
    s = s.bindparams(x="m", y="z")
    print(s)

    s = s.bindparams(bindparam("x", type_=String),
                     bindparam("y", type_=String))
    print(conn.execute(s, {"x": "m", "y": "z"}).fetchall())

    s = text("SELECT id, name FROM users")
    s = s.columns(id=Integer, name=String)
    print(s)

    s = text("SELECT id, name FROM users")
    s = s.columns(users.c.id, users.c.name)
    j = s.join(addresses, s.c.id == addresses.c.user_id)
    print(select([s.c.id, addresses.c.id]).
          select_from(j).where(s.c.name == 'x'))

    s = text("SELECT users.id, addresses.id, users.id, "
             "users.name, addresses.email_address AS email "
             "FROM users JOIN addresses ON users.id=addresses.user_id "
             "WHERE users.id = 1").columns(
        users.c.id,
        addresses.c.id,
        addresses.c.user_id,
        users.c.name,
        addresses.c.email_address
    )
    result = conn.execute(s)
    row = result.first()
    print(row[addresses.c.id])

    s = select([text("CONCAT(users.fullname, ', ', addresses.email_address) AS title")]).\
        where(and_(
            text("users.id = addresses.user_id"),
            text("users.name BETWEEN 'm' AND 'z'"),
            text(
                "(addresses.email_address LIKE :x "
                "OR addresses.email_address LIKE :y)"
            )
        )).\
        select_from(text('users, addresses'))
    print(conn.execute(s, x='%@aol.com', y='%@msn.com').fetchall())

    s = select([(literal_column("users.fullname", String) +
                 ', ' +
                 literal_column("addresses.email_address")).label("title")
                ]).\
        where(and_(
            literal_column("users.id") == literal_column("addresses.user_id"),
            text("users.name BETWEEN 'm' AND 'z'"),
            text(
                "(addresses.email_address LIKE :x OR "
                "addresses.email_address LIKE :y)"
            )
        )).\
        select_from(table('users')).select_from(table('addresses'))
    print(conn.execute(s, x='%@aol.com', y='%@msn.com').fetchall())

    conn.close()
