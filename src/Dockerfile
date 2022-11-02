from almalinux
RUN mkdir /app
workdir /app
copy webhook.py /app/app.py
RUN yum install python3 python3-jsonpatch python3-flask -y && pip3 install gunicorn pyyaml kubernetes
#entrypoint tail -f /dev/null
ENTRYPOINT ["/usr/local/bin/gunicorn"]
CMD ["app:app"]
