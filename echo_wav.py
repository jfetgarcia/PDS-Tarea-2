
import argparse
import numpy as np
import wav_ops

def apply_echo_wav(data, delay: float, amplitude: float, sample_rate: int, num_channels: int):
    data_len = len(data)

    delay_samples = int(round(delay * sample_rate))
    delay_samples = delay_samples * num_channels
    impulse = np.zeros(delay_samples + 1)
    impulse[delay_samples] = amplitude
    impulse[0] = 1.0

    echo = np.convolve(data, impulse, mode="full")

    return echo

def validate_amplitude(value: float):
    amplitude = float(value)

    if not 0.0 <= amplitude <= 1.0:
        raise argparse.ArgumentTypeError(
            "Amplitude should be between 0-1"
        )

    return amplitude

def validate_delay(value: float):
    delay = float(value)

    if delay < 0.0:
        raise argparse.ArgumentTypeError(
            "Delay should be a positive number"
        )

    return delay

def main():
    parser = argparse.ArgumentParser(
        description="Adds echo to wav file"
    )

    parser.add_argument(
        "--file",
        type=str,
        help="Input wav file"
    )

    parser.add_argument(
        "--amplitude",
        type=validate_amplitude,
        default=0.1,
        help="Relative amplitud of echo. Must be between 0-1"
    )

    parser.add_argument(
        "--delay",
        default=1,
        type=validate_delay,
        help="Delay of echo in seconds"
    )

    args = parser.parse_args()

    file_dict, data = wav_ops.wav_file_open(args.file)
    normalized_data = wav_ops.data_byte_to_fp(data, file_dict.get("bits_per_sample"))
    echo_data = apply_echo_wav(normalized_data,
                                args.delay,
                                args.amplitude,
                                file_dict.get("num_samples_sec"),
                                file_dict.get("num_channels")
                            )

    termination = ".wav"
    insert_text = "_out"
    if termination in args.file:
        insert_point = args.file.index(termination)
        out_file = args.file[:insert_point] + insert_text + args.file[insert_point:]

    wav_ops.wav_file_write(
        echo_data,
        file_dict,
        new_bit_sample=file_dict.get("bits_per_sample"),
        filename=out_file
    )

if __name__ == "__main__":
    main()
