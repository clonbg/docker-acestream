#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
# File: /playstream3.py
# Created Date: Monday April 29th 2019
# -----
# Last Modified: Sunday May 12th 2019 7:22:55 pm
'''

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import hashlib
import json
import logging
import re
import signal
import subprocess
import sys
import time
import urllib.request
from typing import Dict, Tuple


class Client(object):

    def __init__(self, server_host, server_port, multi_players=False):
        self.server_host = server_host
        self.server_port = server_port

        self.engine_version = ""
        self.engine_version_code = 0

        self.multi_players = multi_players
        self.poll_time = 2

        self.running = False

    def __enter__(self):

        def stop(sig_num, stack_frame):
            self.running = False

        self.running = True
        logging.info("Client starts.")
        signal.signal(signal.SIGINT, stop)
        return self

    def __exit__(self, exc_type=None, exc_value=None, traceback=None):
        if any([exc_type, exc_value, traceback]):
            logging.error(repr(exc_type))
            logging.error(repr(exc_value))
            logging.error(repr(traceback))
        logging.info("Client exit.")
        return True

    def _api_request(self, url: str) -> Dict:
        """Send request to acestream server and return response json dict

        Args:
            url: api url
        Returns:
            dict: response json data
        """
        response = urllib.request.urlopen(url)
        return json.loads(response.read().decode())

    def _check_server_availability(self) -> bool:
        """Check server availability before start streaming

        Returns:
            bool: wether server is avaliable
        """
        url = "http://{}:{}/webui/api/service?method=get_version&format=jsonp&callback=".format(
            self.server_host, self.server_port)
        try:
            response_dic = self._api_request(url)
        except:
            logging.exception("Check server availability failed!")
            return False
        else:
            if response_dic.get("error"):
                return False
            self.engine_version = response_dic.get("result").get("version")
            self.engine_version_code = int(
                response_dic.get("result").get("code"))

            logging.info("acestream engine version: {}".format(
                self.engine_version))
            logging.info("acestream engine version code: {}".format(
                self.engine_version_code))

            return True

    def start_streaming(self, content_id: str) -> Tuple[str, str]:
        """Start streaming content ID

        Args:
            content_id: acestream content ID
        Returns:
            playback_url: playback url for media player to stream
            stat_url: stat url for client to get stat info of acestream engine
        """
        if self.multi_players:
            # generate a player id to support multi players playing
            player_id = hashlib.sha1(content_id.encode()).hexdigest()
            url = 'http://{}:{}/ace/getstream?format=json&id={}&pid={}'.format(
                self.server_host, self.server_port, content_id, player_id)
        else:
            url = 'http://{}:{}/ace/getstream?format=json&id={}'.format(
                self.server_host, self.server_port, content_id)

        try:
            response_dic = self._api_request(url)
        except:
            logging.exception(
                "Parsing server http response failed while starting streaming!"
            )
            return "", ""
        else:
            playback_url = response_dic.get('response').get("playback_url")
            stat_url = response_dic.get('response').get("stat_url")
            return playback_url, stat_url

    def _start_media_player(self, media_player: str,
                            playback_url: str) -> bool:
        """Start media to get stream from acestream server

        Args:
            media_player: media player cli program name
            playback_url: acestream server playback url
        Return:
            bool: whether media player stared successfully
        """
        # change this if the predefined command is not suitable for your player
        cmd = [media_player, playback_url]

        try:
            process = subprocess.run(cmd)
            process.check_returncode()
        except subprocess.CalledProcessError:
            logging.exception("{} didn't exit normally!".format(media_player))
            return False
        return True

    def _monitor_stream_status(self, stat_url: str) -> None:
        """Keep monitor stream stat status

        Args:
            stat_url: acestream server stat url
        """

        def stream_stats_message(response: dict) -> str:
            return 'Status: {} | Peers: {:>3} | Down: {:>4}KB/s | Up: {:>4}KB/s'.format(
                response.get('response', {
                    'status': 0
                }).get('status', ""),
                response.get('response', {
                    'peers': 0
                }).get('peers', 0),
                response.get('response', {
                    'speed_down': 0
                }).get('speed_down', 0),
                response.get('response', {
                    'speed_up': 0
                }).get('speed_up', 0))

        while (self.running):
            print(stream_stats_message(self._api_request(stat_url)))

            time.sleep(self.poll_time)

    def run(self, content_id: str, media_player: str) -> bool:
        """A simplified api for running whole process easily

        Args:
            content_id: acestream content ID
            media_player: media player to play the stream
        Returns:
            bool: whether client run successfully
        """
        if not self._check_server_availability():
            logging.error(
                "Server is not available. Please check server status")
            return False
        logging.info("Acestream server is available")

        playback_url, stat_url = self.start_streaming(content_id)
        if not playback_url or not stat_url:
            return False
        logging.debug("Server playback url: {}".format(playback_url))
        logging.debug("Server stat url: {}".format(stat_url))

        if not self._start_media_player(media_player, playback_url):
            return False

        self._monitor_stream_status(stat_url)


DEFAULT_SERVER_HOSTNAME = '127.0.0.1'
DEFAULT_SERVER_PORT = 6878
DEFAULT_MEDIA_PLAYER = "iina"
SERVER_POLL_TIME = 2
SERVER_STATUS_STREAM_ACTIVE = 'dl'
FORMAT = '%(levelname)s %(asctime)-15s %(filename)s %(lineno)-8s %(message)s'


def parse_args() -> argparse.Namespace:
    """Parse comand line arguments

    Returns:
        argparse.Namespace: command line args
    """
    # create parser
    parser = argparse.ArgumentParser(
        description='Instructs server to commence a given content ID. '
        'Will execute a local media player once playback has started.')

    parser.add_argument(
        '--content-id',
        help='content ID to stream',
        metavar='HASH',
        required=True,
    )

    parser.add_argument(
        '--player',
        help='media player to execute once stream active',
        default=DEFAULT_MEDIA_PLAYER,
    )

    parser.add_argument(
        '--server',
        default=DEFAULT_SERVER_HOSTNAME,
        help='server hostname, defaults to %(default)s',
        metavar='HOSTNAME',
    )

    parser.add_argument(
        '--port',
        default=DEFAULT_SERVER_PORT,
        help='server HTTP API port, defaults to %(default)s',
    )

    parser.add_argument(
        '--multi-players',
        action="store_true",
        help='play stream in multiple players mode, defaults to %(default)s',
    )

    parser.add_argument(
        '-d',
        '--debug',
        action="store_true",
        help='run client in debug mode',
    )

    args = parser.parse_args()

    if not re.match(r'^[a-f0-9]{40}$', args.content_id):
        # if content id is not a valid hash, quit program
        logging.error('Invalid content ID: [{}]'.format(args.content_id))
        sys.exit(1)

    return args


if __name__ == "__main__":
    args = parse_args()

    if args.debug:
        logging.basicConfig(format=FORMAT, level=logging.DEBUG)
    else:
        logging.basicConfig(format=FORMAT, level=logging.INFO)

    with Client(args.server, args.port) as client:
        client.run(args.content_id, args.player)
