# Sanic in Practice

This project can be used as a starter for learning python api service development, the api service is developed using Sanic web framework, SQLAlchemy sql toolkit, etc. There is also an article [Python Sanic 高并发服务开发指南](https://blog.jaggerwang.net/python-sanic-high-concurrency-service-develop-tour/) for learning this project.

> To students of course: 最新的实战项目目录结构已按照 [干净架构](https://blog.jaggerwang.net/clean-architecture-in-practice/) 进行了整理，另外还使用了 [IoC 容器](https://blog.jaggerwang.net/simplify-business-objects-management-by-ioc-container/) 来简化业务对象的管理。代码结构调整较大，如想获取之前版本，可查看提交记录。

## Dependent frameworks and packages

1. [Sanic](https://github.com/huge-success/sanic) Asynchronous web framework and server
1. [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy) SQL toolkit and orm framework
1. [AIOMySQL](https://github.com/aio-libs/aiomysql) Asynchronous access mysql
1. [AIORedis](https://github.com/aio-libs/aioredis) Asynchronous access redis
1. [MarshMallow](https://github.com/marshmallow-code/marshmallow/) Object serialization
1. [Fire](https://github.com/google/python-fire) CLI application framework
1. [APScheduler](https://github.com/agronholm/apscheduler) Run interval jobs
1. [Dependency Injector](https://github.com/ets-labs/python-dependency-injector) Dependency injection microframework for Python

## APIs

| Path  | Method | Description |
| ------------- | ------------- | ------------- |
| /user/register | POST | Register |
| /user/login | POST | Login |
| /user/logout | GET | Logout |
| /user/logged | GET | Get logged user |
| /user/modify | POST | Modify logged user |
| /user/info | GET | Get user info |
| /user/follow | POST | Follow user |
| /user/unfollow | POST | Unfollow user |
| /user/following | GET | Following users of someone |
| /user/follower | GET | Fans of some user |
| /user/sendMobileVerifyCode | POST | Send mobile verify code |
| /post/publish | POST | Publish post |
| /post/delete | POST | Delete post |
| /post/info | GET | Get post info |
| /post/published | GET | Get published posts of some user |
| /post/like | POST | Like post |
| /post/unlike | POST | Unlike post |
| /post/liked | GET | Liked posts of some user |
| /post/following | GET | Posts of following users of someone |
| /file/upload | POST | Upload file |
| /file/info | GET | Get file meta info |
| /message/ws | Websocket | Create websocket connection for message |

## How to run

This project need python v3.7+.

### By local environment

#### Prapare python virtual environment

```bash
git clone https://github.com/jaggerwang/sanic-in-practice.git && cd sanic-in-practice
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

You can quit the virtual environment by execute command `deactivate`.

#### Prepare mysql and redis service

Install mysql and redis server, and start them. After mysql started, create a database for this project, and a user to access this database.

```sql
CREATE DATABASE `sip`;
CREATE USER 'sip'@'%' IDENTIFIED BY '123456';
GRANT ALL PRIVILEGES ON `sip`.* TO 'sip'@'%';
```

#### Configure application

Change configs in `weiguan/config/base.py` as your need, especially mysql, redis and path related configs. You can also change configs by environment variables, you need add `WG_` prefix to each config you want to change.

#### Create tables

```bash
python -u -m weiguan.cli.app model create-tables
```

#### Start server and scheduler

```bash
python -u -m weiguan.api.app
```

```bash
python -u -m weiguan.cli.app schedule run
```

The api service's endpoint is `http://localhost:8000/`.

### By docker compose

You need install [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) at first.

#### Configure compose

Change the content of `docker-compose.yml` as your need, especially the host path of mounted volumes.

#### Start all services

```bash
docker-compose up -d
```

It will start server, scheduler, mysql and redis services. If you need to stop and remove all services, you can execute command `docker-compose down`. The container port `8000` is mapping to the same port on local host, so the endpoint of api service is same as the local way.

When first start mysql, it will auto create a database `sip` and a user `sip` with password `123446` to access this database. The password of `root` user is also `123456`.

#### Create tables

Login to server container and create tables as previous.

```bash
docker container exec -it sanic-in-practice_server_1 bash
python -u -m weiguan.cli.app model create-tables
```

### Developing in vscode's remote container

This project support developing in [VSCode](https://code.visualstudio.com/)'s remote container, you can create your own development environment in just one click. You need install vscode and it's extension "Remote - Containers" at first.

#### Configure remote container

Configure `docker-compose.dev.yml` and `.devcontainer/devcontainer.json` as your need, especially the host path of mount volumes. The file `docker-compose.dev.yml` will override some configs of the base file `docker-compose.yml` for better developing experience. Such as auto build application image, mount local project folder into container, etc. It also mount host's `~/.ssh` folder into container for executing git command in container.

#### Open project in remote container

Click remote development button at bottom-left corner of vscode, or open command palette, then execute command `Remote-Containers: Reopen Folder in Container`. It'll build application image, and start a server container, including it's dependency containers, as this project's development environment.

The workspace folder of the remote project is at `/workspace`, which mounted the local project's folder. You can now run and restart the remote project as nomal local project. If you need execute some command, you can login to the server container or use `docker container exec`.

The left steps is the same as run application by docker compose, such as create database and tables, access apis, etc.
