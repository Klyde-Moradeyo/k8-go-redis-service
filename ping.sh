while true; do
  echo $(curl -s http://localhost:80/count/1)
  sleep 2
done