
import numpy as np

def wav_file_open(file: str):
    with open(file, 'rb') as audio_file:

        # Usual header size (can be more with metadata)
        read_pointer = 44
        
        # Seperate the header of the wav file
        file_header = audio_file.read(read_pointer)

        if file_header[:4] != b'RIFF' or file_header[8:12] != b'WAVE' or file_header[12:16] != b'fmt ':
            raise ValueError("Invalid WAV file")

        header_chunk_id = file_header[0:4].decode('ascii')
        header_chunk_size = int.from_bytes(file_header[4:7], byteorder='little', signed=False)
        wave_chunk_id = file_header[8:11].decode('ascii')
        format_chunk_id = file_header[12:15].decode('ascii')
        format_chunk_size = int.from_bytes(file_header[16:19], byteorder='little', signed=False)
        format_tag =  int.from_bytes(file_header[20:21], byteorder='little', signed=False)
        num_channels = int.from_bytes(file_header[22:23], byteorder='little', signed=False)
        num_samples_sec = int.from_bytes(file_header[24:27], byteorder='little', signed=False)
        byte_rate = int.from_bytes(file_header[28:31], byteorder='little', signed=False)
        block_align = int.from_bytes(file_header[32:33], byteorder='little', signed=False)
        bits_per_sample = int.from_bytes(file_header[34:35], byteorder='little', signed=False)
        data_chunk_id = file_header[36:39].decode('ascii')

        # The data subchunk is not always next in the subchunk list
        data_str = 'data'
        if data_chunk_id.lower() != data_str.lower():
            data_index = -1
            read_pointer += 20
            audio_file.seek(0)
            file_bytes = audio_file.read(read_pointer)
            while data_index < 0:
                data_index = file_bytes.find(b'data')
                read_pointer += 20
                audio_file.seek(0)
                file_bytes = audio_file.read(read_pointer)
            data_chunk_id = file_bytes[data_index:data_index+4].decode('ascii')
            data_chunk_size = int.from_bytes(file_bytes[data_index+4:data_index+8], byteorder='little', signed=False)
            read_pointer = data_index+8
        else:
            read_pointer = 44
            data_chunk_size = int.from_bytes(file_bytes[40:43], byteorder='little', signed=False)

        # Read the data from the file
        audio_file.seek(read_pointer)
        data = audio_file.read(data_chunk_size)

        wav_info = {
        "header_chunk_id": header_chunk_id,
        "header_chunk_size": header_chunk_size,
        "wave_chunk_id": wave_chunk_id,
        "format_chunk_id": format_chunk_id,
        "format_chunk_size": format_chunk_size,
        "format_tag": format_tag,
        "num_channels": num_channels,
        "num_samples_sec": num_samples_sec,
        "byte_rate": byte_rate,
        "block_align": block_align,
        "bits_per_sample": bits_per_sample,
        "data_chunk_id": data_chunk_id,
        "data_chunk_size": data_chunk_size}

        return wav_info, data

def _open_wav_file(file: str):
    if isinstance(file, str):
        try:
            info, data = wav_file_open(file)
            return info, data
        except FileNotFoundError:
            return FileNotFoundError("Specify a valid .wav file to analyze")
    else:
        raise ValueError("Set 'file' parameter as a valid .wav string")


def get_wav_sample_freq(file: str ='signal.wav', info: dict=None):
    if info == None:
        info, data = _open_wav_file(file)

    sample_freq = info.get("num_samples_sec")
    return sample_freq

def get_wav_duration(file: str ='signal.wav', info: dict=None):
    if info == None:
        info, data = _open_wav_file(file)

    data_chunk_size = info.get("data_chunk_size")
    byte_rate = info.get("byte_rate")
    duration = data_chunk_size / byte_rate

    return duration

def get_wav_num_channels(file: str ='signal.wav', info: dict=None):
    if info == None:
        info, data = _open_wav_file(file)

    num_channels = info.get("num_channels")
    return num_channels

def data_bytes_to_fp(samples, bits_per_sample:int):

    fp_samples = []

    # PCM (8 bit) is the only unsigned format
    if bits_per_sample == 8:
        # At 8 bits, silence is at 128 not 0
        zero_level = 128.0
        for byte in samples:
            fp_samples.append((byte - zero_level) / zero_level)

        return(fp_samples)

    bytes_per_sample = bits_per_sample // 8
    data_range = 2 ** (bits_per_sample - 1)

    for i in range(0, len(samples), bytes_per_sample):
        raw = samples[i:i + bytes_per_sample]

        value = int.from_bytes(raw, byteorder='little', signed=True)
        fp_samples.append(value / data_range)

    return(fp_samples)


if __name__ == "__main__":
    try:
        file_dict, audio_data = wav_file_open("signal.wav")
        print(file_dict)
        print(get_wav_sample_freq())
        print(get_wav_duration())
        print(data_bytes_to_fp(audio_data, file_dict.get("bits_per_sample")))
    except FileNotFoundError:
        print("No valid .wav file found. Exiting....")
