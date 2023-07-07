docker build -t cartoon_filter_api .
docker run -p 8080:80 -d cartoon_filter_api