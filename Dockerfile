FROM ubuntu:20.04

RUN \
  apt update && \
  apt install tesseract-ocr \
  &&
