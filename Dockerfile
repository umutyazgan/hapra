FROM tiangolo/uwsgi-nginx-flask:python3.6
ENV CONFIG_FILE /etc/hapra.cfg
COPY . /app
COPY ./hapra.cfg /etc
ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["supervisord"]
