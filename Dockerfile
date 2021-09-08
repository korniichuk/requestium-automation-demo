# Name: korniichuk/booking
# Description: Dockerfile for example of booking automation with Requestium Python library on https://bezkolejki.eu/suw
# Version: 0.1a1
# Owner: Ruslan Korniichuk

FROM ubuntu:18.04

MAINTAINER Ruslan Korniichuk <ruslan.korniichuk@gmail.com>

USER root

# 1. OS
# Retrieve new lists of packages
ENV OS_REFRESHED_AT 2021-09-08
RUN apt -qq update

# 2. APT
# Install wget, chromium-chromedriver, nano
ENV YUM_REFRESHED_AT 2021-09-08
RUN apt -qq update \
        && apt install -y wget chromium-chromedriver nano \
        && apt clean

# 3. PYTHON+PIP
# Install python3, python3-dev
ENV PYTHON_REFRESHED_AT 2021-09-08
RUN apt -qq update \
        && apt install -y python3 python3-dev \
        && apt clean
# Download 'get-pip.py' file to '/tmp' directory
ENV PIP_REFRESHED_AT 2021-09-08
RUN wget --directory-prefix /tmp https://bootstrap.pypa.io/get-pip.py
# Install pip
RUN python3 /tmp/get-pip.py
# Remove '/tmp/get-pip.py' file
RUN rm /tmp/get-pip.py

# 4. SECURITY
# Add new 'booking' user
RUN useradd -c "Booking Auto" -m -s /bin/bash booking

USER booking

# 5. REQUIREMENTS
# Copy local 'requirements.txt' to image
COPY requirements.txt /tmp/requirements.txt
# Install Python packages
ENV REQUIREMENTS_REFRESHED_AT 2021-09-08
RUN pip3 install --upgrade --user --requirement /tmp/requirements.txt

USER root

# Remove 'requirements.txt' file
RUN rm /tmp/requirements.txt

# 6. FILE STRUCTURE
# Create dir for Python code
RUN mkdir --parents /opt/booking/bin/booking_auto_example
RUN chown booking:booking /opt/booking/bin/booking_auto_example

# Create dir for logger
RUN mkdir /var/log/booking
RUN chown booking:booking /var/log/booking

USER booking

# Create 'awslogs' log driver symlink
RUN ln -sf /proc/1/fd/1 /var/log/booking/awslogs_log_driver_symlink

# 7. PYTHON CODE
# Copy local 'booking_auto_example.py' to image
COPY booking_auto_example.py /opt/booking/bin/booking_auto_example/booking_auto_example.py

# 8. RUN
WORKDIR /opt/booking/bin/booking_auto_example
CMD /usr/bin/python3 booking_auto_example.py --headless --no-sandbox --disable-dev-shm-usage
