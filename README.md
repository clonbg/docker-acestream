# Docker Ace Stream server
An [Ace Stream](http://www.acestream.org/) server Docker image & Python3 client to stream.
- [Overview](#overview)
- [Building](#building)
- [Usage](#usage)
- [Reference](#reference)

## Overview
What this provides:
- Dockerized Ace Stream server (version `3.1.35`) running under Ubuntu 18.04.
- Bash script to start server and present HTTP API endpoint to host.
- Python playback script [`playstream.py`](playstream.py) instructing server to:
	- Commence streaming of a given content ID.
	- ...and optionally start a compatible media player (such as [iina(OS X only)](https://iina.io/)) to view stream.

Since a single HTTP endpoint exposed from the Docker container controls the server _and_ provides the output stream, this provides one of the easier methods for playback of Ace Streams on traditionally unsupported operating systems such as OS X.

## Building
To build Docker image:
```sh
$ ./build.sh
```

## Usage
Start the server via:
```sh
$ ./run.sh
```

Server will now be available from `http://127.0.0.1:6878`:
```sh
$ curl http://127.0.0.1:6878/webui/api/service?method=get_version&format=jsonp&callback=
# {"result": {"code": 3013500, "platform": "linux", "version": "3.1.35"}, "error": null}
```

A program ID can be started with [`playstream.py`](playstream.py):
```sh
$ ./playstream.py --help
usage: playstream.py [-h] --content-id HASH [--player PLAYER]
                      [--server HOSTNAME] [--port PORT] [--multi-players] [-d]

Instructs server to commence a given content ID. Will execute a local media
player once playback has started.

optional arguments:
  -h, --help         show this help message and exit
  --content-id HASH  content ID to stream
  --player PLAYER    media player to execute once stream active
  --server HOSTNAME  server hostname, defaults to 127.0.0.1
  --port PORT        server HTTP API port, defaults to 6878
  --multi-players    play stream in multiple players mode, defaults to False
  -d, --debug        run client in debug mode
```

For example, to stream `CONTENT_ID` and send playback to `iina` when ready:
```sh
$ ./playstream.py \
	--content-id CONTENT_ID \
	--player /usr/bin/vlc \

INFO 2019-05-12 18:45:52,190 playstream.py 47       Client starts.
INFO 2019-05-12 18:45:52,202 playstream.py 91       acestream engine version: 3.1.35
INFO 2019-05-12 18:45:52,202 playstream.py 93       acestream engine version code: 3013500
INFO 2019-05-12 18:45:52,202 playstream.py 188      Acestream server is available
Status:  | Peers:   0 | Down:    0KB/s | Up:    0KB/s
Status: prebuf | Peers:   0 | Down:    0KB/s | Up:    0KB/s
Status: prebuf | Peers:   4 | Down:   24KB/s | Up:    0KB/s
Status: prebuf | Peers:   4 | Down:  540KB/s | Up:    0KB/s
Status: dl | Peers:   4 | Down:  887KB/s | Up:    0KB/s
Status: dl | Peers:   4 | Down:  957KB/s | Up:    0KB/s
Status: dl | Peers:   4 | Down:  887KB/s | Up:    0KB/s
Status: dl | Peers:   4 | Down:  870KB/s | Up:    1KB/s
Status: dl | Peers:   4 | Down:  828KB/s | Up:    2KB/s
INFO 2019-05-10 19:31:23,590 playstream3.py 57       Client exit.
```

Send <kbd>Ctrl + C</kbd> to exit.

## Reference
- [Ace Stream Wiki (English)](http://wiki.acestream.org/wiki/index.php/%D0%97%D0%B0%D0%B3%D0%BB%D0%B0%D0%B2%D0%BD%D0%B0%D1%8F_%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D0%B0/en).
- Binary downloads: http://wiki.acestream.org/wiki/index.php/Download.
- Ubuntu install notes: http://wiki.acestream.org/wiki/index.php/Install_Ubuntu.
- HTTP API usage: http://wiki.acestream.org/wiki/index.php/Engine_HTTP_API.
- `playstream.py` routines inspired by: https://github.com/magnetikonline/docker-acestream-server.
