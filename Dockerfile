# use an official GDAL image as the base image
# https://github.com/OSGeo/gdal/tree/master/docker#ubuntu-based
FROM ghcr.io/osgeo/gdal:ubuntu-small-latest

# install pip
RUN apt-get update && apt-get -y install python3-pip --fix-missing

WORKDIR /
ENV PYTHONUNBUFFERED=0
ENV PYTHONPATH=/demeter

COPY requirements.txt /

RUN mkdir /scratch && \
    chmod og+rw /

RUN pip install --no-cache-dir -r /requirements.txt

COPY demeter /demeter

ENTRYPOINT ["python", "-m", "demeter"]
