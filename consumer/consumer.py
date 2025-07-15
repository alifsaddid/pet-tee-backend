import asyncio
import json
import logging
import os
import signal
import sys
from typing import Dict, Any

import redis.asyncio as redis
import replicate
from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db.session import AsyncSessionLocal
from app.models.task import Task, TaskStatus

from datetime import datetime
from google.cloud import storage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger('task_consumer')


class RedisConsumer:
    def __init__(self):
        self.redis_client = None
        self.running = False
        self.queue_name = "generate_image_queue"
        self.shutdown_event = asyncio.Event()

    async def connect(self) -> None:
        """Establish connection to Redis server"""
        try:
            self.redis_client = redis.from_url(settings.REDIS_URL)
            await self.redis_client.ping()
            logger.info("Successfully connected to Redis")
        except redis.RedisError as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            raise

    async def process_task(self, task_id: str, session: AsyncSession) -> None:
        """Process a task based on its type and payload"""
        logger.info(f"Processing task: {task_id}")

        try:
            if not task_id:
                logger.error("Missing item_id in payload")
                return

            # Retrieve the task from database
            task: Task = await session.scalar(
                select(Task).where(Task.id == task_id)
            )
            if not task:
                logger.error(f"Task with id {task_id} not found")
                return

            # Update task status and save
            task.status = TaskStatus.IN_PROGRESS
            await session.commit()

            # Simulate task processing
            logger.info(f"Processing task {task_id}: {task.animal} with text '{task.text}'")

            output = replicate.run(
                "black-forest-labs/flux-schnell",
                input={
                    "prompt": f"Generate a high-quality, front-facing portrait of a {task.animal} of any breed or species. The animal should be looking directly at the camera with a joyful or expressive face. It must be wearing a plain white shirt that has {task.text} text on it. Optionally, the animal can also wear stylish accessories like a hat, sunglasses, or scarf. Use a minimal, soft background to keep the focus on the animal."
                }
            )

            with open(f'{task.id}.png', 'wb') as f:
                f.write(output[0].read())

            uri = await self.upload_image_to_gcs(task, f'{task.id}.png')

            # Update task as completed
            task.status = TaskStatus.DONE
            task.image_uri = uri
            await session.commit()
            logger.info(f"Task {task_id} completed successfully")

        except Exception as e:
            logger.error(f"Error processing task {task_id}: {str(e)}")
            try:
                task = await session.scalar(
                    select(Task).where(Task.id == task_id)
                )
                if task:
                    task.status = TaskStatus.ERROR
                    await session.commit()
            except Exception as commit_err:
                logger.error(f"Failed to mark task as error: {str(commit_err)}")

    async def upload_image_to_gcs(self, task: Task, local_file_path: str):
        bucket_name = "pet-tee"

        now = datetime.utcnow()
        date_path = now.strftime("%Y/%m/%d")
        full_timestamp = now.strftime("%Y%m%dT%H%M%S%f")

        gcs_blob_name = f"{date_path}/{full_timestamp}_{task.id}.png"

        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(gcs_blob_name)

        blob.upload_from_filename(local_file_path, content_type="image/png")

        logger.info(f"Uploaded to gs://{bucket_name}/{gcs_blob_name}")

        # Delete the local file after successful upload
        os.remove(local_file_path)

        return f"gs://{bucket_name}/{gcs_blob_name}"

    async def listen(self) -> None:
        """Listen for messages on the Redis queue"""
        if not self.redis_client:
            await self.connect()

        self.running = True
        logger.info(f"Starting to listen on queue: {self.queue_name}")

        while self.running and not self.shutdown_event.is_set():
            try:
                result = await self.redis_client.brpop(self.queue_name, timeout=1)

                if not result:
                    continue

                _, message = result
                logger.debug(f"Received message: {message}")

                try:
                    data = json.loads(message)

                    async with AsyncSessionLocal() as session:
                        await self.process_task(data, session)

                except json.JSONDecodeError:
                    logger.error(f"Failed to decode JSON message: {message}")
                except Exception as e:
                    logger.error(f"Error processing message: {str(e)}")

            except redis.RedisError as e:
                logger.error(f"Redis error: {str(e)}")
                await asyncio.sleep(5)
                try:
                    await self.connect()
                except:
                    pass
            except asyncio.CancelledError:
                logger.info("Consumer task cancelled")
                self.running = False
                break
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                await asyncio.sleep(1)

    async def shutdown(self) -> None:
        """Gracefully shutdown the consumer"""
        logger.info("Shutting down consumer...")
        self.running = False
        self.shutdown_event.set()

        if self.redis_client:
            await self.redis_client.close()


async def main() -> None:
    """Main entry point for the consumer"""
    consumer = RedisConsumer()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(consumer.shutdown()))

    try:
        await consumer.listen()
    except Exception as e:
        logger.error(f"Consumer failed: {str(e)}")
    finally:
        await consumer.shutdown()


if __name__ == "__main__":
    load_dotenv()

    # Inject credentials from GOOGLE_CREDENTIALS_JSON into a temp file
    if "GOOGLE_CREDENTIALS_JSON" in os.environ:
        creds_path = "/tmp/gcp-creds.json"
        with open(creds_path, "w") as f:
            f.write(os.environ["GOOGLE_CREDENTIALS_JSON"])
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Consumer stopped by keyboard interrupt")
    except Exception as e:
        logger.error(f"Consumer failed with error: {str(e)}")
        sys.exit(1)
