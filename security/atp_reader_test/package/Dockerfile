FROM python:3.8.6

MAINTAINER dmrussak
RUN apt-get update && apt-get install -y apt-utils
RUN apt-get update && apt-get -y install apt-utils debconf
RUN apt-get -y install  cron gcc
RUN pip install --upgrade pip
RUN apt-get install -y vim \
        procps \
	net-tools \
	telnet


RUN pip install --upgrade pip	

RUN mkdir /opt/atp
RUN mkdir /opt/atp/src 


COPY /opt/atp/src/ /opt/atp/src/
RUN ls /opt/atp/src/

WORKDIR /opt/atp/src/

RUN python -m venv /opt/venv
RUn /opt/venv/bin/python -m pip install --upgrade pip
RUN /opt/venv/bin/pip install -r requirements.txt

#RUN pip install -r requirements.txt

#CMD /opt/venv/bin/python /opt/atp/src/main.py
RUN chmod 0755 /opt/atp/src/run.sh
CMD /opt/atp/src/run.sh