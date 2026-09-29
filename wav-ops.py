
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
        header_chunk_size = int.from_bytes(file_header[4:8], byteorder='little', signed=False)
        wave_chunk_id = file_header[8:12].decode('ascii')
        format_chunk_id = file_header[12:16].decode('ascii')
        format_chunk_size = int.from_bytes(file_header[16:20], byteorder='little', signed=False)
        format_tag =  int.from_bytes(file_header[20:22], byteorder='little', signed=False)
        num_channels = int.from_bytes(file_header[22:24], byteorder='little', signed=False)
        num_samples_sec = int.from_bytes(file_header[24:28], byteorder='little', signed=False)
        byte_rate = int.from_bytes(file_header[28:32], byteorder='little', signed=False)
        block_align = int.from_bytes(file_header[32:34], byteorder='little', signed=False)
        bits_per_sample = int.from_bytes(file_header[34:36], byteorder='little', signed=False)
        data_chunk_id = file_header[36:40].decode('ascii')

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
            data_chunk_size = int.from_bytes(file_bytes[40:44], byteorder='little', signed=False)

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

def fp_to_data_byte(float_point, bits_per_sample:int):

    data = bytearray()

    if bits_per_sample == 8:
        for sample in float_point:
            sample = max(-1.0, min(1.0, sample))
            value = round((sample + 1.0) * 127.5)
            value = max(0, min(255, value))
            data.append(int(value))
    else:
        value_range = 2 ** (bits_per_sample - 1)
        min_value = -value_range
        max_value = value_range - 1
        bytes_per_sample = bits_per_sample // 8
        for sample in float_point:
            sample = max(-1.0, min(1.0, sample))
            value = round(sample * value_range)
            value = max(min_value, min(max_value, value))
            value = int(value)
            data.extend(value.to_bytes(bytes_per_sample, byteorder='little', signed=True))

    return data

def wav_file_write(data, info: dict, new_bit_sample: int=8 ,filename='output.wav'):

    if info.get("bits_per_sample") != new_bit_sample:
        # Calculate new values in case the bit_per_sample changes these
        bytes_per_sample = new_bit_sample // 8
        block_align = info.get("num_channels") * bytes_per_sample
        byte_rate = info.get("num_samples_sec") * block_align
        audio_data = fp_to_data_byte(data, new_bit_sample)
        data_size = len(audio_data)

        # Calculate new header chunk in case this changes
        len_wave_chunk_id = len(info.get("wave_chunk_id").encode('utf-8'))
        len_format_chunk_id = len(info.get("format_chunk_id").encode('utf-8'))
        len_chunk_size_bytes = 4
        len_data_chunk_id = len(info.get("data_chunk_id").encode('utf-8'))
        len_chunk_size_bytes = 4
        header_chunk_size = len_wave_chunk_id + \
                + len_wave_chunk_id \
                + len_format_chunk_id \
                + info.get("format_chunk_size") \
                + len_data_chunk_id\
                + len_chunk_size_bytes\
                + data_size

        info.update({
            "byte_rate": byte_rate,
            "block_align": block_align,
            "bits_per_sample": new_bit_sample,
            "data_chunk_size": data_size
        })
    else:
        audio_data = fp_to_data_byte(data, new_bit_sample)
        data_size = info.get("data_chunk_size")

    # This function assumes no additional meta. Recalculate in case
    # meta was lost
    len_wave_chunk_id = len(info.get("wave_chunk_id").encode('utf-8'))
    len_format_chunk_id = len(info.get("format_chunk_id").encode('utf-8'))
    len_chunk_size_bytes = 4
    len_data_chunk_id = len(info.get("data_chunk_id").encode('utf-8'))
    len_data_size_bytes = 4
    header_chunk_size = len_wave_chunk_id + \
            + len_wave_chunk_id \
            + len_format_chunk_id \
            + info.get("format_chunk_size") \
            + len_data_chunk_id\
            + len_data_size_bytes\
            + data_size

    info["header_chunk_size"] = header_chunk_size

    # Construct WAV Header
    header = bytearray()
    header.extend(info.get("header_chunk_id").encode('ascii') )
    header.extend(info.get("header_chunk_size").to_bytes(len_chunk_size_bytes, byteorder='little'))
    header.extend(info.get("wave_chunk_id").encode('ascii') )

    # Format Sub-chunk
    header.extend(info.get("format_chunk_id").encode('ascii') )
    header.extend(info.get("format_chunk_size").to_bytes(len_chunk_size_bytes, byteorder='little'))  # Sub-chunk 1 size (16 for PCM)
    header.extend(info.get("format_tag").to_bytes(2, byteorder='little'))   # Audio format (1 for PCM)
    header.extend(info.get("num_channels").to_bytes(2, byteorder='little'))
    header.extend(info.get("num_samples_sec").to_bytes(4, byteorder='little'))
    header.extend(info.get("byte_rate").to_bytes(4, byteorder='little'))
    header.extend(info.get("block_align").to_bytes(2, byteorder='little'))
    header.extend(info.get("bits_per_sample").to_bytes(2, byteorder='little'))

    # Data Sub-chunk
    header.extend(info.get("data_chunk_id").encode('ascii') )
    header.extend(info.get("data_chunk_size").to_bytes(4, byteorder='little'))

    # Write to disk
    with open(filename, 'wb') as f:
        f.write(header + audio_data)

if __name__ == "__main__":
    try:
        file_dict, audio_data = wav_file_open("signal.wav")
        print(file_dict)
        fp = data_bytes_to_fp(audio_data, file_dict.get("bits_per_sample"))
        print("Generating output.wav with 16 bit width")
        wav_file_write(fp, file_dict, new_bit_sample=16)
    except FileNotFoundError:
        print("No valid .wav file found. Exiting....")
