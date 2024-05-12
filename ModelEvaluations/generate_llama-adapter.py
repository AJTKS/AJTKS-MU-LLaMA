import sys

sys.path.append('./imagebind_LLM')

import imagebind_LLM.ImageBind.data as data
import imagebind_LLM.llama as llama
import pandas as pd
import librosa
from tqdm import tqdm
import os
from pydub import AudioSegment
import json
from collections import defaultdict
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--model", default="../MU-LLaMA/ckpts/7B.pth", type=str,
    help="Name of or path to the trained checkpoint",
)
parser.add_argument(
    "--llama_dir", default="../MU-LLaMA/ckpts/LLaMA-2", type=str,
    help="Path to LLaMA pretrained checkpoint",
)
args = parser.parse_args()

model = llama.load(args.model, args.llama_dir)
model.eval()


def qa_bot(filename, query="Describe the music"):
    inputs = {}
    audio = data.load_and_transform_audio_data([filename], device='cuda')
    inputs['Audio'] = [audio, 1]
    results = model.generate(
        inputs,
        [llama.format_prompt(query)],
        max_gen_len=256
    )
    result = results[0].strip()
    return result


import librosa
from pydub import AudioSegment


def split_audio(audio, i):
    if len(audio) > 60000:
        audio[:60000].export("./temp_" + str(i) + ".wav", format="wav")
        return ["./temp_" + str(i) + ".wav"] + split_audio(audio[60000:], i + 1)
    if len(audio) > 10000:
        audio.export("./temp_" + str(i) + ".wav", format="wav")
        return ["./temp_" + str(i) + ".wav"]
    return []


def get_duration(filename):
    return librosa.get_duration(path=filename)


def get_split_count(duration):
    if duration > 60:
        return 1 + get_split_count(duration - 60)
    if duration > 10:
        return 1
    return 0


mtg = json.load(open("../MusicQA/MusicQA/EvalMusicQA.json"))

total = 0

for row in mtg:
    duration = get_duration(os.path.join("../MusicQA/MusicQA/audios", row["audio_name"]))
    total += get_split_count(duration) // 2

from tqdm import tqdm

llama_data = defaultdict(lambda: {})
fileset = set()
out_filename = "./results/llama-adapter_data.json"

if not os.path.exists("./results"):
    os.makedirs("./results")

if os.path.exists(out_filename):
    llama_data = defaultdict(lambda: {}, json.load(open(out_filename, 'r')))
    fileset = set(llama_data.keys())

print(f"Already Completed: {len(fileset)}")

count = 0

pbar = tqdm(total=total)

for row in mtg:
    if row["audio_name"] in fileset:
        continue
    audio = AudioSegment.from_wav(os.path.join("../MusicQA/MusicQA/audios", row["audio_name"]))
    audio_splits = split_audio(audio, 1)
    q = row["conversation"][0]["value"]
    result = []
    for j in range(0, len(audio_splits), 2):
        audio = audio_splits[j]
        result.append(qa_bot(audio, query=q))
        pbar.update(1)
    llama_data[row["audio_name"]][q] = " ".join(result)
    count += 1
    if count % 10 == 0:
        with open(out_filename, 'w') as f:
            json.dump(llama_data, f)

with open(out_filename, 'w') as f:
    json.dump(llama_data, f)
