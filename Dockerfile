# =================== BUILDER IMAGE ======================
FROM ubuntu:16.04 as stf_builder
# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    default-jdk \
    file \
    git \
    make \
    unzip
# Download Android SDK and NDK
ENV SDK /root/android-sdk
RUN mkdir /root/.android \
    && touch ~/.android/repositories.cfg \
    && mkdir $SDK \
    && curl -o $SDK/ndk.zip https://dl.google.com/android/repository/android-ndk-r15-linux-x86_64.zip \
    && unzip $SDK/ndk.zip -d $SDK
ENV PATH $SDK/android-ndk-r15:$PATH
# Download and Build OpenSTF minicap 
ENV OPENSTF /root/openstf
RUN mkdir $OPENSTF \
    && cd $OPENSTF \
    && git clone https://github.com/openstf/minicap \
    && cd minicap \
    && git submodule init \
    && git submodule update \
    && ndk-build
# Download and Build OpenSTF minitouch 
RUN cd $OPENSTF \
    && git clone https://github.com/openstf/minitouch.git \
    && cd minitouch \
    && git submodule init \
    && git submodule update \
    && ndk-build
# Download Android Platform Tools
RUN curl -o /root/platform-tools.zip https://dl.google.com/android/repository/platform-tools-latest-linux.zip \
    && unzip /root/platform-tools.zip -d /root/ 


# ===================== MAIN IMAGE =======================
FROM ubuntu:16.04
VOLUME /srv
COPY --from=stf_builder /root/openstf /root/sdk/openstf
COPY --from=stf_builder /root/platform-tools /root/platform-tools
COPY requirements.txt /root/
ENV PATH /root/platform-tools:$PATH
RUN apt-get update && apt-get install -y \
       python-software-properties \
       software-properties-common \
    && add-apt-repository ppa:jonathonf/python-3.6 \
    && apt-get update && apt-get install -y \
       python3.6 \
       python3.6-dev \
       python3-pip \
       python3.6-venv
RUN python3.6 -m pip install --upgrade pip \
    && python3.6 -m pip install -r /root/requirements.txt
WORKDIR /srv
CMD ./run.sh