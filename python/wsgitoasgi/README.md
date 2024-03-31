#### Deps
```bash
pip install fastapi "uvicorn[standard]" flask gunicorn asgiref icecream
```

#### Run wsgi_app.py
```bash
gunicorn wsgi_app:application
```

#### Run asgi_app.py
```bash
gunicorn asgi_app:application --worker-class uvicorn.workers.UvicornWorker
```

#### Run fastapi_and_flask_app.py
```bash
gunicorn fastapi_and_flask_app:fast_api_app --worker-class uvicorn.workers.UvicornWorker
```

#### Run fastapiapp.py
```bash
gunicorn fastapiapp:app --worker-class uvicorn.workers.UvicornWorker
```
