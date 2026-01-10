import fasttext
import fasttext.util

fasttext.util.download_model('en', if_exists='ignore')
print("Downloaded 300-D embeddings model")
ft = fasttext.load_model('cc.en.300.bin')
print(f"Current embedding dimension : {ft.get_dimension()}\n")


print(f"Reducing embedding dimension to 100-D")
fasttext.util.reduce_model(ft, 100)
print(f"Reduced embedding dimension : {ft.get_dimension()}\n")
ft.save_model('cc.en.100.bin')  # Use this in the code...

