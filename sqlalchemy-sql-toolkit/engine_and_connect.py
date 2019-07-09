from sqlalchemy import create_engine


engine = create_engine('mysql://root:@localhost:3306/sa_test', echo=True)
