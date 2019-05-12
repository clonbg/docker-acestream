FROM ubuntu:18.04 as builder

ARG VERSION="3.1.35_ubuntu_18.04"
RUN apt-get update &&\
		apt-get install --no-install-recommends --yes curl && \
		apt-get clean && \
		rm --force --recursive /var/lib/apt/lists && \
		mkdir /opt/acestream && \
		curl "http://acestream.org/downloads/linux-beta/acestream_${VERSION}_x86_64.tar.gz" | \
		tar --extract --gzip -C /opt/acestream

# actual image
FROM ubuntu:18.04
LABEL maintainer="Jack Liar <zhigu1017@gmail.com>"
RUN apt-get update --yes && \
	apt-get install --no-install-recommends --yes \
	python-setuptools python-m2crypto python-apsw libpython2.7 libssl1.0.0 net-tools libxslt1.1 && \
    apt-get clean && \
    rm --force --recursive /var/lib/apt/lists
COPY --from=builder /opt/acestream /opt/acestream

EXPOSE 6878

ENV ACESTREAM_ROOT="/opt/acestream"
ENV LD_LIBRARY_PATH="${ACESTREAM_ROOT}/lib"

CMD ["/opt/acestream/acestreamengine", "--client-console"]
