from applications.timed_task import run_timed_task
from init import app
from setting import F_PORT, F_HOST, F_DEBUG_STATUS


if __name__ == '__main__':
    run_timed_task(app)
    app.run(port=F_PORT, host=F_HOST, debug=F_DEBUG_STATUS)
