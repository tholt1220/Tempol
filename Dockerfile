FROM ubuntu:18.04


RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev

RUN apt-get install -y libsndfile1
RUN apt-get install -y ffmpeg

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install -r requirements.txt

RUN pip3 install python-dotenv

COPY . /app

EXPOSE 5000 
ENV S3_ACCESS_KEY AKIAJI77O3D4A3FYOHFQ
ENV S3_BUCKET_NAME elasticbeanstalk-us-west-1-064202757067
ENV S3_SECRET_ACCESS_KEY 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

ENTRYPOINT [ "python3" ]

CMD [ "-u", "application.py" ]