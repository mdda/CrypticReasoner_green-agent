#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"


# See https://github.com/mdda/cryptic-crossword-reasoning-verifier 
#   for more details of the data being set up here


# This downloads the cryptic crossword dataset required to run the benchmark
CRYPTONITE_DIR="$SCRIPT_DIR/cryptonite"
if [ -d "$CRYPTONITE_DIR" ]; then
    echo "cryptonite already exists at $CRYPTONITE_DIR"
    echo "To re-download, remove the directory first: rm -rf $CRYPTONITE_DIR\n"
else
    wget --no-verbose 'https://github.com/aviaefrat/cryptonite/blob/main/data/cryptonite-official-split.zip?raw=true'
    unzip 'cryptonite-official-split.zip?raw=true' -d $CRYPTONITE_DIR
    rm 'cryptonite-official-split.zip?raw=true'
fi


# This downloads a dictionary of 'crossword words' - used to build the embedding-based lookup tool
DICTIONARY_FILE="$SCRIPT_DIR/UKACD.txt"
if [ -f "$DICTIONARY_FILE" ]; then
    echo "dictionary already exists at $DICTIONARY_FILE"
    echo "To re-download, remove the file first: rm -f $DICTIONARY_FILE\n"
else
    #wget https://cfajohnson.com/wordfinder/UKACD17.tgz  # No longer available...
    #tar -xzf ./UKACD17.tgz UKACD17.TXT
    wget --no-verbose https://www.quinapalus.com/UKACD17.txt.gz  # https://www.quinapalus.com/qxwdownload.html
    gunzip UKACD17.txt.gz
    mv UKACD17.txt $DICTIONARY_FILE
fi

# This downloads and then resizes the fasttext embedding library for the embedding-based lookup tool
EMBEDDINGS_FILE="$SCRIPT_DIR/cc.en.100.bin"
if [ -f "$EMBEDDINGS_FILE" ]; then
    echo "resized embeddings file already exists at $EMBEDDINGS_FILE"
    echo "To re-download, remove the file first: rm -f $EMBEDDINGS_FILE\n"
else
    # Original method that downloaded a huge file and reduced it in size
    #uv run setup-resize-embeddings.py
    #rm -f cc.en.300.bin  # This 7B file can be regenerated...

    # https://huggingface.co/docs/huggingface_hub/guides/download
    uv run hf download mdda-rdai/fasttext-cc.en.100.bin cc.en.100.bin.gz --local-dir=. --cache-dir=.
    gunzip cc.en.100.bin.gz
fi
# The embeddings will be built when the dictionary is first used


# This downloads cryptic-crossword utilities (we're interested in solver/corpora.py)
CRYPTIC_REPO_DIR="$SCRIPT_DIR/cryptic-crossword-reasoning-verifier"
if [ -d "$CRYPTIC_REPO_DIR" ]; then
    echo "cryptic-crossword utilities repo already exists at $CRYPTIC_REPO_DIR"
    echo "To re-download, remove the directory first: rm -rf $CRYPTIC_REPO_DIR\n"
else
    git clone --depth 1 https://github.com/mdda/cryptic-crossword-reasoning-verifier.git $CRYPTIC_REPO_DIR
fi

ls -la

echo ""
echo "Setup complete! cryptonite data is now available at:"
echo "  $CRYPTONITE_DIR"
echo "Dictionary data is at:"
echo "  $DICTIONARY_FILE"
echo "Resized embeddings data is at:"
echo "  $EMBEDDINGS_FILE"
echo "cryptic-crossword utilities repo is at:"
echo "  $CRYPTIC_REPO_DIR"

