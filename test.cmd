docker-compose -f test-compose.yml -p ci build
docker-compose -f test-compose.yml -p ci up -d
docker logs -f ci_server_1