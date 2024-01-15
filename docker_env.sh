#!/bin/sh

export JWT_SECRET_KEY=$(openssl rand -base64 32)
