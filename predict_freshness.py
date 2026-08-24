from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import matplotlib.pyplot as plt
# Loading the trained model
model = load_model('/Applications/Coding/FarmPuree/freshness_model.h5')
# Function to preprocess the image
def preprocess_image(img_path):
    img = image.load_img(img_path, target_size=(150, 150))  # Resize image
    img_array = image.img_to_array(img)  # Convert to numpy array
    img_array = img_array / 255.0  # Normalize pixel values to [0, 1]
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    return img_array
# Provide the path to the image you want to predict
img_path = '/Users/rudranisarkar/Documents/data/train/fresh/16.jpg'  # Example path
# Preprocess the image
img_array = preprocess_image(img_path)
prediction = model.predict(img_array)
# Output the prediction with threshold tuning
#threshold = 0.4  #fresh
threshold = 0.6 #rotten
if prediction[0] > threshold:
    print("The fruit is Rotten!")
else:
    print("The fruit is Fresh!")
    

img = image.load_img(img_path, target_size=(150, 150))
plt.imshow(img)
plt.title(f'Prediction: {"Rotten" if prediction[0] > threshold else "Fresh"}')
plt.show()


    

