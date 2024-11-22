FROM nginx:latest

COPY ./fork_recipes/nginx.conf /etc/nginx/nginx.conf
COPY ./fork_recipes/forkrecipes.nginx.conf /etc/nginx/sites-available/
RUN mkdir /etc/nginx/sites-enabled
RUN ln -s /etc/nginx/sites-available/forkrecipes.nginx.conf /etc/nginx/sites-enabled/

CMD ["nginx", "-g", "daemon off;"]
