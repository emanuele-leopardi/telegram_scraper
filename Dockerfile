FROM python

COPY config.yaml *.session scraper.py /opt/
RUN pip3 install pyyaml telethon \
	&& chmod +x /opt/scraper.py

WORKDIR /opt

ENTRYPOINT ["python3", "scraper.py"]