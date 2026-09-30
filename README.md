# PDS-Tarea-2
Files in this repository
| File | Tooltip |
| --- | --- |
| environment.yml | file to create conda enviroment |
| output.wav | Example output file of process_wav.py |
| signal.wav | Testing wav file |
| respuesta_al_impulso.npy | Testing numpy file for convolving  |
| README.md | This file with details repository documentation |
| wav_ops.py | File with wav processing functions |
| echo_wav.py | Script to add echo to wav file |
| process_wav.py | Script of convolving signals |

## Dependencies 
For a reproducible enviroment Conda Miniforge was used. For Linux Ubuntu, the following command was used:
```
curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
bash Miniforge3-$(uname)-$(uname -m).sh
```

## Running scripts
1.  Run the enviroment script to setup dependencies necessary for both scripts
```
conda env create -f environment.yml
conda activate pds-tarea2
```
2. Running scripts example
```
python3 echo_wav.py
```
3. Exit enviroment
```
conda deactivate
```

### Script: wav_ops.py
Run the script with
```
python3 wav_ops.py
```

Has functions for the following wav file operations:

| Options | Tooltip | Input | Output |
| --- | --- | --- | --- |
| wav_file_open | Open wav file | file: str | wav metadata dictionary, sound data in byte array |
| wav_file_write | Write wav file | data: bytes, wav metadata dictionary, new_bit_sample: int , filename: str | Output wav file |
| get_wav_sample_freq | Get wav file sample frequency | filename string or wav metadata dictionary  | File sample frequency in int |
| get_wav_duration | Get wav file duration in seconds | filename string or wav metadata dictionary | Wav duration in seconds |
| get_wav_num_channels | Get number of channels in the file | filename string or wav metadata dictionary | Wav number of channels |
| data_byte_to_fp | Convert data bytes to normalized floating point | Data byte array, bits_per_sample:int | Floating point sound data in list. Normalized to [-1,1] range |
| fp_to_data_byte | Convert normalized floating point to data bytes | float point data list, bits_per_sample:int| Sound data byte array |


### Script: process_wav.py
Run the script with
```
python3 process_wav.py
```

The script expects the `signal.wav` file and `respuesta_al_impulso.npy` files to be present.
The script will execute a convolve of both signals and create `output.wav`. The original version
of this file is already present for example of expected output.

### Script: echo_wav
Run the script with
```
python3 echo_wav.py --file signal.wav --amplitude 1.0 --delay 5.0
```
| Options | Tooltip | Example |
| --- | --- | --- |
| file | Input wav file | signal.wav |
| amplitude | Relative amplitude for echo | 1.0 |
| delay | Delay in seconds for the echo | 5.0|

Echo is applied independently of bits per sample and number of channels. A new file is created with the '_out' termination.

## Troubleshooting
When installing the conda enviroment. The base enviroment might not activate. This can
result in the `conda` commands not being recognized. This can be fixed by running the
conda binary as follows:
```
<PATH TO MINIFORGE INSTALL>/miniforge3/bin/conda init
```
The terminal should show `(base)` at the start of the line if the conda base
enviroment was succesfully enabled.
