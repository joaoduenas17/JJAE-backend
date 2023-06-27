FROM python:3.8.12

# Environment variables
ENV USER=desarrollo
ARG HOME_DIR=/home/desarrollo
ARG SHELL=/bin/bash
ARG ENTRY_DIR=/entry_folder
ARG env_name

# Create user and install packages
RUN mkdir /tmp/requirements && \
    useradd -ms ${SHELL} ${USER} && chown -R ${USER}:${USER} ${HOME_DIR}
COPY ./requirements/ /tmp/requirements/
RUN pip install -r /tmp/requirements/${env_name}.txt --upgrade

# Entrypoint
RUN mkdir ${ENTRY_DIR}
COPY docker_entrypoint.sh ${ENTRY_DIR}
RUN chmod +x ${ENTRY_DIR}/*.sh

# Add code django
ADD ./app ${HOME_DIR}

# USER ${USER}
WORKDIR ${HOME_DIR}
