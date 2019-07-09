from sqlalchemy.sql import select, desc, union, union_all, func, and_

from define_and_create import engine, metadata, users, addresses


if __name__ == '__main__':
    conn = engine.connect()

    s = select([users.c.name]).order_by(users.c.name)
    print(s)

    s = select([users.c.name]).order_by(users.c.name.desc())
    print(s)

    s = select([users.c.name, addresses.c.email_address]).\
        select_from(users.join(addresses)).\
        limit(1).offset(1)
    print(conn.execute(s).fetchall())

    s = select([users.c.name, func.count(addresses.c.id)]).\
        select_from(users.join(addresses)).\
        group_by(users.c.name)
    print(conn.execute(s).fetchall())

    s = select([users.c.name, func.count(addresses.c.id)]).\
        select_from(users.join(addresses)).\
        group_by(users.c.name).\
        having(func.length(users.c.name) > 4)
    print(conn.execute(s).fetchall())

    s = select([users.c.name]).\
        where(addresses.c.email_address.contains(users.c.name)).\
        distinct()
    print(conn.execute(s).fetchall())

    print(users.join(addresses))

    print(users.join(
        addresses,
        addresses.c.email_address.like(users.c.name + '%')
    ))

    s = select([users.c.fullname]).select_from(
        users.join(addresses,
                   addresses.c.email_address.like(users.c.name + '%'))
    )
    print(conn.execute(s).fetchall())

    s = select([users, addresses]).select_from(
        users.outerjoin(addresses,
                        and_(
                            addresses.c.email_address.like('jack' + '%'),
                            addresses.c.user_id == users.c.id
                        ))
    )
    print(conn.execute(s).fetchall())

    s = select([func.count(addresses.c.id)]).\
        where(users.c.id == addresses.c.user_id).\
        as_scalar()
    print(conn.execute(select([users.c.name, s])).fetchall())

    s = select([func.count(addresses.c.id)]).\
        where(users.c.id == addresses.c.user_id).\
        label("address_count")
    print(conn.execute(select([users.c.name, s])).fetchall())

    s = select([addresses.c.user_id]).\
        where(addresses.c.user_id == users.c.id).\
        where(addresses.c.email_address == 'jack@yahoo.com')
    enclosing_s = select([users.c.name]).where(users.c.id == s)
    print(conn.execute(enclosing_s).fetchall())

    s = select([users.c.id]).\
        where(users.c.id == addresses.c.user_id).\
        where(users.c.name == 'jack').\
        correlate(addresses)
    enclosing_s = select(
        [users.c.name, addresses.c.email_address]).\
        select_from(users.join(addresses)).\
        where(users.c.id == s)
    print(conn.execute(enclosing_s).fetchall())

    s = select([users.c.id]).\
        where(users.c.id == addresses.c.user_id).\
        where(users.c.name == 'jack').\
        correlate_except(users)
    enclosing_s = select(
        [users.c.name, addresses.c.email_address]).\
        select_from(users.join(addresses)).\
        where(users.c.id == s)
    print(conn.execute(enclosing_s).fetchall())

    s = union(
        addresses.select().
        where(addresses.c.email_address == 'foo@bar.com'),
        addresses.select().
        where(addresses.c.email_address.like('%@yahoo.com')),
    ).order_by('email_address')
    print(conn.execute(s).fetchall())

    conn.close()
