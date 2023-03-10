#!/bin/sh
mkdir -p models/
wget -nc https://grammarly-nlp-data-public.s3.amazonaws.com/gector/roberta_1_gector.th -P models/
wget -nc https://grammarly-nlp-data-public.s3.amazonaws.com/gector/xlnet_0_gector.th -P models/
