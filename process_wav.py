
import numpy as np
import wav_ops

file_dict, data = wav_ops.wav_file_open('signal.wav')
normalized_data = wav_ops.data_byte_to_fp(data, file_dict.get("bits_per_sample"))
impulse_data = np.load('respuesta_al_impulso.npy')
print("Applying convolution with numpy file data")
convolved_signal = np.convolve(impulse_data, normalized_data)

print("Writing wav file with convolved signal")
wav_ops.wav_file_write(convolved_signal, file_dict, new_bit_sample=file_dict.get("bits_per_sample"))
