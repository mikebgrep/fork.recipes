# Fork recipes 
<img align="right" src="assets/avatar.png" height="170px" alt="Logo">

Simple, elegant frontend Python web application that work seamlessly with the [ForkApi](https://www.github.com/mikebgrep/forkapi) to provide managment for food recipies collections.

# ⚠ Not Production ready Docker setup and Readme.md

### Futures
- Django v5.x 🐍based
- Docker image on Dockerhub 🛳
- Video or image recipes 👨‍🍳
- Save your favorite recipes 😍
- Categorize 📑 your recipes for easy managment
- Deploy on cloud ☁️ with one click
- more comming ... (ai futures)

### Application previewf
![preview](assets/preview.gif)

### Installation
I will skip in dept documentation for the application and I will include the same steps in the [forkapi docs](https://mikebgrep.github.io/forkapi/Installation/) 

#### Docker deployment method
With this `docker-compose.yml` you can deploy the app together with the backend on a local machine or Rasberry Pi.
```
TODO://
```

##### Steps
1. Download the `.env` file and  make sure all variables are populated (hint sneek peek into the official [docs](https://mikebgrep.github.io/forkapi/Installation/) page if you are not sure what a variable do 🤔)

2. Choice the right image for you host.

3. If you want ssl support you need to map the folder path to the ssl in the container to your local `pem` and `cert` files location. Is should look like in the `docker-compose.yml` file on line `ToDo`
`-YOUR_PATH/SSL_FOLDER:/forkcrecipes/ssl`

4. Last but not least run the docker compose command
``` bash
$ docker compose up
```

5. You are all set.

##### Recap
This will setup 3 Docker container on the host one is the `Nginx` webserver that comunicate with the other two container one for the BE Api `forkapi` and one for the front end `fork.recipes` application
You can access the API admin panel on `host:80/admin` or port 443 if you using ssl and the `host:80` for the fork.recipes application.
### Support
This project relies only on donations if you feel generous you can support it.

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/mikebgrep)


### License 
The application code is with [MIT license](https://opensource.org/license/MIT)