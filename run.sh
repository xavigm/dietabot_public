docker stop dietabot
docker rm dietabot
git pull
docker build . -t dietabot
docker run -d --restart unless-stopped --name dietabot -v /opt/dietabot/static:/usr/src/app/static dietabot
