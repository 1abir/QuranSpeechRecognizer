from os import path
from unicodedata import name
import sounddevice as sd
from transformers import Wav2Vec2ForCTC,Wav2Vec2Processor
from lang_trans.arabic import buckwalter
from nltk import edit_distance
from tqdm import tqdm
import pyquran as q
import torch



def load_models():
    global loaded_model, loaded_processor
    loaded_model = Wav2Vec2ForCTC.from_pretrained("Nuwaisir/Quran_speech_recognizer").eval()
    loaded_processor = Wav2Vec2Processor.from_pretrained("Nuwaisir/Quran_speech_recognizer")

    return loaded_model, loaded_processor

def record(fs = 16000, seconds = 5):
    #fs = 16000  # Sample rate
    #seconds = 5  # Duration of recording
    print("recording...")
    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
    sd.wait()  # Wait until recording is finished
    print("finished recording")
    return fs , myrecording[:,0]

def predict(single):
    inputs = loaded_processor(single["speech"], sampling_rate=16000, return_tensors="pt", padding=True)
    with torch.no_grad():
        predicted = torch.argmax(loaded_model(inputs.input_values).logits, dim=-1)
    predicted[predicted == -100] = loaded_processor.tokenizer.pad_token_id  # see fine-tuning script
    pred_1 = loaded_processor.tokenizer.batch_decode(predicted)[0]
    single["predicted"] = buckwalter.untrans(pred_1)
    return single



def last_para_str(taskeel=False):
    quran_string = ''
    for i in range (78, 115):
        quran_string += ' '.join(q.quran.get_sura(i, with_tashkeel=taskeel,basmalah=False))
        quran_string += ' '
    return quran_string

def whole_quran_str(taskeel=False):
    quran_string = ''
    for i in range (1, 115):
        quran_string += ' '.join(q.quran.get_sura(i, with_tashkeel=taskeel,basmalah=False))
        quran_string += ' '
    return quran_string

def find_match_2(q_str,s,spaces,threshhold = 10):
  len_q = len(q_str)
  len_s = len(s)
  min_dist = 1000000000

  min_dist_pos = []

  for i in tqdm(spaces):
    j = i+1
    k = j + len_s + len_s // 3
    if k > len_q:
      break
    dist = edit_distance(q_str[j:k],s)
    if dist < min_dist:
      min_dist = dist
      min_dist_pos = [j]
    elif dist == min_dist:
      min_dist_pos.append(j)

  return min_dist, min_dist_pos

def find_all_index(s, ch):
    return [i for i, ltr in enumerate(s) if ltr == ch]

def load_last_para():
    global last_para,last_para_spaces
    last_para = last_para_str()
    last_para_spaces = find_all_index(last_para,' ')
    last_para_spaces.insert(0,-1)

def load_all_paras():
    global all_para,all_para_spaces
    all_para = whole_quran_str()
    all_para_spaces = find_all_index(all_para,' ')
    all_para_spaces.insert(0,-1)

def pipeline_last_para():

    fs, myrecording = record()

    single_example = {
        "speech": myrecording,
        "sampling_rate": fs,
    }

    predicted = predict(single_example)

    print(predicted["predicted"])

    return predicted["predicted"]
    

def pipeline_whole_quran():

    fs, myrecording = record()

    single_example = {
        "speech": myrecording,
        "sampling_rate": fs,
    }

    predicted = predict(single_example)

    print(predicted["predicted"])

    return predicted["predicted"]

def quran_finder(predicted,whole_quran=False):
    if whole_quran == False:
        dist,poses = find_match_2(last_para,q.strip_tashkeel(predicted),spaces=last_para_spaces)
        print("distance:",dist)
        matches = []
        for i in poses:
            print(last_para[i:i+200],'\n')
            matches.append(last_para[i:i+200])
        return matches, dist
    else:
        dist,poses = find_match_2(all_para,q.strip_tashkeel(predicted),spaces=all_para_spaces)
        print("distance:",dist)
        matches = []
        for i in poses:
            print(last_para[i:i+200],'\n')
            matches.append(last_para[i:i+200])

        return matches , dist

def load(callback,*args):
    print("loading models...Please wait")
    load_models()
    load_last_para()
    load_all_paras()
    print("loaded")
    callback()

if __name__ == "__main__":
    load_models()
    load_last_para()
    load_all_paras()
    pipeline_last_para()