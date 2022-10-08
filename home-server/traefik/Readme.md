## Add the following lines to labels section to docker-compose, this will enable traefik to detect and expose the container to the network
labels:
    traefik.enable=true
    traefik.http.routers.blog.entrypoints=web,websecure
    traefik.http.routers.blog.tls=true
    traefik.http.routers.blog.rule=Host(`blog.example.com`)