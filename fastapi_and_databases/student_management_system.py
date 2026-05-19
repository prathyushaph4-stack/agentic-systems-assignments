from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, select, insert, update, delete

engine = create_engine("mysql+pymysql://root:password@localhost/student_db")

connection = engine.connect()
metadata = MetaData()
#mysql+pymysql://root:password@localhost/student_db
students = Table(
    "students",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50), nullable=False),
    Column("age", Integer),
    Column("city", String(50))
)

metadata.create_all(engine)
insert_query = insert(students).values([
    {"name": "Rahul", "age": 22, "city": "Mumbai"},
    {"name": "Priya", "age": 19, "city": "Delhi"},
    {"name": "Amit", "age": 23, "city": "Pune"}
])

connection.execute(insert_query)
connection.commit()

select_query = select(students)

result = connection.execute(select_query)

for row in result:
    print(row)