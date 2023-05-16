from locust import HttpUser, task, between
from locust.env import Environment
from locust.stats import stats_printer, stats_history
from locust.log import setup_logging
import gevent
import random

class WebsiteUser(HttpUser):
    wait_time = between(1, 2.5)

    @task
    def load_test(self):
        random_number = random.randint(1, 100)
        response = self.client.get(f"/count/{random_number}")
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.text}")

if __name__ == "__main__":
    # Set your variables here
    number_of_users = 100000 # total number of concurrent users that will be simulated in the load test
    spawn_rate = 1000 # rate at which users are spawned per second
    duration_in_seconds = 300 # total duration for which the load test will run

    setup_logging("INFO", None)
    env = Environment(user_classes=[WebsiteUser])

    # Set the target host to the URL of your service
    env.host = "http://localhost:80"

    # Start a WebUI instance
    env.create_local_runner()

    # Start a greenlet that saves current stats to history
    gevent.spawn(stats_history, env.runner.stats)

    # Start a greenlet that print current stats
    gevent.spawn(stats_printer, env.runner.stats)

    # Start the test
    env.runner.start(number_of_users, spawn_rate=spawn_rate)

    # after a certain duration stop the runner
    gevent.spawn_later(duration_in_seconds, lambda: env.runner.quit())

    # Wait for the greenlets
    env.runner.greenlet.join()
