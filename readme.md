# Quran Speech Recognizer



This application will listen to the user's Quran recitation, and take the 
user to the position of the Quran from where the s/he had recited.

# Methodology
We used transfer learning to make our application. We fine tuned the pretrained
model available at https://huggingface.co/elgeish/wav2vec2-large-xlsr-53-arabic
using the data available at https://www.kaggle.com/c/quran-asr-challenge/data.
Our model can be found at https://huggingface.co/Nuwaisir/Quran_speech_recognizer.

# Usage

Automatic Quran Speech recognizer

Hit the Record Button and Recite a verse

You can search from the last para or the whole Sura

It will take you the part of quran from where you are reciting
