#!/usr/bin/env python3
"""
post_to_threads.py — One-shot script to post text and/or media to Meta Threads.

Usage:
    python post_to_threads.py "Hello from X!" --image /path/to/photo.jpg
    python post_to_threads.py "Check this out" --video /path/to/clip.mp4
    python post_to_threads.py "Text only post"

Requires a .env file with THREADS_USERNAME and THREADS_PASSWORD.
"""

import argparse
import os
import sys
import time
import logging

from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def configure_threads():
    """Apply optional proxy/timeout settings from env vars."""
    from metathreads import config

    proxy_http = os.getenv("THREADS_PROXY_HTTP")
    proxy_https = os.getenv("THREADS_PROXY_HTTPS")
    if proxy_http or proxy_https:
        config.PROXY = {}
        if proxy_http:
            config.PROXY["http"] = proxy_http
        if proxy_https:
            config.PROXY["https"] = proxy_https
        logger.info("Threads proxy configured.")

    timeout = os.getenv("THREADS_TIMEOUT")
    if timeout:
        config.TIMEOUT = int(timeout)
        logger.info("Threads timeout set to %s seconds.", timeout)


def login_threads():
    """Authenticate to Threads and return the client instance."""
    from metathreads import MetaThreads

    username = os.getenv("THREADS_USERNAME")
    password = os.getenv("THREADS_PASSWORD")

    if not username or not password:
        logger.error("THREADS_USERNAME and THREADS_PASSWORD must be set in .env")
        sys.exit(1)

    threads = MetaThreads()
    logger.info("Logging in to Threads as '%s'...", username)
    threads.login(username, password)
    logger.info("Logged in successfully. User: %s", threads.me.get("username", "unknown"))
    return threads


def post_thread(threads, caption: str, image_path: str = None, video_path: str = None):
    """
    Post a thread to Threads.

    Args:
        threads:    Authenticated MetaThreads client.
        caption:    Text content of the post.
        image_path: Optional path to an image file.
        video_path: Optional path to a video file.

    Returns:
        API response from MetaThreads.
    """
    kwargs = {"thread_caption": caption}

    if image_path:
        if not os.path.isfile(image_path):
            logger.error("Image file not found: %s", image_path)
            sys.exit(1)
        kwargs["image_path"] = image_path
        logger.info("Attaching image: %s", image_path)

    if video_path:
        if not os.path.isfile(video_path):
            logger.error("Video file not found: %s", video_path)
            sys.exit(1)
        kwargs["video_path"] = video_path
        logger.info("Attaching video: %s", video_path)

    logger.info("Posting thread...")
    result = threads.post_thread(**kwargs)
    logger.info("Thread posted successfully!")
    return result


def main():
    parser = argparse.ArgumentParser(description="Post to Meta Threads from the command line.")
    parser.add_argument("caption", help="Text caption for the thread post.")
    parser.add_argument("--image", dest="image_path", default=None, help="Path to an image file.")
    parser.add_argument("--video", dest="video_path", default=None, help="Path to a video file.")
    args = parser.parse_args()

    load_dotenv()
    configure_threads()
    threads = login_threads()

    result = post_thread(threads, args.caption, args.image_path, args.video_path)

    if result:
        logger.info("Post result: %s", result)
    else:
        logger.warning("Post may have failed — no result returned.")


if __name__ == "__main__":
    main()
