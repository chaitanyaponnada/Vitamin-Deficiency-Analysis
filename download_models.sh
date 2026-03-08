#!/bin/bash
# Download model files from GitHub Release

set -e

REPO="chaitanyaponnada/Vitamin-Deficiency-Analysis"
RELEASE_TAG="v1.0-Models"
BASE_URL="https://github.com/${REPO}/releases/download/${RELEASE_TAG}"

echo "Downloading model files from GitHub Release ${RELEASE_TAG}..."

mkdir -p model_saved_files

MODEL_FILES=(
    "Cnn.h5"
    "EfficientNetV2L.h5"
    "InceptionResNetV2.h5"
    "InceptionV3.h5"
    "Mobilenet.h5"
    "ResNet.h5"
    "VGG16.h5"
    "Xception.h5"
    "ensemble_metadata.json"
)

for file in "${MODEL_FILES[@]}"; do
    echo "Downloading ${file}..."
    curl -L -o "model_saved_files/${file}" "${BASE_URL}/${file}" || {
        echo "Error downloading ${file}"
        exit 1
    }
done

echo "All model files downloaded successfully!"
echo "Model directory size:"
du -sh model_saved_files
echo "Model files:"
ls -lh model_saved_files/
