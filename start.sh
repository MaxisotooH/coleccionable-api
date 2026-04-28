#!/bin/bash
# Script de inicio para Render
uvicorn coleccionable_API.main:app --host 0.0.0.0 --port $PORT
