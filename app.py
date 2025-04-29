import typing

from piccolo.utils.pydantic import create_pydantic_model
from piccolo.engine import engine_finder
from piccolo.columns import Varchar, Float, Timestamp, Column
from piccolo.columns.column_types import TimestampNow

from blacksheep import Application, FromJSON, json, Response, Content

from blog_app.tables import Blog, BlogIn
from datetime import datetime

BlogModelIn: typing.Any = create_pydantic_model(table=BlogIn, model_name=" BlogModelIn")

BlogModelOut: typing.Any = create_pydantic_model(table=Blog, include_default_columns=True, model_name=" BlogModelIn")

BlogModelPartial: typing.Any = create_pydantic_model(
    table=Blog, model_name="BlogModelPartial", all_optional=True
)


app = Application()

app.use_cors(
    allow_methods="GET POST DELETE",
    allow_origins="https://localhost:4200",
    allow_headers="Content-Type",
    max_age=300,
)

@app.router.get("/blog")
async def blogs():
    try:
        blog = await Blog.select()
        return blog
    except:
        return Response(404, content=Content(b"text/plain", b"Not Found"))


@app.router.get("/blog/{id}")
async def blog(id: int):
    blog = await Blog.select().where(id==Blog.id)
    if not blog:
        return Response(404, content=Content(b"text/plain", b"Id not Found"))
    return blog


@app.router.post("/blog")
async def create_blog(blog_model: FromJSON[BlogModelIn]):
    try:
        blog = Blog(**blog_model.value.dict())
        await blog.save()
        return BlogModelOut(**blog.to_dict())
    except:
        return Response(400, content=Content(b"text/plain", b"Bad Request"))


@app.router.patch("blog/{id}")
async def patch_blog(
        id: int, blog_model: FromJSON[BlogModelPartial]
):
    blog = await Blog.objects().get(Blog.id == id)
    if not blog:
        return Response(404, content=Content(b"text/plain", b"Id not Found"))

    for key, value in blog_model.value.dict().items():
        if value is not None:
            setattr(blog, key, value)

    await blog.save()
    return BlogModelOut(**blog.to_dict())

@app.router.put("/blog/{id}")
async def put_blog(
    id: int, blog_model: FromJSON[BlogModelIn]
):
    blog = await Blog.objects().get(Blog.id == id)
    if not blog:
        return Response(404, content=Content(b"text/plain", b"Id Not Found"))
    for key, value in blog_model.value.dict().items():
        if value is not None:
            setattr(blog, key, value)

    # Update the datetime_of_update field to current time
    blog.datetime_of_update = datetime.now()

    await blog.save()
    return BlogModelOut(**blog.to_dict())


@app.router.delete("/blog/{id}")
async def delete_blog(id: int):
    blog = await Blog.objects().get(Blog.id == id)
    if not blog:
        return Response(404, content=Content(b"text/plain", b"Id Not Found"))
    await blog.remove()
    return json({"message":"Blog deleted"})



async def open_database_connection_pool(application):
    try:
        engine = engine_finder()
        await engine.start_connection_pool()
    except Exception:
        print("Unable to connect to the database")


async def close_database_connection_pool(application):
    try:
        engine = engine_finder()
        await engine.close_connection_pool()
    except Exception:
        print("Unable to connect to the database")


app.on_start += open_database_connection_pool
app.on_stop += close_database_connection_pool
