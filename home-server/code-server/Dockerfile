FROM lscr.io/linuxserver/code-server:latest

# install java and docker
RUN apt update && apt install -y default-jdk nodejs npm
RUN npm install -g yarn

# install docker
RUN curl -fsSL https://get.docker.com -o get-docker.sh
RUN sh get-docker.sh

# install docker-compose




# copy extensisons 
COPY extensions /extensions

# install extensions
RUN for i in /extensions/*.vsix; do /app/code-server/lib/vscode/bin/remote-cli/code-server --install-extension $i; done

# remove extensions
RUN rm -rf /extensions





