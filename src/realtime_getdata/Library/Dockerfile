FROM python:3.8.11-buster
LABEL maintainer="jn@jonasneubert.com"

WORKDIR /docker_test

COPY requirements.txt requirements.txt
# Mono: 6.12

RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 3FA7E0328081BFF6A14DA29AA6A19B38D3D831EF \
  && echo "deb http://download.mono-project.com/repo/debian stretch/snapshots/6.12 main" > /etc/apt/sources.list.d/mono-official.list \
  && apt-get update \
  && apt-get install -y clang \
  && apt-get install -y mono-devel=6.12\* \
  && rm -rf /var/lib/apt/lists/* /tmp/*


# Pythonnet: 2.5.2 (from PyPI)
# Note: pycparser must be installed before pythonnet can be built

RUN pip install pip --upgrade


RUN pip3 install --no-cache-dir -r requirements.txt
COPY . .

CMD ["python", "KKTLib.py"]