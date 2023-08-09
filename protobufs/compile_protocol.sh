#!/bin/bash
DIR=$(dirname "$0")

#Компилируем
python -m grpc_tools.protoc -I $DIR/ --python_out=/tmp --grpc_python_out=/tmp $DIR/morph.proto

#Копируем в сервисы, которым это нужно
cp /tmp/morph_pb2.py $DIR/../morph_service/
cp /tmp/morph_pb2_grpc.py $DIR/../morph_service/