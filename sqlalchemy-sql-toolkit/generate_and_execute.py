from sqlalchemy.sql import select

from define_and_create import engine, metadata, users, addresses


if __name__ == '__main__':
    conn = engine.connect()

    stmt = select([addresses.c.email_address]).\
        where(addresses.c.user_id == users.c.id).\
        limit(1)
    print(users.update().values(fullname=stmt))

    stmt = users.update().\
        values(name='ed wood').\
        where(users.c.id == addresses.c.id).\
        where(addresses.c.email_address.startswith('ed%'))
    print(stmt)

    stmt = users.update().\
        values({
            users.c.fullname: 'fullname: ' + users.c.fullname,
            users.c.name: 'name: ' + users.c.fullname,
        })
    print(stmt)

    stmt = users.update(preserve_parameter_order=True).\
        values([
            (users.c.fullname, 'fullname: ' + users.c.fullname),
            (users.c.name, 'name: ' + users.c.fullname),
        ])
    print(stmt)

    stmt = users.delete().\
        where(users.c.id == addresses.c.id).\
        where(addresses.c.email_address.startswith('ed%'))
    print(stmt)

    conn.close()
