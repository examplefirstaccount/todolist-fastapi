import logging
import time

from fastapi import Request

logger = logging.getLogger("app")


async def log_requests(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    process_time = round(time.time() - start_time, 4)

    logger.info({
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "process_time": f"{process_time}s",
        "client": request.client.host,
    })

    return response
