FROM python:3.10-bullseye

# need to install cv2 dependencies at system level when using pip
RUN apt-get update \
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    ffmpeg \ 
    libsm6 \ 
    libxext6 \ 
    && apt-get clean autoremove --yes

COPY src/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt && rm -f /tmp/requirements.txt

ARG username=kedro
ARG uid=1000
ARG gid=100
ENV USER $username
ENV UID $uid
ENV GID $gid
ENV HOME /home/$USER

RUN adduser --disabled-password \
    --gecos "Non-root user" \
    --uid $UID \
    --gid $GID \
    --home $HOME \
    $USER

WORKDIR $HOME
COPY . .
RUN chown -R $USER:${GID} $HOME

USER $USER
RUN chmod -R a+w $HOME

EXPOSE 8888

CMD ["python", "./run.py"]