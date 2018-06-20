FROM alpine:3.7

RUN apk add --no-cache python socat

ADD flag /cpushop/flag
ADD cpushop.py /cpushop/cpushop.py

EXPOSE 43000

ENTRYPOINT ["socat", "tcp-l:43000,crlf,fork", "system:'python2.7 /cpushop/cpushop.py'" ]
