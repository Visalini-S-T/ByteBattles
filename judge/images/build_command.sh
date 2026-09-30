docker build -t judge-gcc -f ./gcc/Dockerfile ./gcc
docker build -t judge-python -f ./python/Dockerfile ./python
docker build -t judge-javascript -f ./javascript/Dockerfile ./javascript
