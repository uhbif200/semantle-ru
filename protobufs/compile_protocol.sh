#!/bin/bash
DIR=$(dirname "$0")

#Компилируем
python -m grpc_tools.protoc -I $DIR/ --python_out=$DIR/../ --grpc_python_out=$DIR/../ $DIR/semantleru.proto